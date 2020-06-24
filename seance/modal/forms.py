from bootstrap_modal_forms.forms import BSModalForm
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _


from seance.forms import ORDERING_CHOICES, DAY_CHOICES
from seance.models import AdvUser


class ModalOrderingForm(BSModalForm):
    ordering = forms.ChoiceField(choices=ORDERING_CHOICES, label=_('Order by'), required=False)
    days = forms.ChoiceField(choices=DAY_CHOICES, label=_('When?'), required=False)


class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = AdvUser
        fields = ['username', 'password']