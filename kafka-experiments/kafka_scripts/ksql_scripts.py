import logging

import requests

from . import settings
from .http_response_check import check_errors

LOG = logging.getLogger(__name__)

headers = {
    'Accept': 'application/vnd.ksql.v1+json',
    'Content-Type': 'application/vnd.ksql.v1+json'
}


def create_ksql_streams():
    _create_noise_stream()
    _create_sensor_name_keyed_stream()
    _create_loud_noise_stream()
    _create_min_value_table()
    _create_open311_topic()
    _create_location_based_steam()


def _create_noise_stream():
    """
    Create the base stream from the noise topic.

    This is the base of all other topics/streams/table
    """
    if _has_stream(settings.NOISE_STREAM):
        return

    _execute_ksql_commands(
        f"CREATE STREAM {settings.NOISE_STREAM}"
        f" WITH (kafka_topic='{settings.KAFKA_TOPIC}',"
        f" value_format='{settings.VALUE_FORMAT}');")
    LOG.info('Created KSQL stream: %s', settings.NOISE_STREAM)


def _create_location_based_steam():
    """
    Create the stream with location for elasticsearch
    """
    if _has_stream('ELASTIC_LOCATION_STREAM'):
        return

    _execute_ksql_commands(
        f"CREATE STREAM ELASTIC_LOCATION_STREAM"
        f" AS SELECT SENSOR->SENSOR_NAME AS SENSOR_NAME,"
        f" THING->LOCATION AS LOCATION"
        f" FROM {settings.NOISE_STREAM}"
        f" PARTITION BY SENSOR_NAME;")
    LOG.info('Created KSQL stream: %s', 'ELASTIC_LOCATION_STREAM')


def _create_sensor_name_keyed_stream():
    """
    Create the stream with key (sensor_name).

    The key part is required if we want to save the message to database.
    """
    if _has_stream(settings.NOISE_STREAM_KEYED):
        return

    _execute_ksql_commands(
        f"CREATE STREAM {settings.NOISE_STREAM_KEYED}"
        f" AS SELECT SENSOR->SENSOR_NAME AS SENSOR_NAME,"
        f" RESULTS->LEVEL AS LEVEL,"
        f" RESULTS->BATTERY AS BATTERY,"
        f" RESULTS->POWER AS POWER,"
        f" RESULTS->OVERLOAD AS OVERLOAD,"
        f" THING->THING_NAME AS THING_NAME,"
        f" THING->LOCATION[0] AS LON,"
        f" THING->LOCATION[1] AS LAT"
        f" FROM {settings.NOISE_STREAM}"
        f" PARTITION BY SENSOR_NAME;")
    LOG.info('Created KSQL stream: %s', settings.NOISE_STREAM_KEYED)


def _create_min_value_table():
    if _has_table(settings.MIN_VALUE_TABLE):
        return

    _check_stream_create_status(settings.NOISE_STREAM_KEYED)
    _execute_ksql_commands(
        f"CREATE TABLE {settings.MIN_VALUE_TABLE} AS"
        f" SELECT SENSOR_NAME, MIN(BATTERY) AS BATTERY FROM"
        f" {settings.NOISE_STREAM_KEYED} GROUP BY sensor_name;")
    LOG.info('Created KSQL table: %s', settings.MIN_VALUE_TABLE)


def _create_open311_topic():
    """
    Create a stream that captures noise levels over 7.0.
    """
    if _has_stream(settings.ALERT_TOPIC):
        return

    _check_stream_create_status(settings.NOISE_STREAM)
    _execute_ksql_commands(
        f"CREATE STREAM {settings.ALERT_TOPIC} AS"
        f" SELECT * FROM {settings.NOISE_STREAM} WHERE"
        f" RESULTS->LEVEL > 7.0 AND RESULTS->OVERLOAD = True;")
    LOG.info('Created KSQL stream: %s', settings.ALERT_TOPIC)


def _create_loud_noise_stream():
    """
    Create a stream that captures noise levels over 4.0.
    """
    if _has_stream(settings.LOUD_NOISE_TOPIC):
        return

    _check_stream_create_status(settings.NOISE_STREAM)
    _execute_ksql_commands(
        f"CREATE STREAM {settings.LOUD_NOISE_TOPIC}"
        f" AS SELECT * from {settings.NOISE_STREAM_KEYED}"
        f" WHERE LEVEL > 4.0;")
    LOG.info('Created KSQL stream: %s', settings.LOUD_NOISE_TOPIC)


def _has_stream(name):
    return _has_object('stream', name)


def _has_table(name):
    return _has_object('table', name)


def _has_object(kind, name):
    if name in _get_names(kind):
        LOG.info(f'{kind.title()} already exists: %s', name)
        return True
    else:
        return False


def _get_names(kind):
    assert kind in ['stream', 'table']
    response = _execute_ksql_commands(f'SHOW {kind.upper()}S;')
    data = response.json()
    return [x['name'] for x in data[0][kind + 's']]


def _execute_ksql_commands(command):
    url = f'{settings.KSQL_URL}/ksql'
    data = {'ksql': command}
    response = requests.post(url, headers=headers, json=data)
    check_errors(response)
    return response


def _check_stream_create_status(stream=None):
    assert stream
    url = f'{settings.KSQL_URL}/status/stream/{stream}/create'
    response = requests.get(url)
    assert response.json()['status'] == 'SUCCESS'


if __name__ == '__main__':
    create_ksql_streams()
