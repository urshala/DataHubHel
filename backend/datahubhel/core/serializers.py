from rest_framework import serializers

from .models import Datastream


class DatastreamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Datastream
        fields = (
            'name',
            'sts_id',
            'description',
        )
        read_only_fields = fields
