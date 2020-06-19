from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin
from django.views.generic import TemplateView, DetailView, ListView

from seance.models import Film


class IsStaffRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated and is_staff."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated and not request.user.is_staff:
            messages.add_message(request, messages.INFO, f'This page is for staff only. Enter your credentials '
                                                         f'to confirm your staff status')
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class AdminMainView(IsStaffRequiredMixin, TemplateView):
    template_name = 'seance/admin/admin_page.html'


class FilmDetailView(DetailView):
    model = Film


class FilmListView(ListView):
    model = Film
    paginate_by = 30
