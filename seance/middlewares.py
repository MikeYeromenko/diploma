import datetime

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
        if request.user.is_authenticated and not request.user.is_superuser:
            last_activity = request.session.get('last_activity')        # we got it in type "str"
            last_activity = datetime.datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S.%f')
            if last_activity > datetime.datetime.now() - datetime.timedelta(minutes=5):
                request.session['last_activity'] = str(datetime.datetime.now())
            else:
                logout(request)
                messages.add_message(request, messages.INFO, _('More than 5 minutes inactive. '
                                                               'Please login again'))


def seance_context_processor(request):
    context = {}
    basket = request.session.get('basket', None)
    last_seance = request.session.get('last_seance', None)
    seance_date = request.session.get('seance_date', None)
    total_price = request.session.get('total_price', None)
    if basket:
        context['basket'] = basket
    if total_price:
        context['total_price'] = total_price
    if last_seance:
        context['last_seance'] = last_seance
    if seance_date:
        context['seance_date'] = seance_date
    return context

