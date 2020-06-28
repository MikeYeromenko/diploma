import datetime

from rest_framework import mixins
from rest_framework import viewsets

from seance.API import serializers
from seance.API.exceptions import DateFormatError, OrderingFormatError, DatePassedError
from seance.models import Seance, SeanceBase, Hall, Film, AdvUser


class SeanceViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.SeanceModelSerializer

    def get_queryset(self):
        """
        Creates queryset depending upon the asked date and ordering params
        """
        date = self.request.GET.get('date', None)
        ordering = self.request.GET.get('ordering', '')
        if date:
            date = self.get_date(date)              # convert date to datetime format from string
            if date < datetime.date.today():        # if date has passed - raise error
                raise DatePassedError()

        seances = Seance.get_active_seances_for_day(date)

        if ordering not in ['', 'cheap', 'expensive', 'latest', 'closest']:
            raise OrderingFormatError()

        # if client selected type of ordering
        ordering_param = self.request.GET.get('ordering', None)
        if ordering_param:
            seances = Seance.order_queryset(ordering_param, seances)
        return seances

    @staticmethod
    def get_date(date):
        """Validates, that date givven by client has correct format"""
        if date.endswith('/'):
            date = date[0: -1]              # if date ends with '/': 2020-10-10/, move out last symbol

        try:
            date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            raise DateFormatError()

        return date



# class SeanceViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
#     serializer_class = serializers.SeanceModelSerializer


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
