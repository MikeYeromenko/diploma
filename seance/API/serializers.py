import datetime

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers

from seance.models import Seance, AdvUser, Hall, Film, SeanceBase, Price, SeatCategory, Seat, Purchase, Ticket


class AdvUserModelSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api:user-detail')

    class Meta:
        model = AdvUser
        fields = ('username', 'url')


class SeatCategoryModelSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name='api:seat_category-detail')

    class Meta:
        model = SeatCategory
        exclude = ('created_at', 'updated_at', 'admin', 'id')


class HallModelSerializer(serializers.HyperlinkedModelSerializer):
    # admin = AdvUserModelSerializer()
    url = serializers.HyperlinkedIdentityField(view_name='api:hall-detail')

    class Meta:
        model = Hall
        fields = ('url', 'name', 'quantity_seats', 'quantity_rows', 'description')


class FilmModelSerializer(serializers.HyperlinkedModelSerializer):
    # admin = AdvUserModelSerializer()
    url = serializers.HyperlinkedIdentityField(view_name='api:film-detail')

    class Meta:
        model = Film
        fields = ('url', 'title', 'starring', 'director', 'duration', 'description', 'is_active')


class SeanceBaseModelSerializer(serializers.HyperlinkedModelSerializer):
    hall = HallModelSerializer()
    film = FilmModelSerializer()
    url = serializers.HyperlinkedIdentityField(view_name='api:seance_base-detail')

    class Meta:
        model = SeanceBase
        fields = ('url', 'film', 'hall', 'date_starts', 'date_ends')


class PriceModelSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api:price-detail')
    seat_category = SeatCategoryModelSerializer()

    class Meta:
        model = Price
        exclude = ('created_at', 'updated_at', 'seance')


class SeanceModelSerializer(serializers.HyperlinkedModelSerializer):
    seance_base = SeanceBaseModelSerializer()
    # admin = AdvUserModelSerializer()
    url = serializers.HyperlinkedIdentityField(view_name='api:seance-detail')
    prices = PriceModelSerializer(many=True)

    class Meta:
        model = Seance
        fields = ('url', 'pk', 'time_starts', 'time_ends', 'time_hall_free', 'advertisements_duration',
                  'cleaning_duration', 'description', 'is_active', 'seance_base', 'prices')
        depth = 1
        # fields = '__all__'


# class SeanceRetrieveModelSerializer(SeanceModelSerializer):


class SeatModelSerializer(serializers.ModelSerializer):
    seat_category = SeatCategoryModelSerializer()

    class Meta:
        model = Seat
        exclude = ('hall', )


class BasketSerializer(serializers.Serializer):
    seat_pk = serializers.IntegerField(label='seat_pk', min_value=0, required=True)
    seance_pk = serializers.IntegerField(label='seat_pk', min_value=0, required=True)
    seance_date = serializers.DateField(label='seance_date', required=True)

    def validate(self, data):
        """
        Validates, if seat and seance with given pk's exist; seance_date is in range of seance.seance_base dates;
        seat belongs to hall, in which seance goes
        """
        seat_pk = data.get('seat_pk')
        seance_pk = data.get('seance_pk')
        seance_date = data.get('seance_date')

        seat = Seat.objects.filter(pk=seat_pk)
        if not seat:
            raise serializers.ValidationError(f'There are no seat with such pk: {seat_pk}')
        seat = seat[0]

        seance = Seance.objects.filter(pk=seance_pk)
        if not seance:
            raise serializers.ValidationError(f'There are no seance with such pk: {seance_pk}')
        seance = seance[0]

        if seat.hall_id != seance.seance_base.hall_id:
            raise serializers.ValidationError(f'Seat with pk: {seat_pk} is not in hall with pk: '
                                              f'{seance.seance_base.hall_id}. It\' in hall with pk: '
                                              f'{seat.hall_id}')

        if not seance.in_run:
            raise serializers.ValidationError(f'Seance with pk: {seance_pk} is not in run.'
                                              f'It may be not active or its dates may had passed')

        if not timezone.now().date() <= seance_date <= seance.seance_base.date_ends:
            raise serializers.ValidationError(f'seance_date must be between {timezone.now().date()} - '
                                              f'{seance.seance_base.date_ends}')

        if seance.time_starts <= timezone.now().time() and seance_date == timezone.now().date():
            raise serializers.ValidationError(f'That seance had already started at {seance.time_starts}. '
                                              f'You can\'t book ticket on it')

        tickets = Ticket.objects.filter(seance_id=seance_pk, date_seance=seance_date, seat_id=seat_pk)
        if tickets:
            raise serializers.ValidationError(f'The ticket on that seat was already sold')
        price = Price.objects.filter(seance_id=seance_pk, seat_category_id=seat.seat_category.pk)
        data.update({'price': price[0].price})
                     #    , 'date_starts': seance.seance_base.date_starts,
                     # 'time_starts': seance.time_starts})
        return data


class TicketModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        exclude = ('was_returned', 'created_at', 'purchase')


class PurchaseModelSerializer(serializers.ModelSerializer):
    tickets = TicketModelSerializer(many=True)

    class Meta:
        model = Purchase
        # exclude = ('created_at', 'was_returned', 'returned_at')
        fields = ('id', 'created_at', 'tickets', )
