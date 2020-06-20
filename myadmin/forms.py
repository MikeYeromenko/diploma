import datetime

from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _


from seance.models import Film, SeatCategory, Price, SeanceBase, Hall, Seance


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


class SeanceBaseCreateForm(forms.ModelForm):

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

    def clean(self, sb_pk_exclude=None):
        """Validates, that new seance doesn't intersect with others seances base with this film in this hall.
        We also can't create Base Seance on a film, that is not active
        sb_exclude=None is used for inheritor - SeanceBaseUpdateForm, not to validate fields while updating
        with itself fields"""
        super().clean()
        date_starts = self.cleaned_data.get('date_starts')
        date_ends = self.cleaned_data.get('date_ends')
        film = Film.objects.get(title=self.cleaned_data.get('film'))
        hall = Hall.objects.get(name=self.cleaned_data.get('hall'))

        if not film:
            raise ValidationError('You have to specify valid film')

        if not hall:
            raise ValidationError('You have to specify valid hall')

        if not film.is_active:
            raise ValidationError('Film must have is_active status set in True')

        if not hall.is_active:
            raise ValidationError('Hall must have is_active status set in True')

        if date_starts > date_ends:
            raise ValidationError('date_starts must be less or equal to date_ends')

        if sb_pk_exclude:
            seances_base = SeanceBase.validate_seances_base_intersect(date_starts, date_ends, film, hall, sb_pk_exclude)
        else:
            seances_base = SeanceBase.validate_seances_base_intersect(date_starts, date_ends, film, hall)
        if seances_base:
            raise ValidationError(f'There are intersections in dates with other Base Seances on this film '
                                  f'in this hall: {seances_base}')


class SeanceBaseUpdateForm(SeanceBaseCreateForm):

    def clean(self):
        """Validates that your changes will not interfere users who had already bought tickets"""
        sb_pk_exclude = self.instance.pk
        super(SeanceBaseUpdateForm, self).clean(sb_pk_exclude=sb_pk_exclude)
        seance_base = get_object_or_404(SeanceBase, pk=sb_pk_exclude)
        if 'date_starts' in self.changed_data:
            date_starts = self.cleaned_data.get('date_starts')
            if date_starts > self.instance.date_starts:
                tickets_list = [seance.get_sold_but_not_used_tickets(date_starts=self.instance.date_starts,
                                                                     date_ends=date_starts - datetime.timedelta(days=1))
                                for seance in seance_base.seances.all()]
                if tickets_list:
                    raise ValidationError(f'You can\'t change date_starts because there are sold tickets on '
                                    f'dates you want to exclude: {tickets_list}')
        if 'date_ends' in self.changed_data:
            date_ends = self.cleaned_data.get('date_ends')
            if date_ends < self.instance.date_ends:
                tickets_list = [seance.get_sold_but_not_used_tickets(date_starts=date_ends + datetime.timedelta(days=1),
                                                                     date_ends=self.instance.date_ends)
                                for seance in seance_base.seances.all()]
                if tickets_list:
                    raise ValidationError(f'You can\'t change date_starts because there are sold tickets on '
                                    f'dates you want to exclude: {tickets_list}')

        if 'hall' in self.changed_data:
            hall = Hall.objects.get(name=self.cleaned_data.get('hall'))
            if hall.quantity_seats < self.instance.hall.quantity_seats:
                tickets_list = [seance.get_sold_but_not_used_tickets(date_starts=datetime.date.today(),
                                                                     date_ends=seance_base.date_ends)
                                for seance in seance_base.seances.all()]
                if tickets_list:
                    raise ValidationError(f'You can\'t change hall because there are sold tickets on '
                                    f'seances in the previous hall: {tickets_list}; \n and new hall'
                                    f'you want to set has less quantity of seats than hall set before')

        if 'film' in self.changed_data:
            tickets_list = [seance.get_sold_but_not_used_tickets(date_starts=datetime.date.today(),
                                                                 date_ends=seance_base.date_ends)
                            for seance in seance_base.seances.all()]
            if tickets_list:
                raise ValidationError(f'You can\'t change hall because there are sold tickets on '
                                      f'seances with film you want to change: {tickets_list}')


class SeanceModelForm(forms.ModelForm):
    class Meta:
        model = Seance
        fields = ('time_starts', 'advertisements_duration', 'cleaning_duration',
                  'description', 'seance_base')

    def clean(self, seance_exclude_pk=None):
        """Validates that Seance object doesn't intersect with other seances in current hall"""
        super(SeanceModelForm, self).clean()
        starts = self.cleaned_data.get('time_starts')
        adds = self.cleaned_data.get('advertisements_duration')
        clean = self.cleaned_data.get('cleaning_duration')
        sb = self.cleaned_data.get('seance_base')
        if self.is_valid():
            # create instance of Seance without saving to database to auto generate time_ends etc
            seance = Seance(time_starts=starts, advertisements_duration=adds,
                            cleaning_duration=clean, seance_base=sb)
            seance.save(commit=False)
            if seance_exclude_pk:
                seances = seance.validate_seances_intersect(seance_exclude_pk=seance_exclude_pk)
            else:
                seances = seance.validate_seances_intersect()
            if seances:
                raise ValidationError(f'There are intersections in times with other Seances in this hall: '
                                      f'{seances}'
                                      f'Seance\'s you are going to create values: '
                                      f'time_starts: {seance.time_starts}; time_hall_free: {seance.time_hall_free}, '
                                      f'film duration: {seance.seance_base.film.duration}')


class SeanceUpdateForm(SeanceModelForm):
    class Meta(SeanceModelForm.Meta):
        fields = SeanceModelForm.Meta.fields + ('is_active', )

    def clean(self):
        super().clean(seance_exclude_pk=self.instance.pk)
        if 'is_active' in self.changed_data:
            is_active = self.cleaned_data.get('is_active')
            if is_active:
                raise ValidationError(f'To activate Seance please use "Activate" button in Seance list'
                                      f'Here its possible only to deactivate seance')
            else:
                tickets = self.instance.get_sold_but_not_used_tickets()
                if tickets:
                    raise ValidationError(f'You can\'t deactivate this seance because there are sold tickets on '
                                          f'it: {tickets}')
        if 'time_starts' in self.changed_data:
            tickets = self.instance.get_sold_but_not_used_tickets(date_starts=datetime.date.today(),
                                                                  date_ends=self.instance.seance_base.date_ends)
            if tickets:
                raise ValidationError(f'You can\'t change time_starts because there are sold and not used tickets on '
                                      f'it: {tickets}')
