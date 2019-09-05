import requests
import json

from .constants import KafkaConstants

headers = {
    'Accept': 'application/vnd.ksql.v1+json',
    'Content-Type': 'application/vnd.ksql.v1+json'
}


def _execute_ksql_commands(command=None):
    assert command
    response = requests.post(
        KafkaConstants.KSQL_SERVER.value,
        headers=headers,
        data=json.dumps({'ksql': command})
    )
    return response


def _check_stream_create_status(stream=None):
    assert stream
    response = requests.get(f'http://localhost:8088/status/stream/{stream}/create')
    assert response.json()['status'] == 'SUCCESS'


def _create_noise_stream():
    """
    Create the base stream from the noise topic.This
    is the base of all other topics/streams/table
    """
    command = (
        f"CREATE STREAM {KafkaConstants.NOISE_STREAM.value}"
        f" WITH (kafka_topic='{KafkaConstants.KAFKA_TOPIC.value}',"
        f" value_format='{KafkaConstants.VALUE_FORMAT.value}');"
    )
    cmd = 'CREATE STREAM NOISE_STREAM WITH (KAKFA_TOPIC=\'noise\', VALUE_FORMAT=\'AVRO\');'
    response = _execute_ksql_commands(command)
    print(response.json())
    assert response.status_code == 200

    print(f'KAFKA/KSQL:: {KafkaConstants.NOISE_STREAM.value} STREAM CREATED')


def _create_location_based_steam():
    """
    Create the stream with location for elasticsearch
    """
    command = (
        f"CREATE STREAM ELASTIC_LOCATION_STREAM"
        f" AS SELECT SENSOR->SENSOR_NAME AS SENSOR_NAME,"
        f" THING->LOCATION AS LOCATION"
        f" FROM {KafkaConstants.NOISE_STREAM.value}"
        f" PARTITION BY SENSOR_NAME;"
    )
    response = _execute_ksql_commands(command)
    assert response.status_code == 200

    print(f"KAFKA/KSQL:: STREAM LOCATION BASED CREATED")


def _create_sensor_name_keyed_stream():
    """
    Create the stream with key (sensor_name). The key part is required
    if we want to save the message to database.
    """
    command = (
        f"CREATE STREAM {KafkaConstants.NOISE_STREAM_KEYED.value}"
        f" AS SELECT * FROM {KafkaConstants.NOISE_STREAM.value}"
        f" PARTITION BY sensor_name;"
    )
    command1 = (
        f"CREATE STREAM {KafkaConstants.NOISE_STREAM_KEYED.value}"
        f" AS SELECT SENSOR->SENSOR_NAME AS SENSOR_NAME,"
        f" RESULTS->LEVEL AS LEVEL,"
        f" RESULTS->BATTERY AS BATTERY,"
        f" RESULTS->POWER AS POWER,"
        f" RESULTS->OVERLOAD AS OVERLOAD,"
        f" THING->THING_NAME AS THING_NAME,"
        f" THING->LOCATION[0] AS LON,"
        f" THING->LOCATION[1] AS LAT"
        f" FROM {KafkaConstants.NOISE_STREAM.value}"
        f" PARTITION BY SENSOR_NAME;"
    )
    response = _execute_ksql_commands(command1)
    assert response.status_code == 200

    print(f"KAFKA/KSQL:: STREAM {KafkaConstants.NOISE_STREAM_KEYED.value} CREATED")


def _create_min_value_table():
    _check_stream_create_status(KafkaConstants.NOISE_STREAM_KEYED.value)
    command = (
        f"CREATE TABLE {KafkaConstants.MIN_VALUE_TABLE.value} AS"
        f" SELECT SENSOR_NAME, MIN(BATTERY) AS BATTERY FROM"
        f" NOISE_STREAM_KEYED GROUP BY sensor_name;"
    )
    response = _execute_ksql_commands(command)
    assert response.status_code == 200

    print(f"KAFKA/KSQL:: TABLE/TOPIC {KafkaConstants.MIN_VALUE_TABLE.value} CREATED")


def _create_OPEN311_topic():
    _check_stream_create_status(KafkaConstants.NOISE_STREAM.value)
    command = (
        f"CREATE STREAM {KafkaConstants.ALERT_TOPIC.value} AS"
        f" SELECT * FROM {KafkaConstants.NOISE_STREAM.value} WHERE"
        # f" SELECT * FROM {KafkaConstants.NOISE_STREAM_KEYED.value} WHERE"
        # We can't create the functioning stream from keyed_stream so use original
        f" RESULTS->LEVEL > 7.0 AND RESULTS->OVERLOAD = True;"
    )
    response = _execute_ksql_commands(command)
    assert response.status_code == 200

    print (f'KAFKA/KSQL:: {KafkaConstants.ALERT_TOPIC.value} CREATED')


def _create_loud_noise_stream():
    _check_stream_create_status(KafkaConstants.NOISE_STREAM.value)
    command = (
        f"CREATE STREAM {KafkaConstants.LOUD_NOISE_TOPIC.value}"
        f" AS SELECT SENSOR_NAME AS SENSOR_NAME,"
        f" LEVEL, BATTERY, LOCATION[0] AS LON,"
        f" LOCATION[1] AS LAT from {KafkaConstants.NOISE_STREAM.value}"
        f" WHERE level > 4.0 PARTITION BY sensor_name;"
    )
    command1 = (
        f"CREATE STREAM {KafkaConstants.LOUD_NOISE_TOPIC.value}"
        f" AS SELECT * from {KafkaConstants.NOISE_STREAM_KEYED.value}"
        f" WHERE LEVEL > 4.0;"
    )
    response = _execute_ksql_commands(command1)
    assert response.status_code == 200

    print (f'KAFKA/KSQL:: {KafkaConstants.LOUD_NOISE_TOPIC.value} STREAM CREATED')


def create_ksql_streams():
    _create_noise_stream()  # Registers a stream in ksql for noise topic.
    _create_sensor_name_keyed_stream() #  Registers a base keyed stream
    _create_loud_noise_stream()  # Registers and runs a stream for where level > theshold value also save to database.
    _create_min_value_table()
    _create_OPEN311_topic()  # Registers and runs stream where level > threshold value.
    # _create_location_based_steam()



if __name__ == '__main__':
    create_ksql_streams()
