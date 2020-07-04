from celery import shared_task
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from cinema.settings import ALLOWED_HOSTS
from seance.models import AdvUser, Purchase


@shared_task
def send_tickets_with_celery(user_pk, purchase_pk):
    user = get_object_or_404(AdvUser, pk=user_pk)
    purchase = get_object_or_404(Purchase, pk=purchase_pk)
    if ALLOWED_HOSTS:
        host = f'http://{ALLOWED_HOSTS[0]}'
    else:
        host = f'http://localhost:8000'
    context = {'user': user, 'host': host, 'purchase': purchase}
    subject = render_to_string('email/purchase_letter_subject.txt', context)
    body_text = render_to_string('email/purchase_letter_body.txt', context)
    user.email_user(subject, body_text)

