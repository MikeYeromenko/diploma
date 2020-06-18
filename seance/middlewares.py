from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import gettext_lazy as _


from seance.models import AdvUser


class LogoutIfInActiveMiddleware(MiddlewareMixin):
    @staticmethod
    def process_request(request):
        assert hasattr(request, 'user'), (
            'The LogoutIfNotActiveMiddleware middleware requires authentication middleware to be installed.'
        )
        if request.user.is_authenticated:
            if request.user.is_superuser or (request.user.last_activity >
                                             timezone.now() - timezone.timedelta(minutes=5)):
                user = get_object_or_404(AdvUser, pk=request.user.pk)
                user.last_activity = timezone.now()
                user.save()
                request.user.last_activity = user.last_activity
            else:
                logout(request)
                messages.add_message(request, messages.INFO, _('More than 5 minutes inactive. '
                                                               'Please login again'))


def seance_context_processor(request):
    context = {}
    basket = request.session.get('basket', None)
    last_seance = request.session.get('last_seance', None)
    if basket:
        context['basket'] = basket
        total_price = 0
        for key in basket:
            total_price += float(basket[key]['price'])
        context['total_price'] = total_price
    if last_seance:
        context['last_seance'] = last_seance
    return context

