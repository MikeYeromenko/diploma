from django import forms
from django.utils.translation import gettext_lazy as _


from seance.models import Film, SeatCategory


class FilmModelForm(forms.ModelForm):
    class Meta:
        model = Film
        fields = ('title', 'starring', 'director', 'duration', 'description', 'is_active')


class SeatCategoryModelForm(forms.ModelForm):

    class Meta:
        model = SeatCategory
        fields = ('name', )



