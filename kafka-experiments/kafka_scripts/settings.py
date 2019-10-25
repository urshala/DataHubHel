import environs

env = environs.Env()
env.read_env()

ALERT_TOPIC = 'OPEN311'  # Topic for alert system
NOISE_STREAM = 'NOISE_STREAM'  # Stream from NOISE topic
KAFKA_TOPIC = 'NOISE'  # Base topic for noise data
VALUE_FORMAT = 'AVRO'  # Serialization format for Kafka
LOUD_NOISE_TOPIC = 'LOUDNOISE'  # Topic for loud noise data
NOISE_STREAM_KEYED = 'NOISE_STREAM_KEYED'  # sensor_name keyed noise stream
MIN_VALUE_TABLE = 'MIN_BATTERY'  # Table to store minimum battery reading

KAFKA_SERVER = env.str('KAFKA_SERVER', 'localhost:29092')
SCHEMA_REGISTRY_URL = env.str('SCHEMA_REGISTRY_URL', 'http://localhost:8081')
KSQL_URL = env.str('KSQL_URL', 'http://localhost:8088')
KAFKA_CONNECT_URL = env.str('KAFKA_CONNECT_URL',
                            'http://localhost:8083/connectors')

SINK_DATABASE_URL = env.str('SINK_DATABASE_URL',
                            'postgresql://kafka-sink-db/noisedata')

ELASTICSEARCH_URL = env.str('ELASTICSEARCH_URL', 'http://localhost:9200')
