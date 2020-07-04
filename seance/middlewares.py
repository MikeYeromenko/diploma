import datetime
from django.contrib import messages
from django.contrib.auth import logout
from django.utils.translation import gettext_lazy as _

from cinema.settings import INACTIVITY_NOT_SUPERUSER_LOGOUT_FOR as TIME_LOGOUT


class LogoutIfInActiveMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if request.user.is_authenticated and not request.user.is_superuser:
            last_activity = request.session.get('last_activity')        # we got it in type "str"
            if last_activity:
                last_activity = datetime.datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S.%f')
                if last_activity > datetime.datetime.now() - TIME_LOGOUT:
                    request.session['last_activity'] = str(datetime.datetime.now())
                else:
                    logout(request)
                    messages.add_message(request, messages.INFO, _(f'More than {str(TIME_LOGOUT)} minutes inactive. '
                                                                   'Please login again'))
            else:
                logout(request)
                messages.add_message(request, messages.INFO, _(f'Request does not contain last_activity, but must'))

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        if request.user.is_authenticated and not request.user.is_superuser:
            request.session['last_activity'] = str(datetime.datetime.now())
        return response


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

