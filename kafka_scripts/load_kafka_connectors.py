import os
import json
import requests
from urllib.parse import urlparse

from . import settings

SINK_CONFIGURATION_FILES = [
    './kafka_scripts/postgres_sink.json',
    './kafka_scripts/min_sink.json',
    './kafka_scripts/elastic_sink.json',
    './kafka_scripts/elastic_sink_location.json',
]




def _load_connector(file_to_load=""):
    assert file_to_load
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    with open(file_to_load) as f:
        data = json.load(f)
        data.update(_get_schema_registry_settings())
    response = requests.post(
        settings.KAFKA_CONNECT_URL,
        headers=headers,
        data=json.dumps(data)
    )
    assert response.status_code == 201

    print (f"KAFKA_CONNECT: CONNECTOR {data['name']} LOADED")


def _get_schema_registry_settings():
    result = {
        'value.converter.schema.registry.url': settings.SCHEMA_REGISTRY_URL,
    }

    parsed = urlparse(settings.SCHEMA_REGISTRY_URL)
    if parsed.username and parsed.password:
        creds = '{}:{}'.format(parsed.username, parsed.password)
        result.update({
            'key.converter.basic.auth.credentials.source': 'USER_INFO',
            'value.converter.basic.auth.credentials.source': 'USER_INFO',
            'key.converter.schema.registry.basic.auth.user.info': creds,
            'value.converter.basic.auth.user.info': creds,
        })

    return result


def load_kafka_connectors():
    for file in SINK_CONFIGURATION_FILES:
        _load_connector(file)

if __name__ == "__main__":
    load_kafka_connectors()
