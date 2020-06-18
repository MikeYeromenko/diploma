from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse

from seance.models import AdvUser, Hall, Seance, Film

admin.site.register(AdvUser)
admin.site.register(Hall)
admin.site.register(Seance)
admin.site.register(Film)
