import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from django.shortcuts import get_object_or_404
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

    def __str__(self):
        return self.username


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

    class Meta:
        ordering = ('-updated_at', )


class Hall(models.Model):
    name = models.CharField(max_length=20, verbose_name=_('name'))
    quantity_seats = models.PositiveSmallIntegerField(default=0, verbose_name=_('how many seats?'))
    quantity_rows = models.PositiveSmallIntegerField(default=0, verbose_name=_('how many rows?'))
    description = models.TextField(verbose_name=_('description'))
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=_('instance created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('instance updated at'))
    is_active = models.BooleanField(default=False, verbose_name=_('in run?'))
    admin = models.ForeignKey(AdvUser, on_delete=models.PROTECT, verbose_name=_('instance created by'),
                              related_name='halls')

    class Meta:
        ordering = ('-updated_at', )

    def __str__(self):
        return self.name

    def validate_all_seats_created(self):
        """Validates, that all seats for hall were created. If all seats created - returns True"""
        return not bool(self.quantity_seats-self.seats.count())

    def create_seats(self, row, number_start, number_end, admin, seat_category):
        """Creates seats in hall corresponding to given by admin info"""
        for number in range(number_start, number_end + 1):
            Seat.objects.create(
                hall=Hall.objects.get(name=self.name),
                seat_category=seat_category,
                number=number,
                row=row,
                admin=admin
            )


class SeatCategory(models.Model):
    name = models.CharField(max_length=20, verbose_name=_('category name'))
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=_('instance created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('instance updated at'))
    admin = models.ForeignKey(AdvUser, on_delete=models.PROTECT, verbose_name=_('instance created by'),
                              related_name='seat_categories')

    class Meta:
        ordering = ('-updated_at',)

    def __str__(self):
        return self.name


class Seat(models.Model):
    hall = models.ForeignKey(Hall, on_delete=models.PROTECT, related_name='seats', verbose_name=_('hall'))
    seat_category = models.ForeignKey(SeatCategory, on_delete=models.PROTECT,
                                      related_name='seats', verbose_name=_('seat category'))
    number = models.PositiveSmallIntegerField(default=0, verbose_name=_('number of seat'))
    row = models.PositiveSmallIntegerField(default=0, verbose_name=_('number of row'))

    class Meta:
        unique_together = ('row', 'number', 'hall')
        verbose_name = _('seat')
        verbose_name_plural = _('seats')
        ordering = ('row', 'number')


class SeanceBase(models.Model):
    film = models.ForeignKey(Film, on_delete=models.PROTECT, related_name='seances', verbose_name=_('film'))
    hall = models.ForeignKey(Hall, on_delete=models.PROTECT, related_name='seances', verbose_name=_('hall'))
    date_starts = models.DateField(verbose_name=_('starts'))
    date_ends = models.DateField(null=True, blank=True, verbose_name=_('ends'))
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=_('instance created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('instance updated at'))

    class Meta:
        ordering = ('-updated_at', )

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
        return f'Base seance with {self.film.title} in dates: {self.date_starts} - {self.date_ends}'

    @staticmethod
    def validate_seances_base_intersect(date_starts, date_ends, film, hall, sb_pk_exclude=None):
        """Validates, that SeanceBase doesn't intersect with others seances base with this film in this hall"""
        seance_bases = SeanceBase.objects.filter(Q(film=film) & Q(hall=hall) &
                                                 Q(date_starts__lte=date_ends) &
                                                 Q(date_ends__gte=date_starts))
        if sb_pk_exclude:
            seance_bases = seance_bases.exclude(pk=sb_pk_exclude)
        return seance_bases


class Price(models.Model):
    seance = models.ForeignKey('Seance', on_delete=models.PROTECT, related_name='prices', verbose_name=_('seance'))
    seat_category = models.ForeignKey(SeatCategory, on_delete=models.PROTECT,
                                      related_name='prices', verbose_name=_('seat category'))
    price = models.FloatField(verbose_name=_('price per one seat'))
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=_('instance created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('instance updated at'))

    class Meta:
        ordering = ('-updated_at', )
        unique_together = ('seance', 'seat_category')

    def __str__(self):
        return f'price for {self.seat_category} in {self.seance}'


class Seance(models.Model):
    time_starts = models.TimeField(verbose_name=_('starts at: '))
    time_ends = models.TimeField(null=True, blank=True, verbose_name=_('ends at: '))
    time_hall_free = models.TimeField(null=True, blank=True, verbose_name=_('hall free at: '))
    advertisements_duration = models.TimeField(null=True, blank=True, default=datetime.time(0, 10),
                                               verbose_name=_('advertisements duration: '))
    cleaning_duration = models.TimeField(null=True, blank=True, default=datetime.time(0, 10),
                                         verbose_name=_('cleaning duration: '))
    description = models.TextField(verbose_name=_('description'))
    seance_base = models.ForeignKey(SeanceBase, on_delete=models.PROTECT, related_name='seances',
                                    verbose_name=_('base seance'))
    is_active = models.BooleanField(default=False, verbose_name=_('in run?'))
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
            if not self.advertisements_duration:
                self.advertisements_duration = datetime.time(0, 10)
            if not self.cleaning_duration:
                self.cleaning_duration = datetime.time(0, 10)
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

    def get_sold_tickets(self, date_starts, date_ends):
        """returns tickets sold on the seance"""
        tickets = self.tickets.filter(Q(date_seance__gte=date_starts) & Q(date_seance__lte=date_ends))
        return tickets

    def __str__(self):
        return f'Seance with {self.seance_base.film.title} in {self.time_starts}-{self.time_ends} o\'clock'


class Purchase(models.Model):
    user = models.ForeignKey(AdvUser, on_delete=models.PROTECT, related_name='purchases', verbose_name=_('user'))

    # maybe it has sense to set total_price as property without saving to database
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=_('instance created at'))
    was_returned = models.BooleanField(default=False, verbose_name=_('was returned?'))
    returned_at = models.DateTimeField(blank=True, null=True, verbose_name=_('returned at'))

    def __str__(self):
        return f'{self.user.username} at {self.created_at}'

    class Meta:
        ordering = ('-created_at', )

    @property
    def total_price(self):
        """Counts total price of purchase"""
        total_price = 0
        for price in self.tickets.values('price'):
            total_price += price.get('price')
        return total_price


class Ticket(models.Model):
    seance = models.ForeignKey(Seance, on_delete=models.PROTECT, related_name='tickets', verbose_name=_('seance'))
    date_seance = models.DateField(verbose_name=_('date of seance'))
    seat = models.ForeignKey(Seat, on_delete=models.PROTECT, related_name='tickets', verbose_name=_('seat'))
    price = models.FloatField(verbose_name=_('price'))
    purchase = models.ForeignKey(Purchase, on_delete=models.PROTECT, related_name='tickets', verbose_name=_('purchase'))
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=_('instance created at'))
    was_returned = models.BooleanField(default=False, verbose_name=_('was_returned?'))

    def __str__(self):
        return f'ticket on {self.seance.__str__()} on {self.date_seance}'

    def save(self, *args, **kwargs):
        if not self.id:
            if not self.date_seance:
                self.date_seance = datetime.date.today()
        return super().save(*args, **kwargs)

    class Meta:
        unique_together = ('seance', 'date_seance', 'seat')


class Return:
    """For future goals))"""
    pass
