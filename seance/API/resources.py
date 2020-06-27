import datetime

from rest_framework import mixins
from rest_framework import viewsets

from seance.API import serializers
from seance.models import Seance, SeanceBase, Hall, Film, AdvUser


class SeanceViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.SeanceModelSerializer

    def get_queryset(self):
        """
        Creates queryset depending upon the asked date and ordering params
        """
        if self.request.GET.get('days', None):
            date = datetime.date.today() + datetime.timedelta(days=1)
            # self.request.session['seance_date'] = str(datetime.date.today() + datetime.timedelta(days=1))
        else:
            date = None
            # self.request.session['seance_date'] = str(datetime.date.today())
        seances = Seance.get_active_seances_for_day(date)

        # if client selected type of ordering
        ordering_param = self.request.GET.get('ordering', None)
        if ordering_param:
            seances = Seance.order_queryset(ordering_param, seances)
        return seances


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
