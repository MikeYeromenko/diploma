import datetime

from colorfield.widgets import ColorWidget
from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _


from seance.models import Film, SeatCategory, Price, SeanceBase, Hall, Seance, Ticket


class FilmModelForm(forms.ModelForm):
    class Meta:
        model = Film
        fields = ('title', 'starring', 'director', 'duration', 'description', 'is_active', 'image', 'admin')
        widgets = {'admin': forms.HiddenInput,
                   'title': forms.TextInput(attrs={'class': 'form-control', 'style': 'color: black'}),
                   'starring': forms.TextInput(attrs={'class': 'form-control', 'style': 'color: black'}),
                   'director': forms.TextInput(attrs={'class': 'form-control', 'style': 'color: black'}),
                   'duration': forms.TextInput(attrs={'class': 'form-control', 'style': 'color: black'}),
                   'description': forms.Textarea(attrs={'class': 'form-control', 'style': 'color: black'}),
                   'is_active': forms.TextInput(attrs={'class': 'form-control', 'style': 'color: black'}),
                   }


class SeatCategoryModelForm(forms.ModelForm):
    color = forms.CharField(widget=ColorWidget(attrs={'class': 'form-control',
                                               'style': 'color: black'}))

    class Meta:
        model = SeatCategory
        fields = ('name', 'color')
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control',
                                                  'style': 'color: black'})}


class PriceModelForm(forms.ModelForm):

    class Meta:
        model = Price
        fields = ('seance', 'seat_category', 'price')
        widgets = {'seance': forms.Select(attrs={'class': 'form-control',
                                                 'style': 'color: black'}),
                   'seat_category': forms.Select(attrs={'class': 'form-control',
                                                 'style': 'color: black'}),
                   'price': forms.TextInput(attrs={'class': 'form-control',
                                                   'style': 'color: black'})}


# class PriceSeanceActivateForm(forms.ModelForm):
#     seance = forms.ChoiceField(disabled=True, widget=forms.TextInput(attrs={'class': 'form-control',
#                                                                             'style': 'color: black'}))
#     seat_category = forms.ChoiceField(disabled=True, widget=forms.TextInput(attrs={'class': 'form-control',
#                                                                             'style': 'color: black'}))
#
#     class Meta:
#         model = Price
#         fields = PriceModelForm.Meta.fields
#         widgets = {'price': forms.TextInput(attrs={'class': 'form-control', 'style': 'color: black'})}


class SeanceBaseCreateForm(forms.ModelForm):

    class Meta:
        model = SeanceBase
        exclude = ('created_at', 'updated_at')
        widgets = {'film': forms.Select(attrs={'class': 'form-control', 'style': 'color: black'}),
                   'hall': forms.Select(attrs={'class': 'form-control', 'style': 'color: black'}),
                   'date_starts': forms.TextInput(attrs={'class': 'form-control', 'style': 'color: black'}),
                   'date_ends': forms.TextInput(attrs={'class': 'form-control', 'style': 'color: black'})
                   }

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
                  'description', 'seance_base', 'admin')
        widgets = {'admin': forms.HiddenInput,
                   'time_starts': forms.TextInput(attrs={'class': 'form-control', 'style': 'color: black'}),
                   'advertisements_duration': forms.TextInput(attrs={'class': 'form-control', 'style': 'color: black'}),
                   'cleaning_duration': forms.TextInput(attrs={'class': 'form-control', 'style': 'color: black'}),
                   'description': forms.Textarea(attrs={'class': 'form-control', 'style': 'color: black'}),
                   'seance_base': forms.Select(attrs={'class': 'form-control', 'style': 'color: black'}),
                   }

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
        widgets = {**SeanceModelForm.Meta.widgets,
                   'is_active': forms.TextInput(attrs={'class': 'form-control', 'style': 'color: black'})
        }

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


class HallModelForm(forms.ModelForm):
    class Meta:
        model = Hall
        fields = ('name', 'quantity_seats', 'quantity_rows', 'description')


class HallUpdateForm(HallModelForm):
    class Meta(HallModelForm.Meta):
        fields = HallModelForm.Meta.fields + ('is_active', )

    def clean(self):
        """
        If admin decides to update quantity rows or quantity_seats its possible if hall is not active.
        Admin can deactivate Hall if there are no active base seances related to it
        """
        super(HallUpdateForm, self).clean()
        if ('is_active' in self.changed_data or 'quantity_seats' in self.changed_data or
                'quantity_rows' in self.changed_data):
            is_active = self.cleaned_data.get('is_active')
            if is_active and 'is_active' in self.changed_data:
                raise ValidationError(f'To activate Hall please use "Activate" button in Hall list. '
                                      f'Here its possible only to deactivate hall')
            active_base_seances = self.instance.base_seances.filter(Q(date_ends__gte=datetime.date.today()) &
                                                                    Q(hall=self.instance))
            if active_base_seances.count():
                raise ValidationError(f'You can\'t deactivate this hall or change its size because there are active '
                                      f'base seances in it: {active_base_seances.all()}')


class SeatsCreateForm(forms.Form):
    seat_starts = forms.IntegerField(min_value=1, initial=1, label=_('Seats start number'), required=True)
    seat_ends = forms.IntegerField(min_value=1, label=_('Seats end number'), required=True)
    hall = forms.IntegerField(widget=forms.HiddenInput, label=_(Hall), required=True)

    def __init__(self, choices=(), row_max_value=1000, *args, ** kwargs):
        super().__init__(*args, **kwargs)
        self.fields['row'] = forms.IntegerField(min_value=1, max_value=row_max_value,
                                                initial=1, label=_('Row number'), required=True)
        self.fields['seat_category'] = forms.ChoiceField(required=True, label=_('Choice seats category'),
                                                         choices=choices)

    def clean(self):
        super().clean()
        hall = get_object_or_404(Hall, pk=self.cleaned_data.get('hall'))
        if not hall:
            raise ValidationError(f'errors with Hall object occurred, please try again')


