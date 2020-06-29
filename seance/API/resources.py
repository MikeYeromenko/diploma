import datetime

from rest_framework import mixins, status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from seance.API import serializers
from seance.API.exceptions import DateFormatError, OrderingFormatError, DatePassedError, DateEssential
from seance.models import Seance, SeanceBase, Hall, Film, AdvUser, Price, SeatCategory


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

        # if client selected type of ordering
        if ordering:
            if ordering.endswith('/'):
                ordering = ordering[0: -1]

            if ordering not in ['', 'cheap', 'expensive', 'latest', 'closest']:
                raise OrderingFormatError()
            seances = Seance.order_queryset(ordering, seances)

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

    def retrieve(self, request, *args, **kwargs):
        """Includes into response info about all seats of the hall and info about taken seats"""
        date = self.request.GET.get('date', None)
        if date:
            date = self.get_date(date)              # convert date to datetime format from string
            if date < datetime.date.today():        # if date has passed - raise error
                raise DatePassedError()
        else:
            raise DateEssential()

        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # get all seats
        seats = instance.seance_base.hall.seats
        seats = serializers.SeatModelSerializer(seats, many=True)

        # get taken seats
        tickets = instance.tickets.filter(date_seance=date)
        seats_taken = serializers.SeatModelSerializer([ticket.seat for ticket in tickets], many=True)
        return Response({'seance': serializer.data,
                         'seats': seats.data,
                         'seats_taken': seats_taken.data
                         })


class PriceViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.PriceModelSerializer
    queryset = Price.objects.all()


class SeanceBaseViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = SeanceBase.objects.all()
    serializer_class = serializers.SeanceBaseModelSerializer


class HallViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Hall.objects.all()
    serializer_class = serializers.HallModelSerializer


class FilmViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Film.objects.all()
    serializer_class = serializers.FilmModelSerializer


class AdvUserViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = AdvUser.objects.all()
    serializer_class = serializers.AdvUserModelSerializer


class SeatCategoryViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.SeatCategoryModelSerializer
    queryset = SeatCategory.objects.all()


class BasketAPIView(APIView):

    def post(self, request, format=None):
        """
        Validates given data, adds it to existing or creates new basket object in session
        """
        serializer = serializers.BasketSerializer(data=request.data, many=True)
        if serializer.is_valid():
            basket = request.session.get('basket', {})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
