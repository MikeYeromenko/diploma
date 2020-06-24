from bootstrap_modal_forms.generic import BSModalCreateView, BSModalLoginView
from django.urls import reverse_lazy
from django.views.generic import FormView

from seance.modal import forms


class ModalOrderingView(FormView):
    form_class = forms.ModalOrderingForm
    template_name = 'modal/ordering_form.html'
    # success_message = 'Success: You were successfully logged in.'
    # success_url = reverse_lazy('index')


class CustomLoginView(BSModalLoginView):
    authentication_form = forms.CustomAuthenticationForm
    template_name = 'modal/login_modal.html'
    success_message = 'Success: You were successfully logged in.'
    success_url = reverse_lazy('seance:index')

    def get_success_url(self):
        return '/'     #   reverse_lazy('seance:index')
    
    def post(self, request, *args, **kwargs):
        return super(CustomLoginView, self).post(request, *args, **kwargs)
