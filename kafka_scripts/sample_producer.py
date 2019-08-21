import random
import time
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer

from constants import KafkaConstants

VALID_NAMES = 'ABCDEGHIJKL'

THINGS = (
    {
        'location': [25.751953, 62.238472],
        'thing_name': 'Ground Floor moniting system'
    },
    {
        'location': [22.386789, 60.452985],
        'thing_name': 'Motion sensors'
    },
    {
        'location': [23.825741, 61.495406],
        'thing_name': 'Light sensors'
    }
)

sample_data = {
    'sensor': {
        'sensor_name': 'Thermometer',
        'sensor_key': 'TMPXYZ'
    },
    'results': {
        'level': 0.0,
        'overload': False,
        'underrange': False,
        'power': False,
        'battery': 0.0,
        'wifi_strength': 0.0,
        'modem_strength': 0.0,
        'laeq1s_registers': ''
    },
    'thing': {
        'location': [62.238472, 25.751953],
        'thing_name': 'Ground Floor moniting system'
    }
}


def produce_sample_data():
    value_schema = avro.load('schema_nested_value.avsc')
    key_schema = avro.load('schema_key.avsc')
    producer = AvroProducer(
        {
            'bootstrap.servers': KafkaConstants.KAFKA_SERVER.value,
            'schema.registry.url': KafkaConstants.SCHEMA_REGISTRY_SERVER.value
        },
        default_value_schema=value_schema,
        default_key_schema=key_schema
    )
    while True:
        sensor_name = f'Sensor {random.choice(VALID_NAMES)}'
        overload = random.choice((True, False))
        sample_data['thing'] = random.choice(THINGS)
        sample_data['results']['level'] = float('{:.2f}'.format(random.uniform(1.0, 9.0)))
        sample_data['results']['overload'] = overload
        sample_data['results']['battery'] = float('{:.2f}'.format(random.uniform(1.0, 9.0)))
        sample_data['sensor']['sensor_name'] = sensor_name


        producer.produce(
            topic=KafkaConstants.KAFKA_TOPIC.value,
            value=sample_data,
            key={'sensor_name': sensor_name}
        )
        time.sleep(2)

if __name__ == "__main__":
    produce_sample_data()
