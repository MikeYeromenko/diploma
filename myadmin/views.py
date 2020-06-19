from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, DetailView, ListView, UpdateView, CreateView, DeleteView

from myadmin import forms
from myadmin.forms import FilmUpdateCreateForm
from seance.models import Film, AdvUser


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
    form_class = forms.FilmUpdateCreateForm
    success_url = reverse_lazy('myadmin:film_list')

    def post(self, request, *args, **kwargs):
        """Adds admin, who edit film, to admin field"""
        film = get_object_or_404(Film, pk=kwargs.get('pk'))
        film.admin = get_object_or_404(AdvUser, pk=request.user.pk)
        form = FilmUpdateCreateForm(request.POST, instance=film)
        if form.is_valid():
            film = form.save()
            messages.add_message(request, messages.SUCCESS, _('Film was edited successfully'))
            return redirect(self.success_url)
        return render(request, 'myadmin/films/film_update_form.html', {'form': form})


class FilmListView(IsStaffRequiredMixin, ListView):
    model = Film
    paginate_by = 30
    template_name = 'myadmin/films/film_list.html'

    def get_queryset(self):
        """Filters only films with is_active = True status"""
        return Film.objects.filter(is_active=True)


class FilmCreateView(IsStaffRequiredMixin, CreateView):
    model = Film
    form_class = forms.FilmUpdateCreateForm
    success_url = reverse_lazy('myadmin:film_list')
    template_name = 'myadmin/films/film_create_form.html'

    def post(self, request, *args, **kwargs):
        """Adds admin, who creates film, to admin field"""
        admin = get_object_or_404(AdvUser, pk=request.user.pk)
        form = FilmUpdateCreateForm(request.POST)
        if form.is_valid():
            film = form.save(commit=False)
            film.admin = admin
            film.save()
            messages.add_message(request, messages.SUCCESS, _('Film was created successfully'))
            return redirect(self.success_url)
        return render(request, 'myadmin/films/film_create_form.html', {'form': form})


class FilmDeleteView(DeleteView):
    model = Film
    success_url = reverse_lazy('myadmin:film_list')
    template_name = 'myadmin/films/film_confirm_delete.html'
