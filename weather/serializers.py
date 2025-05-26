from .models import *
from rest_framework import serializers


class CheckedCitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckedCity
        fields = [
            'city',
            'date'
        ]


class CityCounterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CityCounter
        fields = [
            'city',
            'count'
        ]
