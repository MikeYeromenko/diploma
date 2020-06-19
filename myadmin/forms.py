from django import forms

from seance.models import Film


class FilmUpdateCreateForm(forms.ModelForm):
    class Meta:
        model = Film
        fields = ('title', 'starring', 'director', 'duration', 'description', 'is_active')


