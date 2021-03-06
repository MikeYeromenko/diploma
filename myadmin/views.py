import datetime

from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, DetailView, ListView, UpdateView, CreateView, DeleteView, FormView, \
    RedirectView, View

from myadmin import forms
from myadmin.forms import FilmModelForm
from seance.models import Film, AdvUser, SeatCategory, Price, Seance, SeanceBase, Hall


class IsStaffRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated and is_staff."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated and not request.user.is_staff:
            messages.add_message(request, messages.INFO, f'This page is for staff only. Enter your credentials '
                                                         f'to confirm your staff status')
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class AdminMainView(IsStaffRequiredMixin, TemplateView):
    template_name = 'myadmin/main.html'


class FilmUpdateView(IsStaffRequiredMixin, UpdateView):
    model = Film
    template_name = 'myadmin/films/film_update_form.html'
    form_class = forms.FilmModelForm
    success_url = reverse_lazy('myadmin:film_list')

    def get_initial(self):
        initial = super(FilmUpdateView, self).get_initial()
        initial.update({'admin': self.request.user})
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs


class FilmListView(IsStaffRequiredMixin, ListView):
    model = Film
    paginate_by = 30
    template_name = 'myadmin/films/film_list.html'

    def get_queryset(self):
        """Filters only films with is_active = True status"""
        active = self.request.GET.get('active', False)
        return Film.objects.filter(is_active=active) if active else Film.objects.all()


class FilmCreateView(IsStaffRequiredMixin, CreateView):
    model = Film
    form_class = forms.FilmModelForm
    success_url = reverse_lazy('myadmin:film_list')
    template_name = 'myadmin/films/film_create_form.html'

    def post(self, request, *args, **kwargs):
        """Adds admin, who creates film, to admin field"""
        admin = get_object_or_404(AdvUser, pk=request.user.pk)
        form = FilmModelForm(request.POST)
        if form.is_valid():
            film = form.save(commit=False)
            film.admin = admin
            film.save()
            messages.add_message(request, messages.SUCCESS, _('Film was created successfully'))
            return redirect(self.success_url)
        return render(request, 'myadmin/films/film_create_form.html', {'form': form})


class FilmDeleteView(IsStaffRequiredMixin, DeleteView):
    model = Film
    success_url = reverse_lazy('myadmin:film_list')
    template_name = 'myadmin/films/film_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        """
        We can't delete film, if there are Seance Base objects related to it. First we need to delete SeanceBase
        object
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        # check if there are related SBases to our Film
        seance_bases = self.object.base_seances
        if seance_bases.count():
            messages.add_message(request, messages.INFO, f"We can't delete film: {self.object.title}, "
                                                         f"because there are SBases related to it. First "
                                                         f"we need to delete all SeanceBase objects:"
                                                         f" {seance_bases}")
            return redirect(success_url)
        self.object.delete()
        return redirect(success_url)


class SeatCategoryCRUDView(IsStaffRequiredMixin, FormView):
    template_name = 'myadmin/seat_category/seat_category_list_form.html'
    form_class = forms.SeatCategoryModelForm
    success_url = reverse_lazy('myadmin:seat_category_crud')

    def get_context_data(self, **kwargs):
        context = super(SeatCategoryCRUDView, self).get_context_data(**kwargs)
        categories = SeatCategory.objects.all()
        object_list = [(category, forms.SeatCategoryModelForm(instance=category)) for category in categories]
        context['object_list'] = object_list
        return context

    def post(self, request, *args, **kwargs):
        """
        Creates or updates seat category, depending upon a form it was posted by
        :return:
        """
        admin = get_object_or_404(AdvUser, pk=request.user.pk)
        pk = kwargs.get('pk', None)
        if pk:
            seat_category = get_object_or_404(SeatCategory, pk=pk)
            form_update = forms.SeatCategoryModelForm(request.POST, instance=seat_category)
            if form_update.is_valid():
                seat_category = form_update.save(commit=False)
                seat_category.admin = admin
                seat_category.save()
                messages.add_message(request, messages.SUCCESS, _(f'Seat category {seat_category.name}'
                                                                  f' was updated successfully'))
                return redirect(self.success_url)
            else:
                render(request, reverse_lazy('myadmin:seat_category_crud'), {
                    'form_update': form_update
                })
        else:
            form = self.get_form()
            if form.is_valid():
                seat_category = form.save(commit=False)
                seat_category.admin = admin
                seat_category.save()
                messages.add_message(request, messages.SUCCESS, _(f'Seat category {seat_category.name}'
                                                                  f' was created successfully'))
                return redirect(self.success_url)
            else:
                return self.form_invalid(form)


class SeatCategoryDeleteView(IsStaffRequiredMixin, DeleteView):
    model = SeatCategory
    success_url = reverse_lazy('myadmin:seat_category_crud')
    template_name = 'myadmin/seat_category/seat_category_delete.html'

    def delete(self, request, *args, **kwargs):
        """We can't delete seat category, if there are seats related to it. First we need to delete Hall object"""
        self.object = self.get_object()
        success_url = self.get_success_url()
        # check if there are seats related to our SeatCategory
        if self.object.seats.last():
            messages.add_message(request, messages.INFO, f"We can't delete seat category: {self.object.name}, "
                                                         f"because there are seats related to it. First "
                                                         f"we need to delete all Hall objects with seats, "
                                                         f"related to this category")
            return redirect(success_url)
        self.object.delete()
        return redirect(success_url)


