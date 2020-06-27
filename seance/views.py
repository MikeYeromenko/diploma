import datetime

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone, dateformat
from django.views.generic import ListView, CreateView, TemplateView, FormView, DetailView, RedirectView, View

from seance.forms import RegistrationForm, OrderingForm, UserAuthenticationForm
from seance.models import Seance, AdvUser, Hall, Seat, Purchase, Ticket


class SeanceListView(ListView):
    model = Seance
    template_name = 'seance/index.html'
    context_object_name = 'seance_list'

    def get_queryset(self):
        # if user wants to watch seances for tomorrow 'days' will be in GET

        if self.request.GET.get('days', None):
            date = datetime.date.today() + datetime.timedelta(days=1)
            self.request.session['seance_date'] = str(datetime.date.today() + datetime.timedelta(days=1))
        else:
            date = None
            self.request.session['seance_date'] = str(datetime.date.today())
            
        seances = Seance.get_active_seances_for_day(date)

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
            # return seances.order_by('prices__price')
            return Seance.order_by_cheap_first(seances)
        if ordering_param == 'expensive':
            # return seances.order_by('-prices__price')
            return Seance.order_by_expensive_first(seances)
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        seance_date = self.request.session.get('seance_date', None)
        tickets = context.get('seance').tickets.filter(date_seance=seance_date)

        seats_taken = [ticket.seat for ticket in tickets]
        context['seats_taken'] = seats_taken

        return context


class RegisterUserView(CreateView):
    model = AdvUser
    form_class = RegistrationForm
    template_name = 'registration/register_user.html'
    success_url = reverse_lazy('seance:index')


class UserLoginView(LoginView):
    form_class = UserAuthenticationForm
    success_url = reverse_lazy('seance:index')

    def form_valid(self, form):
        """
        Security check complete. Log the user in.
        Updates last_activity field in sessions
        """
        # user = get_object_or_404(AdvUser, pk=form.get_user().pk)
        # user.last_activity = timezone.now()
        # user.save()
        if not self.request.user.is_superuser:
            self.request.session['last_activity'] = str(datetime.datetime.now())
        return super().form_valid(form)


class UserLogoutView(LogoutView):
    pass


class UserProfileView(TemplateView):
    template_name = 'seance/profile.html'


class BasketView(LoginRequiredMixin, TemplateView):
    template_name = 'seance/basket.html'


class BasketRedirectView(LoginRequiredMixin, RedirectView):
    url = reverse_lazy('seance:basket')

    def dispatch(self, request, *args, **kwargs):
        self.add_to_session(request)
        return super(BasketRedirectView, self).dispatch(request, *args, **kwargs)

    def inspect_double_chosen(self, request):
        """
        Looks through the basket, and if dict with the same row, seat and seance is in it, messages user
        he can't book the same seat twice
        """
        seat_pk = request.GET.get('seat_pk', None)
        row = request.GET.get('row', None)
        number = request.GET.get('number', None)
        seance_pk = request.GET.get('seance', None)
        seance_date = request.GET.get('seance_date', None)
        basket = request.session.get('basket')
        if basket and seat_pk and seance_pk and seance_date and row and number:
            for key in basket:
                if (basket[key]['seat_pk'] == seat_pk and
                        basket[key]['seance_pk'] == seance_pk and
                        basket[key]['seance_date'] == seance_date):
                    messages.add_message(request, messages.INFO, f'You can\'t choose the same seat twice')
                    self.url = reverse_lazy('seance:seance_detail', kwargs={'pk': seance_pk})
                    return None, None, None, None, None
        return seat_pk, seance_pk, seance_date, row, number

    def add_to_session(self, request):
        """Adds info about the ticket in the basket into sessions"""
        seat_pk, seance_pk, seance_date, row, number = self.inspect_double_chosen(request)
        if seat_pk and seance_pk and seance_date:
            if not request.session.get('basket', None):
                request.session['basket'] = {}
            seance = get_object_or_404(Seance, pk=seance_pk)
            seat = get_object_or_404(Seat, pk=seat_pk)
            price = 0
            if seat and seance:
                price = seance.prices.get(seat_category=seat.seat_category).price

            key = str(datetime.datetime.now().timestamp()).replace('.', '')
            request.session['basket'][f'{key}'] = {
                'seat_pk': seat_pk,
                'row': row,
                'number': number,
                'seance_pk': seance_pk,
                'seance_date': seance_date,
                'film': seance.seance_base.film.title,
                'hall': seance.seance_base.hall.name,
                'price': str(price),
                'created': dateformat.format(timezone.now(), 'Y-m-d H:i:s')
            }
            request.session['last_seance'] = seance_pk
            request.session['total_price'] = self.get_total_price(request.session.get('basket'))
            request.session.modified = True

    @staticmethod
    def get_total_price(basket):
        """count total price of tickets in the basket"""
        total_price = 0
        for key in basket:
            total_price += float(basket[key]['price'])
        return total_price


