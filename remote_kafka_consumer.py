from confluent_kafka import KafkaError
from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError


consumer = AvroConsumer(
    {
        'bootstrap.servers': 'kafka-1a4f1159-forumvirium-feab.aivencloud.com:12060',
        'schema.registry.url': 'https://avnadmin:xnga6baarrlsgyn6@kafka-1a4f1159-forumvirium-feab.aivencloud.com:12063',
        'security.protocol': 'SSL',
        'ssl.ca.location': './secrets/ca.pem',
        'ssl.certificate.location': './secrets/service.cert',
        'ssl.key.location': './secrets/service.key',
        'group.id': 'groupid',
        'auto.offset.reset': 'earliest'
    })

consumer.subscribe(['NOISE'])

while True:
    try:
        msg = consumer.poll(10)
    except SerializerError as e:
        print (f'ERROR {e}')

    if msg:
        print(msg.value())