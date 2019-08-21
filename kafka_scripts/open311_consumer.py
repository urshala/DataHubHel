from confluent_kafka import KafkaError
from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError

from constants import KafkaConstants

consumer = AvroConsumer({
    'bootstrap.servers': KafkaConstants.KAFKA_SERVER.value,
    'schema.registry.url': KafkaConstants.SCHEMA_REGISTRY_SERVER.value,
    'group.id': 'groupid'
})
consumer.subscribe([KafkaConstants.ALERT_TOPIC.value])


def listen_open311():
    while True:
        try:
            msg = consumer.poll(10)
        except SerializerError as e:
            print(e)
            print('Error serializing message')
            break

        if msg is None:
            continue

        if msg.error():
            print(f'Error {msg.error()}')

        value = msg.value()
        print (f'OPEN311:: Alert {value["SENSOR"]["SENSOR_NAME"]} reaching {value["RESULTS"]["LEVEL"]}')

    consumer.close()

if __name__ == "__main__":
    listen_open311()
