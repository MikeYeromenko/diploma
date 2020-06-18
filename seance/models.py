import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from cinema.settings import DEFAULT_SUM_TO_WALLET


class AdvUser(AbstractUser):
    email = models.EmailField(verbose_name=_('email address'), blank=True, null=True)
    wallet = models.FloatField(blank=True, null=True, verbose_name=_('wallet'))
    was_deleted = models.BooleanField(default=False, verbose_name=_('was deleted?'))
    last_activity = models.DateTimeField(auto_now_add=True, blank=True, null=True,
                                         verbose_name=_('user\'s last activity was: '))

    def delete(self, *args, **kwargs):
        self.is_active = False
        self.was_deleted = True
        self.save()

    def save(self, *args, **kwargs):
        """Adds default sum into user's wallet at creation time"""
        if not self.id:
            self.wallet = DEFAULT_SUM_TO_WALLET
        return super().save(*args, **kwargs)


class Film(models.Model):
    title = models.CharField(max_length=100, verbose_name=_('title'))
    starring = models.CharField(max_length=200, verbose_name=_('starring'))
    director = models.CharField(max_length=100, verbose_name=_('director'))
    duration = models.TimeField(verbose_name=_('duration'))
    description = models.TextField(verbose_name=_('description'))
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=_('instance created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('instance updated at'))
    is_active = models.BooleanField(default=True, verbose_name=_('in run?'))
    admin = models.ForeignKey(AdvUser, on_delete=models.PROTECT, verbose_name=_('instance created by'))

    def __str__(self):
        return self.title


class Hall(models.Model):
    name = models.CharField(max_length=20, verbose_name=_('name'))
    quantity_seats = models.PositiveSmallIntegerField(default=0, verbose_name=_('how many seats?'))
    quantity_rows = models.PositiveSmallIntegerField(default=0, verbose_name=_('how many rows?'))
    description = models.TextField(verbose_name=_('description'))
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=_('instance created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('instance updated at'))
    is_active = models.BooleanField(default=True, verbose_name=_('in run?'))
    admin = models.ForeignKey(AdvUser, on_delete=models.PROTECT, verbose_name=_('instance created by'),
                              related_name='halls')

    def __str__(self):
        return self.name

    def validate_all_seats_created(self):
        """Validates, that all seats for hall were created"""
        pass


class SeatCategory(models.Model):
    name = models.CharField(max_length=20, verbose_name=_('category name'))
    price_list = models.ForeignKey('PriceList', on_delete=models.PROTECT,
                                   related_name='seat_categories', verbose_name=_('price list object'))
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=_('instance created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('instance updated at'))
    admin = models.ForeignKey(AdvUser, on_delete=models.PROTECT, verbose_name=_('instance created by'),
                              related_name='seat_categories')


class Seat(models.Model):
    hall = models.ForeignKey(Hall, on_delete=models.PROTECT, related_name='seats', verbose_name=_('hall'))
    seat_category = models.ForeignKey(SeatCategory, on_delete=models.PROTECT,
                                      related_name='seats', verbose_name=_('seat category'))
    number = models.PositiveSmallIntegerField(default=0, verbose_name=_('number of seat'))
    row = models.PositiveSmallIntegerField(default=0, verbose_name=_('number of row'))
    admin = models.ForeignKey(AdvUser, on_delete=models.PROTECT, verbose_name=_('instance created by'),
                              related_name='seats')


class SeanceBase(models.Model):
    film = models.ForeignKey(Film, on_delete=models.PROTECT, related_name='seances', verbose_name=_('films'))
    hall = models.ForeignKey(Hall, on_delete=models.PROTECT, related_name='seances', verbose_name=_('hall'))
    date_starts = models.DateField(verbose_name=_('starts'))
    date_ends = models.DateField(null=True, blank=True, verbose_name=_('ends'))
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=_('instance created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('instance updated at'))
    is_active = models.BooleanField(default=True, verbose_name=_('in run?'))
    admin_name = models.CharField(max_length=20, null=True, blank=True, verbose_name=_('creator: '))

    def save(self, *args, **kwargs):
        """
        Adds date_ends and if it wasn't added by admin.
        By default it is set to +15 days to date_starts of seance
        """
        if not self.id:
            if not self.date_ends:
                self.date_ends = self.get_date_ends()
        super().save(*args, **kwargs)

    def get_date_ends(self):
        """
        Counts the date of seance ending, adding 15 days to its start
        :return: date_ends of seance
        """
        return self.date_starts + datetime.timedelta(days=15)

    def __str__(self):
        return f'Base seance with {self.film.title}'


class PriceList(models.Model):
    title = models.CharField(max_length=20, verbose_name=_('title'))
    price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_('price per one seat'))
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=_('instance created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('instance updated at'))
    admin = models.ForeignKey(AdvUser, on_delete=models.PROTECT, verbose_name=_('instance created by'),
                              related_name='seance_bases')


class Seance(models.Model):
    time_starts = models.TimeField(verbose_name=_('starts at: '))
    time_ends = models.TimeField(null=True, blank=True, verbose_name=_('ends at: '))
    time_hall_free = models.TimeField(null=True, blank=True, verbose_name=_('ends at: '))
    advertisements_duration = models.TimeField(default=datetime.time(0, 10), verbose_name=_('adds duration: '))
    cleaning_duration = models.TimeField(default=datetime.time(0, 10), verbose_name=_('cleaning duration: '))
    description = models.TextField(verbose_name=_('description'))
    seance_base = models.ForeignKey(SeanceBase, on_delete=models.PROTECT, related_name='seances',
                                    verbose_name=_('base seance'))
    admin = models.ForeignKey(AdvUser, on_delete=models.PROTECT, verbose_name=_('instance created by'),
                              related_name='seances')

    class Meta:
        ordering = ('time_starts', )
        verbose_name = _('seance')
        verbose_name_plural = _('seances')

    def save(self, *args, **kwargs):
        """
        Adds time_ends if it wasn't added by admin
        """
        if not self.id:
            if not self.time_ends:
                self.time_ends = self.get_time_ends
            if not self.time_hall_free:
                self.time_hall_free = self.get_time_hall_free
        super().save(*args, **kwargs)

    @property
    def get_time_ends(self):
        """Count time_ends of seance"""
        minutes = (self.time_starts.minute + self.seance_base.film.duration.minute +
                   self.advertisements_duration.minute)

        # if value of minutes is more then 60, add integer part of it to hours
        hours = (self.time_starts.hour + self.seance_base.film.duration.hour +
                 self.advertisements_duration.hour + minutes // 60) % 24

        # fractional part will be less then 60, so we leave it as minutes value
        minutes %= 60
        time_ends = datetime.time(hour=hours, minute=minutes)
        return time_ends

    @property
    def get_time_hall_free(self):
        """Count time_hall_free of seance"""
        minutes = (self.time_ends.minute + self.cleaning_duration.minute)

        # if value of minutes is more then 60, add integer part of it to hours
        hours = (self.time_ends.hour + self.cleaning_duration.hour + minutes // 60) % 24

        # fractional part will be less then 60, so we leave it as minutes value
        minutes %= 60
        time_hall_free = datetime.time(hour=hours, minute=minutes)
        return time_hall_free

    @staticmethod
    def validate_seances_intersect(hall_id, date_starts, time_starts, date_ends, time_hall_free):
        """
        Validates, that given seance doesn't intersect with others in current hall in time
        To the time_ends of seance cleaning_duration is added, not to set next seance without
        giving time to clean hall
        :returns seances which intersect or empty queryset
        """
        seances = Seance.objects.filter(Q(seance_base__hall_id=hall_id) &
                                        Q(seance_base__date_starts__lte=date_ends) &
                                        Q(seance_base__date_ends__gte=date_starts) &
                                        Q(time_starts__lt=time_hall_free) &
                                        Q(time_hall_free__gt=time_starts))
        return seances


class Purchase(models.Model):
    user = models.ForeignKey(AdvUser, on_delete=models.PROTECT, related_name='purchases', verbose_name=_('user'))

    # maybe it has sense to set total_price as property without saving to database
    total_price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_('payed:'))
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=_('instance created at'))
    was_returned = models.BooleanField(default=False, verbose_name=_('was returned?'))
    returned_at = models.DateTimeField(blank=True, null=True, verbose_name=_('returned at'))

    def __str__(self):
        return f'{self.user.username} at {self.created_at}'


class Ticket(models.Model):
    seance = models.ForeignKey(Seance, on_delete=models.PROTECT, related_name='tickets', verbose_name=_('seance'))
    date_seance = models.DateField(default=datetime.date.today(), verbose_name=_('date of seance'))
    seat = models.ForeignKey(Seat, on_delete=models.PROTECT, related_name='tickets', verbose_name=_('seat'))
    purchase = models.ForeignKey(Purchase, on_delete=models.PROTECT, related_name='tickets', verbose_name=_('purchase'))
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=_('instance created at'))
    was_returned = models.BooleanField(default=False, verbose_name=_('was_returned?'))

    def __str__(self):
        return self.seance.__str__()


class Return:
    """For future goals))"""
    pass
