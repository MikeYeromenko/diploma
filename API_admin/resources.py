from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from API_admin import serializers as serial
from seance.models import SeatCategory, Price


class SeatCategoryViewSet(viewsets.ModelViewSet):
    queryset = SeatCategory.objects.all()
    permission_classes = (IsAdminUser, )

    def get_serializer_class(self):
        if self.request.method.lower() == 'get':
            return serial.SeatCategoryHyperSerializer
        else:
            return serial.SeatCategoryCUDSerializer

    def perform_create(self, serializer):
        serializer.save(admin=self.request.user)

    def perform_update(self, serializer):
        serializer.save(admin=self.request.user)


class PriceViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = serial.PriceHyperSerializer
    queryset = Price.objects.all()
