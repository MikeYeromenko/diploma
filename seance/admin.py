from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse

from seance.models import AdvUser, Hall, Seance, Film, Seat, SeatCategory, Price, SeanceBase, Ticket, Purchase


class AdvUserAdmin(admin.ModelAdmin):
    # list_display = ('__str__', 'is_activated', 'date_joined')
    # search_fields = ('username', 'email', 'first_name', 'last_name')
    # # list_filter = (NonActivatedFilter,)
    # fields = (('username', 'email'), ('first_name', 'last_name'),
    #           ('send_messages', 'is_active', 'is_activated'),
    #           ('is_staff', 'is_superuser'), 'groups', 'user_permissions',
    #           ('last_login', 'date_joined'))
    # readonly_fields = ('last_login', 'date_joined')
    # # actions = (send_activation_notifications,)
    pass


class FilmAdmin(admin.ModelAdmin):
    list_display = ('title', 'starring', 'director', 'admin', 'created_at')
    fields = (('title', 'starring', 'director'), ('duration', 'description'),
              'image', 'is_active', 'admin')
    # inlines = (AdditionalImageInline, )


admin.site.register(AdvUser, AdvUserAdmin)
admin.site.register(Hall)
admin.site.register(Seance)
admin.site.register(Film, FilmAdmin)
admin.site.register(Seat)
admin.site.register(SeatCategory)
admin.site.register(Price)
admin.site.register(SeanceBase)
admin.site.register(Ticket)
admin.site.register(Purchase)
