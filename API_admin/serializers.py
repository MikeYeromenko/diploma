from django.core.validators import RegexValidator
from django.urls import reverse_lazy
from rest_framework import serializers as serial

from seance.API.serializers import AdvUserModelSerializer
from seance.models import SeatCategory, AdvUser, Price
from seance.utilities import HexColorField


class SeatCategoryHyperSerializer(serial.HyperlinkedModelSerializer):
    admin = AdvUserModelSerializer()
    url = serial.HyperlinkedIdentityField(view_name='api_admin:seat_category-detail')

    class Meta:
        model = SeatCategory
        exclude = ('created_at', )


class SeatCategoryCUDSerializer(serial.ModelSerializer):
    """Serializer for creation and updation of SeatCategory"""
    color = HexColorField(required=True)

    class Meta:
        model = SeatCategory
        fields = ('id', 'name', 'color', 'admin')
        read_only_fields = ('admin', )


class PriceHyperSerializer(serial.HyperlinkedModelSerializer):

    class Meta:
        model = Price
        exclude = ('created_at', )
