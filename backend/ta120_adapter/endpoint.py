from rest_framework import generics, permissions, serializers
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response

from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer

from .authentication import AuthParametersSerializer, SensorKeyAuthentication, SensorUser
from .ul20 import UltraLight20Parser, UltraLight20Renderer
from .models import Sensor

class QueryParametersSerializer(serializers.Serializer):
    t = serializers.DateTimeField(
        label="time", help_text="timestamp", required=False)
    getCmd = serializers.BooleanField(  # noqa: N815
        default=True, initial=True, required=False,
        label="get_command", help_text="request for receive commands")


class SensorDataSerializer(serializers.Serializer):
    n = serializers.FloatField(
        label="level", help_text="sound pressure level")
    o = serializers.NullBooleanField(
        label="overload", help_text="overload", required=False)
    u = serializers.NullBooleanField(
        label="underrange", help_text="underrange", required=False)
    b = serializers.FloatField(
        label="battery", help_text="battery level", required=False)
    p = serializers.NullBooleanField(
        label="power", help_text="power supply status", required=False)
    w = serializers.FloatField(
        label="wifi_strength", help_text="wi-fi strength", required=False)
    m = serializers.FloatField(
        label="modem_strength", help_text="modem strength", required=False)
    s = serializers.CharField(
        label="laeq1s_registers", help_text="LAeq1s registers", required=False)


class Endpoint(generics.GenericAPIView):
    parser_classes = [
        UltraLight20Parser,
        FormParser,
        MultiPartParser,
    ]
    renderer_classes = [
        UltraLight20Renderer,
        JSONRenderer,
        BrowsableAPIRenderer,
    ]
    authentication_classes = [SensorKeyAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SensorDataSerializer

    def create_data(self, data, sensor):
        # TODO: This will be removed
        data['level'] = data.pop('n')
        data['overload'] = data.pop('o')
        data['underrange'] = data.pop('u')
        data['battery'] = data.pop('b')
        data['power'] = data.pop('p')
        data['wifi_strength'] = data.pop('w')
        data['modem_strength'] = data.pop('m')
        data['laeq1s_registers'] = data.pop('s')
        data['sensor_id'] = int(sensor.sensor_id)
        data['sensor_name'] = sensor.name

        thing = sensor.thing.thinglocations.first()

        return {
            'results': data,
            'thing': {
                # 'location': str(thing.location.location), # .wkt and .srid (ST_GeomFromText('POINT(latitude longitude)', 4326)))
                'location': 'POINT(22.29125976252256 60.48970392119742)',
                'thing_name': thing.thing.name
            },
            'sensor': {
                'sensor_name': sensor.name,
                'sensor_key': sensor.key
            }
        }

    def _get_sensor_object(self, request):
        auth_parser = AuthParametersSerializer(data=request.query_params)
        auth_parser.is_valid(raise_exception=True)
        return generics.get_object_or_404(
            Sensor,
            key=auth_parser.validated_data['k'],
            sensor_id=auth_parser.validated_data['i']
        )

    def post(self, request, format=None):
        params_parser = QueryParametersSerializer(data=request.query_params)
        params_parser.is_valid(raise_exception=True)
        params = params_parser.validated_data

        body_parser = self.get_serializer(data=request.data)
        body_parser.is_valid(raise_exception=True)
        data = body_parser.validated_data

        # TODO: Consume the sensor readings here

        # TODO: Remove the following debugging code
        print(params)
        print(data)
        assert isinstance(request.user, SensorUser)
        sensor = request.user.sensor
        print(sensor.pk, sensor.sensor_id, sensor)

        # TODO: Design how to implement sensor configuration changes
        # WIP: send the data to kafka
        value_schema = avro.load('./utils/schema_nested_value.avsc')
        key_schema = avro.load('./utils/schema_key.avsc')


        producer = AvroProducer(
            {
                'bootstrap.servers': 'kafka:9092',
                'schema.registry.url': 'http://schema-registry:8081'
            },
            default_value_schema=value_schema,
            default_key_schema=key_schema
        )
        data_to_kafka = self.create_data(data, sensor)
        producer.produce(
            topic='NOISE1',
            value=data_to_kafka,
            key={'sensor_name': data_to_kafka['sensor']['sensor_name']}
        )
        producer.flush()
        return Response()
        # if 0:
        #     return Response()
        # else:
        #     # Parameters of the sensor can be changed in the response,
        #     # e.g. something like this (to set averaging time to 30 secs):
        #     return Response({
        #         '{.sensor_id}@setConfig'.format(sensor): 't=0030',
        #     })

CREATE OR REPLACE FUNCTION my_fn() RETURNS trigger AS $$
BEGIN
    # new.location := ST_GeomFromText('POINT(23.4 45.6)');
    INSERT INTO NEW_TABLE (SERNOSR_NAME, LOCATION) VALUES (NEW.SERNSOR_NAME, ST_GeomFromText(NEW."LOCATION"));
    RETURN NEW;
END
$$ language plpgsql;


# create trigger mytrigger before insert on "LOUDNOISE" for each row execute procedure my_fn();
CREATE TRIGGER LOCATION_TRIGGER BEFORE INSERT ON "LOUDNOISE" FOR EACH ROW EXECUTE PROCEDUE my_fn();