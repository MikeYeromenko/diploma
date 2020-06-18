import datetime

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone, dateformat
from django.views.generic import ListView, CreateView, TemplateView, FormView, DetailView, RedirectView

from seance.forms import RegistrationForm, OrderingForm
from seance.models import Seance, AdvUser, Hall


class SeanceListView(ListView):
    model = Seance
    template_name = 'seance/index.html'

    def get_queryset(self):
        query = Q(seance_base__is_active=True)

        # if user wants to watch seances for tomorrow this key will be in GET

        if self.request.GET.get('days', None):
            tomorrow = datetime.date.today() + datetime.timedelta(days=1)
            query &= Q(seance_base__date_starts__lte=tomorrow) & Q(seance_base__date_ends__gte=tomorrow)
        else:
            query &= (Q(seance_base__date_starts__lte=datetime.date.today()) &
                      Q(seance_base__date_ends__gte=datetime.date.today()) &
                      Q(time_starts__gt=timezone.now()))

        seances = Seance.objects.filter(query)

        # if user selected type of ordering
        ordering_param = self.request.GET.get('ordering', None)
        if ordering_param:
            seances = self.order_queryset(ordering_param, seances)
        return seances

    def order_queryset(self, ordering_param, seances):
        """
        orders seances queryset by users ordering
        """
        if ordering_param == 'cheap':
            return seances.order_by('prices__price')
        if ordering_param == 'expensive':
            return seances.order_by('-prices__price')
        elif ordering_param == 'latest':
            return seances.order_by('-time_starts')
        elif ordering_param == 'closest':
            return seances.order_by('time_starts')

    def get_context_data(self, *args, **kwargs):
        """
        Adds OrderingForm to context
        :return: context
        """
        context = super().get_context_data(*args, **kwargs)

        # if there is a choice made by user, we render page with that choice
        ordering = self.request.GET.get('ordering', '')
        days = self.request.GET.get('days', '')
        ordering_form = OrderingForm(initial={'ordering': ordering, 'days': days})

        context['ordering_form'] = ordering_form
        return context


class SeanceDetailView(DetailView):
    model = Seance
    template_name = 'seance/seance_detail.html'


class RegisterUserView(CreateView):
    model = AdvUser
    form_class = RegistrationForm
    template_name = 'registration/register_user.html'
    success_url = reverse_lazy('seance:index')


class UserLoginView(LoginView):

    def form_valid(self, form):
        """
        Security check complete. Log the user in.
        Updates last_activity field
        """
        user = get_object_or_404(AdvUser, pk=form.get_user().pk)
        user.last_activity = timezone.now()
        user.save()
        login(self.request, user)
        return HttpResponseRedirect(self.get_success_url())


class UserLogoutView(LogoutView):
    pass


class UserProfileView(TemplateView):
    template_name = 'seance/profile.html'


class BasketView(LoginRequiredMixin, TemplateView):
    template_name = 'seance/basket.html'


class BasketRedirectView(LoginRequiredMixin, RedirectView):
    url = reverse_lazy('seance:basket')

    # def dispatch(self, request, *args, **kwargs):
    #     self.add_to_session(request)
    #     return super(BasketRedirectView, self).dispatch(request, *args, **kwargs)
    #
    # def inspect_double_chosen(self, request):
    #     """
    #     Looks through the basket, and if dict with the same row, seat and seance is in it, messages user
    #     he can't book the same seat twice
    #     """
    #     row = request.GET.get('row', None)
    #     seat = request.GET.get('seat', None)
    #     seance_pk = request.GET.get('seance', None)
    #     basket = request.session.get('basket')
    #     if basket and row and seat and seance_pk:
    #         for key in basket:
    #             if (basket[key]['row'] == row and basket[key]['seat'] == seat
    #                     and basket[key]['seance_pk'] == seance_pk):
    #                 messages.add_message(request, messages.INFO, f'You can\'t choose the same seat twice')
    #                 self.url = reverse_lazy('seance:seance_detail', kwargs={'pk': seance_pk})
    #                 return None, None, None
    #     return row, seat, seance_pk
    #
    # def add_to_session(self, request):
    #     """Adds info about the ticket in the basket into sessions"""
    #     row, seat, seance_pk = self.inspect_double_chosen(request)
    #     if row and seat and seance_pk:
    #         if not request.session.get('basket', None):
    #             request.session['basket'] = {}
    #         seance = get_object_or_404(Seance, pk=seance_pk)
    #         key = str(datetime.datetime.now().timestamp()).replace('.', '')
    #         request.session['basket'][f'{key}'] = {
    #             'row': row,
    #             'seat': seat,
    #             'seance_pk': seance_pk,
    #             'film': seance.film.title,
    #             'hall': seance.hall.name,
    #             'price': str(seance.ticket_price),
    #             'created': dateformat.format(timezone.now(), 'Y-m-d H:i:s')
    #         }
    #         request.session['last_seance'] = seance_pk
    #         request.session.modified = True


class BasketCancelView(LoginRequiredMixin, RedirectView):
    pattern_name = 'seance:basket'

    # def dispatch(self, request, *args, **kwargs):
    #     key = request.GET.get('seance', None)
    #     request.session.get('basket').pop(key)
    #     request.session.modified = True
    #     return super(BasketCancelView, self).dispatch(request, *args, **kwargs)
