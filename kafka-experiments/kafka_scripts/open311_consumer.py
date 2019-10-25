import logging

from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError

from . import settings

LOG = logging.getLogger(__name__)

consumer = AvroConsumer({
    'bootstrap.servers': settings.KAFKA_SERVER,
    'schema.registry.url': settings.SCHEMA_REGISTRY_URL,
    'group.id': 'groupid'
})
consumer.subscribe([settings.ALERT_TOPIC])


def listen_open311():
    while True:
        try:
            msg = consumer.poll(10)
        except SerializerError:
            LOG.exception("Error serializing message")
            break

        if msg is None:
            continue

        if msg.error():
            LOG.error("Consumed an error: %s", msg.error())
            continue

        value = msg.value()
        LOG.info("Alert: %(sensor)s reaching %(level)s", {
            "sensor": value["SENSOR"]["SENSOR_NAME"],
            "level": value["RESULTS"]["LEVEL"],
        })

    consumer.close()


if __name__ == "__main__":
    listen_open311()
