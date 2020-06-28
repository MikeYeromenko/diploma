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
        fields = ('url', 'time_starts', 'time_ends', 'time_hall_free', 'advertisements_duration',
                  'cleaning_duration', 'description', 'is_active', 'seance_base', 'prices')
        depth = 1
        # fields = '__all__'


# class SeanceRetrieveModelSerializer(SeanceModelSerializer):


class SeatModelSerializer(serializers.ModelSerializer):
    seat_category = SeatCategoryModelSerializer()

    class Meta:
        model = Seat
        exclude = ('id', 'hall')


class SeanceDataSerializer(serializers.Serializer):
    pass


