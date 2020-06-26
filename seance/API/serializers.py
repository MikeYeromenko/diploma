from rest_framework import serializers

from seance.models import Seance, AdvUser, Hall, Film, SeanceBase


class AdvUserModelSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api:user-detail')

    class Meta:
        model = AdvUser
        fields = ('username', 'url')


class HallModelSerializer(serializers.HyperlinkedModelSerializer):
    admin = AdvUserModelSerializer()
    url = serializers.HyperlinkedIdentityField(view_name='api:hall-detail')

    class Meta:
        model = Hall
        # exclude = ('created_at', )
        fields = ('url', 'name', 'quantity_seats', 'quantity_rows', 'description', 'created_at', 'updated_at',
                  'is_active', 'admin', )


class FilmModelSerializer(serializers.HyperlinkedModelSerializer):
    admin = AdvUserModelSerializer()
    url = serializers.HyperlinkedIdentityField(view_name='api:film-detail')

    class Meta:
        model = Film
        fields = ('url', 'title', 'starring', 'director', 'duration', 'description', 'created_at', 'updated_at',
                  'is_active', 'admin', )


class SeanceBaseModelSerializer(serializers.HyperlinkedModelSerializer):
    hall = HallModelSerializer()
    film = FilmModelSerializer()
    url = serializers.HyperlinkedIdentityField(view_name='api:seance_base-detail')

    class Meta:
        model = SeanceBase
        fields = ('url', 'film', 'hall', 'date_starts', 'date_ends', 'created_at', 'updated_at')


class SeanceModelSerializer(serializers.HyperlinkedModelSerializer):
    seance_base = SeanceBaseModelSerializer()
    admin = AdvUserModelSerializer()
    url = serializers.HyperlinkedIdentityField(view_name='api:seance-detail')

    class Meta:
        model = Seance
        fields = ('url', 'time_starts', 'time_ends', 'time_hall_free', 'advertisements_duration',
                  'cleaning_duration', 'description', 'is_active', 'seance_base', 'admin')
        # depth = 1
        # fields = '__all__'
