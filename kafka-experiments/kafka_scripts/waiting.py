import asyncio
import logging
from datetime import timedelta
from typing import Awaitable, Callable

import confluent_kafka.admin
import httpx

from . import settings

LOG = logging.getLogger(__name__)


def wait_for_services(timeout: timedelta = timedelta(seconds=120)) -> None:
    loop = asyncio.new_event_loop()
    return loop.run_until_complete(_wait_for_services(timeout))


async def _wait_for_services(timeout: timedelta) -> None:
    secs = timeout.total_seconds()
    wait_all = asyncio.gather(
        wait_for_kafka(settings.KAFKA_SERVERS),
        wait_for_schema_registry(settings.SCHEMA_REGISTRY_URL),
        wait_for_ksql(settings.KSQL_URL),
        wait_for_kafka_connect(settings.KAFKA_CONNECT_URL),
        wait_for_database(settings.SINK_DATABASE_URL),
        wait_for_elasticsearch(settings.ELASTICSEARCH_URL),
    )
    try:
        await asyncio.wait_for(wait_all, timeout=secs)
    except asyncio.TimeoutError:
        LOG.error("Timeout: Services did not come up in %s seconds", secs)
        return False
    return True


async def wait_for_kafka(servers: str) -> None:
    loop = asyncio.get_event_loop()

    async def attempt_connect() -> None:
        await loop.run_in_executor(None, _connect_to_kafka, servers)

    await _try_until_ok(attempt_connect, "Kafka", servers)


def _connect_to_kafka(servers: str, timeout: float = 5.0) -> None:
    client = confluent_kafka.admin.AdminClient({"bootstrap.servers": servers})
    response = client.list_topics(timeout=timeout)
    if not response.topics:
        raise Exception("No topics found")


async def wait_for_schema_registry(url):
    await _wait_for_http_ok(url, name="Schema Registry")


async def wait_for_ksql(url):
    await _wait_for_http_ok(url, name="KSQL")


async def wait_for_kafka_connect(url):
    await _wait_for_http_ok(url, name="Kafka Connect")


async def wait_for_database(url):
    pass


async def wait_for_elasticsearch(url):
    await _wait_for_http_ok(url, name="ElasticSearch")


async def _wait_for_http_ok(url: str, *, name: str) -> None:
    async with httpx.AsyncClient() as client:
        async def attempt_get() -> None:
            response: httpx.AsyncResponse = await client.get(url)
            response.raise_for_status()

        await _try_until_ok(attempt_get, name, url)


AttemptFunc = Callable[[], Awaitable[None]]


async def _try_until_ok(
        attempt: AttemptFunc,
        name: str,
        address: str,
        interval: float = 1.0,
):
    while True:
        try:
            await attempt()
        except Exception as error:
            LOG.debug("Still waiting for %s at %s (Error: %s)",
                      name, address, error)
            await asyncio.sleep(interval)
            continue
        else:
            LOG.info("Service %s is up at %s", name, address)
            return


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    LOG.setLevel(logging.DEBUG)
    wait_for_services(timedelta(seconds=15))
