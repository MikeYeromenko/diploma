import datetime

from rest_framework import mixins, status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework.views import APIView

from seance.API import serializers
from seance.API.exceptions import DateFormatError, OrderingFormatError, DatePassedError, DateEssential
from seance.models import Seance, SeanceBase, Hall, Film, AdvUser, Price, SeatCategory, Purchase, Ticket


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

    def get(self, request, *args, **kwargs):
        basket = request.session.get('basket')
        return Response(basket)


class BasketCancelAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        serializer = serializers.BasketSerializer(data=request.data)
        if serializer.is_valid():
            basket = request.session.get('basket', {})
            key = f'{serializer.data["seat_pk"]}_{serializer.data["seance_pk"]}_{serializer.data["seance_date"]}'
            if key in basket:
                del basket[key]
                request.session['basket'] = basket
                request.session.modified = True
                return Response({'basket': basket,
                                 'detail': 'Object was removed from basket',
                                 'object': serializer.data
                                 }, status=status.HTTP_200_OK)
            return Response({
                'basket': basket,
                'detail': f'There is no such object in basket',
                'object': serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def check_basket(basket):
    """Checks, that basket was created no more than 10 minutes ago"""
    if basket:
        added = datetime.datetime.strptime(basket.get('added'), '%Y-%m-%d %H:%M:%S.%f')
        if added < (datetime.datetime.now() - datetime.timedelta(minutes=10)):
            return None
    return basket


class BasketAddAPIView(APIView):

    def get(self, request, *args, **kwargs):
        """
        Validates given data, adds it to existing or creates new basket object in session
        Basket object has 10 minutes for leaving, starting with time of its creation
        """
        serializer = serializers.BasketSerializer(data=request.data)
        if serializer.is_valid():
            basket = request.session.get('basket', None)
            basket = check_basket(basket)
            if not basket:
                basket = {'added': str(datetime.datetime.now())}
            key = f'{serializer.data["seat_pk"]}_{serializer.data["seance_pk"]}_{serializer.data["seance_date"]}'
            if key in basket:
                return Response({'data': serializer.data,
                                 'detail': 'Object with such data is already in basket'
                                 }, status=status.HTTP_201_CREATED)
            basket_item = serializer.data
            basket_item.update({'price': serializer.validated_data.get('price')})
            basket.update({key: basket_item})
            request.session['basket'] = basket
            request.session.modified = True
            return Response(basket, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PurchaseViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.PurchaseModelSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return Purchase.objects.filter(user_id=self.request.user.pk)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        money_spent = request.user.sum_money_spent
        return Response({
            'money_spent': money_spent,
            'purchases': serializer.data})

    def create(self, request, *args, **kwargs):
        """Creates purchase with tickets for it
        If some of the tickets was sold, we cancel purchase and make basket empty"""
        basket = request.session.get('basket')
        basket = check_basket(basket)
        if not basket:
            return Response({'detail': 'Empty basket. Or was created more than 10 minutes ago'},
                            status=status.HTTP_200_OK)

        # del added key from basket to get only info about future tickets in it
        if 'added' in basket:
            del basket['added']
        total_price = sum([float(basket[item]['price']) for item in basket])
        if total_price > request.user.wallet:
            Response({'detail': f'Insufficient funds. You need {total_price} hrn,'
                                f' but have only {request.user.wallet} hrn'}, status=status.HTTP_200_OK)

        purchase = Purchase.objects.create(user_id=request.user.pk)
        tickets = []
        for i, item in enumerate(basket):
            existing_tickets = Ticket.objects.filter(seance_id=basket[item]['seance_pk'],
                                                     date_seance=basket[item]['seance_date'],
                                                     seat_id=basket[item]['seat_pk'])
            if existing_tickets:
                purchase.delete()
                del request.session['basket']
                request.session.modified = True
                return Response({'detail': f'Some of the tickets you choose was already sold'},
                                status=status.HTTP_200_OK)
            tickets.append(Ticket(seance_id=basket[item]['seance_pk'], date_seance=basket[item]['seance_date'],
                                  seat_id=basket[item]['seat_pk'], purchase=purchase, price=basket[item]['price']))

        [ticket.save() for ticket in tickets]
        tickets = Ticket.objects.filter(purchase_id=purchase.id)
        tickets = serializers.TicketModelSerializer(tickets, many=True)
        del request.session['basket']
        request.session.modified = True
        return Response({'tickets': tickets.data, 'total_price': total_price},
                        status=status.HTTP_201_CREATED)
