import logging

import requests

from . import settings

LOG = logging.getLogger(__name__)


def map_lat_lng_to_geopoints():
    """
    This is the template that needs to be in the
    elasticsearch before the indices are created.
    It basically tells the elasticsearch to treat
    the LOCATION field as geo_point and not array.
    """
    headers = {
        'Accept': 'application/json',
    }
    dynamic_template_mapping = {
            "index_patterns": "*",
            "settings": {
                "number_of_shards": 1
            },
            "mappings": {
                "dynamic_templates": [
                    {
                        "geopoint": {
                            "match": "*LOCATION",
                            "mapping": {
                                "type": "geo_point"
                            }
                        }
                    }
                ]
            }
        }
    url = f'{settings.ELASTICSEARCH_URL}/_template/geomapping'
    data = dynamic_template_mapping
    response = requests.put(url, headers=headers, json=data)
    assert response.status_code == 200
    LOG.info("Created geomapping to the ElasticSearch template")
