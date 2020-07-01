from django.core.validators import RegexValidator
from django.urls import reverse_lazy
from rest_framework import serializers as serial
from rest_framework.generics import get_object_or_404

from seance.API.serializers import AdvUserModelSerializer
from seance.models import SeatCategory, AdvUser, Price, Film, Hall, Seat
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
        if value:
            raise serial.ValidationError(f'You can only change is_active to False. If you '
                                         f'want to set it True, please make activation of hall')
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
        _ = super(CreateSeatsSerializer, self).validate_hall(value)
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
        _ = super(CreateSeatsSerializer, self).validate_seat_category(value)
        if not Hall.objects.filter(id=value):
            raise serial.ValidationError(f'There is no hall with given id')
        return value

    def validate(self, attrs):
        """Validates specified row is not greater then quantity_rows in hall"""
        hall = get_object_or_404(Hall, pk=attrs.get('hall'))
        row = attrs.get('row')
        if hall.quantity_rows < row:
            raise serial.ValidationError(f'Row with {row} number doesn\'t exist in current hall')
        # seat_categories = hall.get_seat_categories().values('pk')
        # if attrs.get('seat_category') not in seat_categories:
        #     raise serial.ValidationError(f'Current hall has no seats with this seat_category')
        return attrs


# class ImageSerializer(serial.Serializer):
#     image = serial.ImageField()