class PriceTemplateView(IsStaffRequiredMixin, TemplateView):
    template_name = 'myadmin/price/price_list.html'

    def get_context_data(self, **kwargs):
        """Adds list of prices to context"""
        context = super().get_context_data(**kwargs)
        form = forms.PriceModelForm()
        price_list = Price.objects.all().order_by('-updated_at')
        context['price_objects'] = [(price, forms.PriceModelForm(instance=price)) for price in price_list]
        context['form'] = form
        return context


class PriceUpdateView(IsStaffRequiredMixin, UpdateView):
    model = Price
    # fields = ('seance', 'seat_category', 'price')
    template_name = 'myadmin/price/price_create_update.html'
    success_url = reverse_lazy('myadmin:price_list')
    form_class = forms.PriceModelForm


class PriceDeleteView(IsStaffRequiredMixin, DeleteView):
    model = Price
    success_url = reverse_lazy('myadmin:price_list')
    template_name = 'myadmin/price/price_confirm_delete.html'

    def post(self, request, *args, **kwargs):
        """If price is in active seances, we cannot delete it, only modify"""
        price = get_object_or_404(Price, pk=kwargs.get('pk'))
        if price.seance:
            messages.add_message(request, messages.INFO, 'You can\'t delete price if there are related to it '
                                                         'seances.\n Try to delete seance first.\n Or you may update '
                                                         'this price, but not to delete!')
            return redirect(self.success_url)
        return self.delete(request, *args, **kwargs)


class PriceCreateView(IsStaffRequiredMixin, CreateView):
    model = Price
    success_url = reverse_lazy('myadmin:price_list')
    template_name = 'myadmin/price/price_list.html'
    form_class = forms.PriceModelForm


class SeanceBaseTemplateView(IsStaffRequiredMixin, TemplateView):
    template_name = 'myadmin/seance_base/seance_base_list.html'

    def get_context_data(self, **kwargs):
        """Adds list of prices to context"""
        context = super().get_context_data(**kwargs)
        form = forms.SeanceBaseCreateForm(initial={'date_starts': datetime.date.today(),
                                                   'date_ends': datetime.date.today() + datetime.timedelta(days=15),
                                                   })
        # sb_list = SeanceBase.objects.filter(date_ends__gte=datetime.date.today())
        sb_list = SeanceBase.objects.filter()
        context['sb_objects'] = [(sb, forms.SeanceBaseCreateForm(instance=sb)) for sb in sb_list]
        context['form'] = form
        return context


class SeanceBaseUpdateView(IsStaffRequiredMixin, UpdateView):
    model = SeanceBase
    template_name = 'myadmin/seance_base/seancebase_update.html'
    success_url = reverse_lazy('myadmin:seance_base_list')
    form_class = forms.SeanceBaseUpdateForm


class SeanceBaseCreateView(IsStaffRequiredMixin, CreateView):
    model = SeanceBase
    template_name = 'myadmin/seance_base/seance_base_list.html'
    success_url = reverse_lazy('myadmin:seance_base_list')
    form_class = forms.SeanceBaseCreateForm


class SeanceBaseDeleteView(IsStaffRequiredMixin, DeleteView):
    model = SeanceBase
    template_name = 'myadmin/seance_base/seancebase_confirm_delete.html'
    success_url = reverse_lazy('myadmin:seance_base_list')

    def post(self, request, *args, **kwargs):
        """If SeanceBase we want to delete has related seances we can't delete it"""
        seance_base = get_object_or_404(SeanceBase, pk=kwargs.get('pk'))
        if seance_base.seances.all():
            messages.add_message(request, messages.INFO, 'You can\'t delete base seance if there are related to it '
                                                         'seances.\n Try to delete seances first.\n Or you may update '
                                                         'this base seance, but not to delete!')
            return redirect(self.success_url)
        return self.delete(request, *args, **kwargs)


class SeanceListView(IsStaffRequiredMixin, ListView):
    model = Seance
    template_name = 'myadmin/seances/seance_list.html'
    paginate_by = 10

    def get_queryset(self):
        return Seance.objects.all().order_by('-updated_at')


class SeanceUpdateView(IsStaffRequiredMixin, UpdateView):
    model = Seance
    success_url = reverse_lazy('myadmin:seance_list')
    template_name = 'myadmin/seances/seance_update_form.html'
    form_class = forms.SeanceUpdateForm

    def get_initial(self):
        """Return the initial data to use for forms on this view."""
        initial = super().get_initial()
        initial.update({'admin': self.request.user})
        return initial.copy()


