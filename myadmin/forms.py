import datetime

from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


from seance.models import Film, SeatCategory, Price, SeanceBase


class FilmModelForm(forms.ModelForm):
    class Meta:
        model = Film
        fields = ('title', 'starring', 'director', 'duration', 'description', 'is_active')


class SeatCategoryModelForm(forms.ModelForm):

    class Meta:
        model = SeatCategory
        fields = ('name', )


class PriceModelForm(forms.ModelForm):

    class Meta:
        model = Price
        fields = ('seance', 'seat_category', 'price')


class SeanceBaseModelForm(forms.ModelForm):

    class Meta:
        model = SeanceBase
        exclude = ('created_at', 'updated_at')

    def clean_date_ends(self):
        """Validates, that date_ends is more or equal date.today()"""
        date_ends = self.cleaned_data.get('date_ends')
        if date_ends:
            if date_ends < datetime.date.today():
                raise ValidationError('Date ends must not be less, then today\'s date')
        return date_ends



