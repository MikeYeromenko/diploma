import datetime
from os.path import splitext
import re


from django.forms import fields
from django.forms import ValidationError
from django.template.loader import render_to_string
from django.utils.encoding import smart_text

from cinema.settings import ALLOWED_HOSTS


def get_timestamp_path(instance, filename):
    return f'{datetime.datetime.now().timestamp()}{splitext(filename)[0][:10]}'


class HexColorField(fields.Field):
    default_error_messages = {
        'hex_error': u'This is an invalid color code. It must be a html hex color code e.g. #000000'
    }

    def clean(self, value):

        super(HexColorField, self).clean(value)

        if value in fields.EMPTY_VALUES:
            return u''

        value = smart_text(value)
        value_length = len(value)

        if value_length != 7 or not re.match(r'^\#([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$', value):
            raise ValidationError(self.error_messages['hex_error'])

        return value

    def widget_attrs(self, widget):
        if isinstance(widget, (fields.TextInput)):
            return {'maxlength': str(7)}


def send_tickets(user, purchase):
    if ALLOWED_HOSTS:
        host = f'http://{ALLOWED_HOSTS[0]}'
    else:
        host = f'http://localhost:8000'
    context = {'user': user, 'host': host, 'purchase': purchase}
    subject = render_to_string('email/purchase_letter_subject.txt', context)
    body_text = render_to_string('email/purchase_letter_body.txt', context)
    user.email_user(subject, body_text)