class SeanceCreateView(IsStaffRequiredMixin, CreateView):
    model = Seance
    template_name = 'myadmin/seances/seance_create_form.html'
    form_class = forms.SeanceModelForm
    success_url = reverse_lazy('myadmin:seance_list')

    def get_initial(self):
        """Return the initial data to use for forms on this view."""
        initial = super().get_initial()
        initial.update({'admin': self.request.user})
        return initial.copy()


class SeanceDeleteView(IsStaffRequiredMixin, DeleteView):
    model = Seance
    template_name = 'myadmin/seances/seance_confirm_delete.html'
    success_url = reverse_lazy('myadmin:seance_list')

    def post(self, request, *args, **kwargs):
        """We can't delete Seance if it is active or there are Ticket or Price objects related to it"""
        seance = get_object_or_404(Seance, pk=kwargs.get('pk'))
        if seance.is_active or seance.tickets.all() or seance.prices.all():
            messages.add_message(request, messages.INFO, f"We can't delete {seance} if it is active or there are "
                                                         f"Ticket or Price objects related to it. "
                                                         f"Tickets: {seance.tickets.all()}, "
                                                         f"prices: {seance.prices.all()}")
            return redirect(self.success_url)
        return self.delete(request, *args, **kwargs)


class SeanceActivateView(IsStaffRequiredMixin, FormView):
    template_name = 'myadmin/seances/seance_activate.html'
    form_class = forms.PriceModelForm
    success_url = reverse_lazy('myadmin:seance_list')

    def dispatch(self, request, *args, **kwargs):
        """Adds Seance object to self"""
        self.seance = get_object_or_404(Seance, pk=kwargs.get('pk'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seance'] = self.seance
        result_dict = self.seance.activate()
        if result_dict.get('success'):
            context['success'] = True
            return context
        context['success'] = False
        context['errors'] = result_dict.get('errors_list')
        sc = result_dict.get('seat_categories')
        if sc:
            pass
            context['form'] = self.form_class(initial={
                'seance': self.seance,
                'seat_category': sc[0]
            })
        else:
            context['form'] = None
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.get_form()
        if form.is_valid():
            form.save()
        return redirect(reverse_lazy('myadmin:seance_activate', kwargs={'pk': self.seance.pk}))


class HallListView(IsStaffRequiredMixin, ListView):
    model = Hall
    template_name = 'myadmin/hall/hall_list.html'
    queryset = Hall.objects.all()


class HallUpdateView(IsStaffRequiredMixin, UpdateView):
    model = Hall
    template_name = 'myadmin/hall/hall_update_form.html'
    success_url = reverse_lazy('myadmin:hall_list')
    form_class = forms.HallUpdateForm

    def form_valid(self, form):
        """Adds admin to Hall"""
        self.object = form.save(commit=False)
        self.object.admin = self.request.user
        self.object.save()
        return super().form_valid(form)


class HallCreateView(IsStaffRequiredMixin, CreateView):
    model = Hall
    template_name = 'myadmin/hall/hall_create_form.html'
    success_url = reverse_lazy('myadmin:hall_list')
    form_class = forms.HallModelForm

    def get_initial(self):
        """Return the initial data to use for forms on this view."""
        initial = super().get_initial()
        initial.update({'admin': self.request.user})
        return initial.copy()


class HallDeleteView(IsStaffRequiredMixin, DeleteView):
    model = Hall
    template_name = 'myadmin/hall/hall_confirm_delete.html'
    success_url = reverse_lazy('myadmin:hall_list')

    def delete(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        if self.object.is_active:
            messages.add_message(request, messages.INFO, f'We can\' delete {self.object.name} hall '
                                                         f'because its status is_active=True. Deactivate it first')
            return redirect(success_url)
        messages.add_message(request, messages.INFO, f'{self.object.name} deleted successfully')
        self.object.delete()
        return redirect(success_url)


def get_categories():
    categories = SeatCategory.objects.all()
    return [(c.id, c.name) for c in categories]


class HallActivateView(IsStaffRequiredMixin, FormView):
    form_class = forms.SeatsCreateForm
    template_name = 'myadmin/hall/hall_activate.html'
    success_url = reverse_lazy('myadmin:hall_list')

    def dispatch(self, request, *args, **kwargs):
        self.hall = get_object_or_404(Hall, pk=kwargs.get('pk'))
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        return {'hall': self.hall.pk}

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'choices': get_categories(),
            'row_max_value': self.hall.quantity_rows
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        result = self.hall.activate_hall()
        context['hall'] = self.hall

        seat_categories = [sc for sc in SeatCategory.objects.all()]
        context['seat_categories'] = seat_categories
        context.update(result)
        return context

    def form_valid(self, form):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        if form.is_valid():
            seat_category = get_object_or_404(SeatCategory, pk=form.cleaned_data.get('seat_category'))
            self.hall.create_or_update_seats(row=form.cleaned_data.get('row'),
                                             number_starts=form.cleaned_data.get('seat_starts'),
                                             number_ends=form.cleaned_data.get('seat_ends'),
                                             seat_category=seat_category
                                             )
        return redirect(reverse_lazy('myadmin:hall_activate', kwargs={'pk': self.hall.pk}))


