from rest_framework import mixins, viewsets

from API_admin import serializers as serial
from seance.models import SeatCategory


class SeatCategoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = serial.SeatCategoryHyperSerializer
    queryset = SeatCategory.objects.all()
