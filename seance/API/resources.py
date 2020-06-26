from rest_framework import mixins
from rest_framework import viewsets

from seance.API import serializers
from seance.models import Seance, SeanceBase, Hall, Film, AdvUser


class SeanceViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
# class SeanceViewSet(viewsets.ModelViewSet):
    queryset = Seance.objects.filter(is_active=True)
    serializer_class = serializers.SeanceModelSerializer


class SeanceBaseViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = SeanceBase.objects.all()
    serializer_class = serializers.SeanceBaseModelSerializer


class HallViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Hall.objects.all()
    serializer_class = serializers.HallModelSerializer


class FilmViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Film.objects.all()
    serializer_class = serializers.FilmModelSerializer


class AdvUserViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = AdvUser.objects.all()
    serializer_class = serializers.AdvUserModelSerializer
