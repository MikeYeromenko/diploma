import datetime

from django.core.validators import RegexValidator
from django.urls import reverse_lazy
from rest_framework import serializers as serial
from rest_framework.generics import get_object_or_404

from seance.API.serializers import AdvUserModelSerializer
from seance.models import SeatCategory, AdvUser, Price, Film, Hall, Seat, SeanceBase, Seance
from seance.utilities import HexColorField


class SeatCategoryHyperSerializer(serial.HyperlinkedModelSerializer):
    admin = AdvUserModelSerializer()
    url = serial.HyperlinkedIdentityField(view_name='api_admin:seat_category-detail')

    class Meta:
        model = SeatCategory
        exclude = ('created_at', )


class SeatCategoryCUDSerializer(serial.ModelSerializer):
    """Serializer for creation and updation of SeatCategory"""
    color = HexColorField(required=True)

    class Meta:
        model = SeatCategory
        fields = ('id', 'name', 'color')
        # read_only_fields = ('admin', )


class PriceHyperSerializer(serial.HyperlinkedModelSerializer):
    url = serial.HyperlinkedIdentityField(view_name='api_admin:price-detail')
    seat_category = SeatCategoryHyperSerializer()

    class Meta:
        model = Price
        exclude = ('created_at', 'seance')


class FilmHyperSerializer(serial.HyperlinkedModelSerializer):
    url = serial.HyperlinkedIdentityField(view_name='api_admin:film-detail')
    admin = AdvUserModelSerializer()

    class Meta:
        model = Film
        exclude = ('created_at', )


class FilmCUDSerializer(serial.ModelSerializer):

    class Meta:
        model = Film
        exclude = ('created_at', 'updated_at', 'admin')


class HallHyperSerializer(serial.HyperlinkedModelSerializer):
    url = serial.HyperlinkedIdentityField(view_name='api_admin:hall-detail')
    admin = AdvUserModelSerializer()

    class Meta:
        model = Hall
        exclude = ('created_at', )


class HallCUDSerializer(serial.ModelSerializer):

    class Meta:
        model = Hall
        exclude = ('created_at', 'updated_at', 'admin')

    def validate_is_active(self, value):
        if type(value).__name__ != 'bool':
            raise serial.ValidationError(f'is_active must be true or false')
        if value and not self.instance.validate_all_seats_created():
            raise serial.ValidationError(f'You can not set is_active "true" because not all seats for hall'
                                         f'were created')
        elif self.instance:
            if not self.instance.can_deactivate:
                raise serial.ValidationError(f'You can\'t deactivate hall, because there are related '
                                             f'Seance Base objects to it')
        return value


class SeatModelSerializer(serial.ModelSerializer):

    class Meta:
        model = Seat
        exclude = ('id', )


class CreateSeatsSerializer(serial.Serializer):
    seat_starts = serial.IntegerField(min_value=1, required=True)
    seat_ends = serial.IntegerField(min_value=1, required=True)
    hall = serial.IntegerField(min_value=0, required=True)
    row = serial.IntegerField(min_value=1, required=True)
    seat_category = serial.IntegerField(min_value=0, required=True)

    def validate_hall(self, value):
        """Validates, of given hall exists"""
        # _ = super(CreateSeatsSerializer, self).validate_hall(value)
        hall = Hall.objects.filter(id=value)
        if hall:
            if hall[0].is_active:
                raise serial.ValidationError(f'Ypu ca\'t change seats in hall with is_active=True. '
                                             f'Deactivate it first')
        else:
            raise serial.ValidationError(f'There is no hall with given id')
        return value

    def validate_seat_category(self, value):
        """Validates, of given seat_category exists"""
        # _ = super(CreateSeatsSerializer, self).validate_seat_category(value)
        s_k = SeatCategory.objects.filter(id=value)
        if not SeatCategory.objects.filter(id=value):
            raise serial.ValidationError(f'There is no seat category with given id')
        return value

    def validate(self, attrs):
        """Validates specified row is not greater then quantity_rows in hall"""
        attrs = super(CreateSeatsSerializer, self).validate(attrs)
        hall = get_object_or_404(Hall, pk=attrs.get('hall'))
        row = attrs.get('row')
        if hall.quantity_rows < row:
            raise serial.ValidationError(f'Row with {row} number doesn\'t exist in current hall')
        return attrs


class SeanceBaseHyperSerializer(serial.HyperlinkedModelSerializer):
    url = serial.HyperlinkedIdentityField(view_name='api_admin:seance_base-detail')
    film = FilmHyperSerializer()
    hall = HallHyperSerializer()

    class Meta:
        model = SeanceBase
        exclude = ('created_at', )


