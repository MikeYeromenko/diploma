from django.urls import reverse_lazy
from rest_framework import serializers as serial

from seance.API.serializers import AdvUserModelSerializer
from seance.models import SeatCategory


class SeatCategoryHyperSerializer(serial.HyperlinkedModelSerializer):
    admin = AdvUserModelSerializer()
    url = serial.HyperlinkedIdentityField(view_name='api_admin:seat_category-detail')

    class Meta:
        model = SeatCategory
        exclude = ('created_at', )
