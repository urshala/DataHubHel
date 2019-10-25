import confluent_kafka.admin
from avro.schema import Schema
from confluent_kafka.avro.cached_schema_registry_client import (
    CachedSchemaRegistryClient,
)

from . import settings


def create_topic(
        name: str,
        *,
        partitions: int = 5,
        replication_factor: int = -1,
) -> None:
    config = {"bootstrap.servers": settings.KAFKA_SERVER}
    client = confluent_kafka.admin.AdminClient(config)
    if replication_factor == -1:
        cluster_metadata = client.list_topics()
        num_brokers = len(cluster_metadata.brokers)
        replication_factor = 1 if num_brokers == 1 else 2
    futures = client.create_topics([
        confluent_kafka.admin.NewTopic(
            topic=name,
            num_partitions=partitions,
            replication_factor=replication_factor,
        )
    ])
    futures[name].result()


def register_schema(topic: str, kind: str, schema: Schema) -> None:
    assert kind in ["key", "value"]

    subject = f"{topic}-{kind}"

    schema_registry = CachedSchemaRegistryClient({
        "url": settings.SCHEMA_REGISTRY_URL,
    })
    schema_id = schema_registry.register(subject, schema)
    assert schema_id