class SeanceBaseCUDSerializer(serial.ModelSerializer):

    class Meta:
        model = SeanceBase
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_hall(self, value):
        """Checks for hall is_active attr to be True"""
        hall = Hall.objects.filter(id=value.pk)
        if hall:
            if not hall[0].is_active:
                raise serial.ValidationError(f'Hall is_active must be True to create SeanceBase with it')
        else:
            raise serial.ValidationError(f'There is no hall with given id')
        return value

    def validate_film(self, value):
        """Checks for film to exist and its is_active attr to be True"""
        film = Film.objects.filter(id=value.pk)
        if film:
            if not film[0].is_active:
                raise serial.ValidationError(f'Film is_active must be True to create SeanceBase with it')
        else:
            raise serial.ValidationError(f'There is no film with given id')
        return value

    def validate_date_starts(self, value):
        """Check for date starts not to be set in the past"""
        if value < datetime.date.today():
            raise serial.ValidationError(f'date_starts can\'t be less, then today')
        return value

    def validate(self, attrs):
        attrs_valid = super().validate(attrs)
        date_starts = attrs_valid.get('date_starts') or self.instance.date_starts

        date_ends = attrs_valid.get('date_ends') or SeanceBase.get_date_ends(attrs_valid.get('date_starts'))

        if date_ends < date_starts:
            raise serial.ValidationError(f'date_ends can\'t be less, then date_starts')

        if attrs_valid:
            if self.instance:
                seances_base_intersections = SeanceBase.validate_seances_base_intersect(
                    date_starts=date_starts,
                    date_ends=date_ends,
                    film=attrs_valid.get('film'),
                    hall=attrs_valid.get('hall'),
                    sb_pk_exclude=self.instance.pk
                )
                if seances_base_intersections:
                    raise serial.ValidationError(f'There are intersections with other base seances: '
                                                 f'{seances_base_intersections.values()}')
                seances = self.instance.seances.all()
                tickets = [seance.get_sold_but_not_used_tickets() for seance in seances]
                if tickets:
                    raise serial.ValidationError(f'You can\'t update SeanceBase, because there are sold but not'
                                                 f'used tickets on it')
                # get_sold_but_not_used_tickets
            else:
                seances_base_intersections = SeanceBase.validate_seances_base_intersect(
                    date_starts=date_starts,
                    date_ends=date_ends,
                    film=attrs_valid.get('film'),
                    hall=attrs_valid.get('hall')
                )
                if seances_base_intersections:
                    raise serial.ValidationError(f'There are intersections with other base seances: '
                                                 f'{seances_base_intersections.values()}')
        return attrs_valid


class SeanceHyperSerializer(serial.HyperlinkedModelSerializer):
    url = serial.HyperlinkedIdentityField(view_name='api_admin:seance-detail')
    seance_base = SeanceBaseHyperSerializer()
    admin = AdvUserModelSerializer()

    class Meta:
        model = Seance
        exclude = ('created_at', )


class SeanceCUDSerializer(serial.ModelSerializer):

    class Meta:
        model = Seance
        fields = '__all__'
        read_only_fields = ('id', 'updated_at', 'created_at', 'admin', 'time_ends', 'time_hall_free', 'is_active')

    def validate(self, attrs):
        attrs_valid = super().validate(attrs)
        if attrs_valid:
            if self.instance:
                seances_intersect = self.instance.validate_seances_intersect(seance_exclude_pk=self.instance.pk)
                if seances_intersect:
                    raise serial.ValidationError(f'Can\'t update. There are intersections with seances: '
                                                 f'{seances_intersect.values()}')
                if self.instance.get_sold_but_not_used_tickets().count():
                    raise serial.ValidationError(f'Can\'t update. There are sold but not used tickets.')
            else:
                seance = Seance(time_starts=attrs_valid.get('time_starts'),
                                advertisements_duration=attrs_valid.get('advertisements_duration', None),
                                cleaning_duration=attrs_valid.get('cleaning_duration', None),
                                description=attrs_valid.get('description'),
                                seance_base=attrs_valid.get('seance_base')
                                )
                # for auto generated fields to be created
                seance.save(commit=False)
                seances_intersect = seance.validate_seances_intersect()
                if seances_intersect:
                    raise serial.ValidationError(f'Can\'t create. There are intersections with seances: '
                                                 f'{seances_intersect.values()}')
        return attrs_valid

    # def validate_seances_intersect(self, seance_exclude_pk=None):

# class ImageSerializer(serial.Serializer):
#     image = serial.ImageField()