class BasketCancelView(LoginRequiredMixin, RedirectView):
    pattern_name = 'seance:basket'

    def dispatch(self, request, *args, **kwargs):
        key = request.GET.get('seance_cancel', None)
        pop_element = request.session.get('basket').pop(key, None)
        total_price = float(request.session.get('total_price')) - float(pop_element.get('price'))
        request.session['total_price'] = total_price
        request.session.modified = True
        return super(BasketCancelView, self).dispatch(request, *args, **kwargs)


class PurchaseCreateView(LoginRequiredMixin, RedirectView):
    url = reverse_lazy('seance:my_tickets')

    def post(self, request, *args, **kwargs):
        # if there are problems - don't create purchase
        if not self.check_basket_and_total_price(request):
            self.session_clean_and_redirect(request)
            return super().post(request, *args, **kwargs)

        # get user object
        user = get_object_or_404(AdvUser, pk=request.user.pk)
        tickets = []
        self.create_tickets_datalist(request, tickets, *args, **kwargs)
        if tickets:
            # last element is total_price
            total_price = tickets.pop(len(tickets) - 1)
            if user.wallet - total_price >= 0:
                user.wallet -= total_price
                user.save()
                purchase = Purchase.objects.create(user=user)
                for ticket in tickets:
                    Ticket.objects.create(seance=ticket.get('seance'),
                                          date_seance=ticket.get('date_seance'),
                                          seat=ticket.get('seat'),
                                          purchase=purchase,
                                          price=ticket.get('price')
                                          )
                self.session_clean_and_redirect(request, change_url=False)
                return super().post(request, *args, **kwargs)
            messages.add_message(request, messages.INFO, 'Insufficient funds')
        self.session_clean_and_redirect(request)
        return super().post(request, *args, **kwargs)

    def create_purchase_and_tickets(self):
        """Creates purchase and tickets in it"""
        pass

    def session_clean_and_redirect(self, request, change_url=True):
        """Removes all custom data from session"""
        if change_url:
            self.url = reverse_lazy('seance:index')
        request.session.pop('basket', None)
        request.session.pop('last_seance', None)
        request.session.pop('total_price', None)

    @staticmethod
    def check_basket_and_total_price(request):
        """Checks if user has tickets in basket and enough money for them"""
        basket = request.session.get('basket', None)
        total_price = request.session.get('total_price', None)
        if not basket:
            return False
        if total_price:
            if total_price > request.user.wallet:
                messages.add_message(request, messages.INFO, 'Insufficient funds')
                return False
        return True

    @staticmethod
    def create_tickets_datalist(request, tickets, *args, **kwargs):
        """
        Creates list with data for creating tickets.
        We will create tickets only if initial data for all of them is OK
        If not - clean basket and ask user to full it once again
        List of initial data for tickets is saved in argument tickets, which is the same list() -
        tickets in main post()

        Also check that tickets with the same data don't exist
        Last element in tickets[], if its not empty, we push total_price
        """
        basket = request.session.get('basket', None)
        total_price = 0
        for key in basket:
            seat = get_object_or_404(Seat, pk=basket[key].get('seat_pk'))
            seance = get_object_or_404(Seance, pk=basket[key].get('seance_pk'))
            seance_date = basket[key].get('seance_date', None)

            price = seance.prices.get(seat_category=seat.seat_category).price
            total_price += price

            # if ticket already exists or there problems with init. data - don't create purchase
            if (not seat or not seance or not seance_date or
                    Ticket.objects.filter(seance=seance, seat=seat, date_seance=seance_date)):
                messages.add_message(request, messages.ERROR, 'Error occurred, please try once again')
                tickets = []
                break
            else:
                tickets.append({
                    'seance': seance,
                    'date_seance': seance_date,
                    'seat': seat,
                    'price': price
                })
        if tickets:
            tickets.append(total_price)


class PurchaseListView(LoginRequiredMixin, ListView):
    model = Purchase

    def get_queryset(self):
        return Purchase.objects.filter(user_id=self.request.user.pk)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['money_spent'] = self.request.user.sum_money_spent
        return context


