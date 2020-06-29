from django.shortcuts import get_object_or_404
from rest_framework import serializers

from seance.models import Seance, AdvUser, Hall, Film, SeanceBase, Price, SeatCategory, Seat


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
    seat_pk = serializers.IntegerField(label='seat_pk', min_value=0)
    seance_pk = serializers.IntegerField(label='seat_pk', min_value=0)
    seance_date = serializers.DateField(label='seance_date')

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

        seance = Seance.objects.filter(pk=seance_pk)
        if not seance:
            raise serializers.ValidationError(f'There are no seance with such pk: {seance_pk}')

        if seat[0].hall_id != seance[0].seance_base.hall_id:
            raise serializers.ValidationError(f'Seat with pk: {seat_pk} is not in hall with pk: '
                                              f'{seance.seance_base.hall_id}. It\' in hall with pk: '
                                              f'{seat.hall_id}')
        if not seance.seance_base.date_starts <= seance_date <= seance.seance_base.date_ends:
            raise serializers.ValidationError(f'seance date must be between {seance.seance_base.date_starts} - '
                                              f'{seance.seance_base.date_ends}')
        return data

