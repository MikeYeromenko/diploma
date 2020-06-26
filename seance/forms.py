from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from seance.models import AdvUser, Ticket


class RegistrationForm(forms.ModelForm):
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': _('username'),
                                                                            'class': 'form-control'}))
    password1 = forms.CharField(required=True, min_length=8,
                                widget=forms.PasswordInput(attrs={'placeholder': _('password'),
                                                                  'class': 'form-control'}),
                                help_text=password_validation.password_validators_help_text_html())
    password2 = forms.CharField(required=True, min_length=8,
                                widget=forms.PasswordInput(attrs={'placeholder': _('repeat password'),
                                                                  'class': 'form-control'}),
                                help_text=_('Enter the same password for check please'))
    email = forms.EmailField(min_length=8, widget=forms.TextInput(attrs={'placeholder': _('email'),
                                                                         'class': 'form-control'}),
                             help_text=_('We recommend to fill email to get tickets on it'), required=False)

    class Meta:
        model = AdvUser
        fields = ('username', 'password1', 'password2', 'email')

    def clean_password1(self):
        """
        Validates password1 to satisfy requirements for passwords
        """
        password1 = self.cleaned_data.get('password1')
        if password1:
            password_validation.validate_password(password1)
        return password1

    def clean(self):
        """
        Checks that password1 is equal with password2
        """
        super().clean()
        password1, password2 = self.cleaned_data.get('password1'), self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            errors = {'password2': ValidationError(_('passwords mismatch'), code='password_mismatch')}
            raise ValidationError(errors)

    def is_valid(self):
        return super(RegistrationForm, self).is_valid()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


ORDERING_CHOICES = (
    ('', _('default ordering')),
    ('cheap', _('from cheap to expensive')),
    ('expensive', _('from expensive to cheap')),
    ('latest', _('latest first')),
    ('closest', _('closest first'))
)

DAY_CHOICES = (
    ('', 'today'),
    ('tomorrow', 'tomorrow')
)


class OrderingForm(forms.Form):
    ordering = forms.ChoiceField(choices=ORDERING_CHOICES, label=_('Order by: '), required=False, widget=
                                 forms.Select(attrs={'class': 'form-control'}))
    days = forms.ChoiceField(choices=DAY_CHOICES, label=_('When? '), required=False, widget=
                             forms.Select(attrs={'class': 'form-control'}))


class UserAuthenticationForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'}))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class': 'form-control'}),
    )


# class TicketForm(forms.Form):
#     # film =
#     row = forms.IntegerField(label=_('Row'))
#     number = forms.IntegerField(label=_('Seat number'))
#     date = forms.DateField(label=_('Date of seance'))

