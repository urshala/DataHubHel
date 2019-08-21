from enum import Enum


class KafkaConstants(Enum):
    ALERT_TOPIC = 'OPEN311'  # Topic for alert system
    NOISE_STREAM = 'NOISE_STREAM'  # Stream from NOISE topic
    KAFKA_TOPIC = 'NOISE'  # Base topic for noise data
    VALUE_FORMAT = 'AVRO'  # Serialization format for Kafka
    LOUD_NOISE_TOPIC = 'LOUDNOISE'  # Topic for loud noise data
    NOISE_STREAM_KEYED = 'NOISE_STREAM_KEYED'  # sensor_name keyed noise stream
    MIN_VALUE_TABLE = 'MIN_BATTERY'  # Table to store minimum battery reading
    KAFKA_SERVER = 'localhost:29092'
    SCHEMA_REGISTRY_SERVER = 'http://localhost:8081'
    KSQL_SERVER = 'http://localhost:8088/ksql'
    CONNECT_SERVER = 'http://localhost:8083/connectors'

