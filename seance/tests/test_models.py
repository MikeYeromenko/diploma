import datetime
from django.contrib.auth import get_user_model
from django.db.models import ProtectedError
from django.test import TestCase
from django.utils import timezone

from seance.models import Film, Hall, Seance, AdvUser, Purchase, Ticket, SeanceBase, SeatCategory, Seat, Price


class BaseInitial:
    def __init__(self):

        self.film_bond = Film.objects.get(title='James Bond')
        self.film_365 = Film.objects.get(title='365 Days')
        self.seat_category_base = SeatCategory.objects.get(name='base')
        self.hall_yellow = Hall.objects.get(name='Yellow')
        self.hall_red = Hall.objects.get(name='Red')
        self.seance_base_bond = SeanceBase.objects.get(film=self.film_bond)
        self.seance_bond_12 = Seance.objects.get(time_starts=datetime.time(12), seance_base=self.seance_base_bond)
        self.seance_bond_evening = Seance.objects.get(time_starts=datetime.time(19), seance_base=self.seance_base_bond)
        self.seance_bond_night = Seance.objects.get(time_starts=datetime.time(23, 50),
                                                    seance_base=self.seance_base_bond)

        self.admin = get_user_model().objects.create_superuser(
            username='admin', email='admin@somesite.com'
        )
        self.admin.set_password('password1')
        self.admin.save()

        self.film_terminator = Film.objects.create(
            title='Terminator',
            starring='Somebody and Arnold',
            director='DirectorT',
            duration=datetime.time(2, 10),
            description='some text....',
            admin=self.admin,
            is_active=False,
        )

        self.user = AdvUser.objects.create(
            username='test_user',
        )
        self.user.set_password('password1234')
        self.user.save()

        self.purchase = Purchase.objects.create(
            user=self.user
        )

        self.ticket1 = Ticket.objects.create(
            seance=self.seance_bond_night,
            date_seance=datetime.date.today() + datetime.timedelta(days=3),
            purchase=self.purchase,
            seat=self.hall_yellow.seats.all()[0],
            price=120
        )

        self.ticket2 = Ticket.objects.create(
            seance=self.seance_bond_night,
            date_seance=datetime.date.today() + datetime.timedelta(days=3),
            purchase=self.purchase,
            seat=self.hall_yellow.seats.all()[1],
            price=120
        )

        self.admin2 = get_user_model().objects.create_superuser(
            username='admin2', email='admin2@somesite.com'
        )
        self.admin2.set_password('password2')
        self.admin2.save()


class GeneralModelsTestCase(TestCase, BaseInitial):

    def setUp(self):
        BaseInitial.__init__(self)

    def test_advuser_model(self):
        """
        Tests that AdvUser object was created correctly and its features work as expected
        """
        self.assertEqual(self.user.username, 'test_user')
        self.assertEqual(self.user.wallet, 10000)

        # sum_money_spent property works correctly
        self.assertEqual(self.user.sum_money_spent, 240)

        # checks that user deleted softly
        user2 = AdvUser(
            username='user2'
        )
        user2.set_password('pass1234')
        user2.save()
        self.assertFalse(user2.was_deleted)
        user2.delete()
        self.assertTrue(user2.was_deleted)

    def test_film_model_basic(self):
        """
        Tests that Film object was created correctly
        """
        self.assertEqual(self.film_bond.title, 'James Bond')
        self.assertEqual(self.film_bond.starring, 'Daniel Craig and co')
        self.assertEqual(self.film_bond.director, 'Somebody')
        self.assertEqual(self.film_bond.description, 'A cool film about superman')
        self.assertEqual(self.film_bond.duration, datetime.time(1, 40))
        self.assertEqual(self.film_bond.admin.username, 'initial_admin')
        self.assertTrue(self.film_bond.is_active)

        # film was created no more then 2 minutes ago
        self.assertTrue(timezone.now() - datetime.timedelta(minutes=2) < self.film_bond.created_at < timezone.now())

    def test_film_str(self):
        """
        Test Film has __str__ that returns its title
        """
        self.assertEqual(self.film_bond.__str__(), 'James Bond')

    def test_hall_str(self):
        """
        Test Hall has __str__ that returns its name
        """
        self.assertEqual(self.hall_yellow.__str__(), 'Yellow')

    def test_seance_str(self):
        """
        Test Seance has __str__ that returns its 'Seance with Film.title'
        """
        self.assertEqual(self.seance_bond_12.__str__(), f'Seance with James Bond in 12:00:00-14:00:00 o\'clock')

    def test_hall_model_basic(self):
        """
        Tests that Hall object was created correctly
        """
        self.assertEqual(self.hall_yellow.name, 'Yellow')
        self.assertEqual(self.hall_yellow.quantity_seats, 100)
        self.assertEqual(self.hall_yellow.quantity_rows, 10)
        self.assertEqual(self.hall_yellow.admin.username, 'initial_admin')
        self.assertEqual(self.hall_yellow.description, 'Convenient place for your exciting journey')
        self.assertTrue(self.hall_yellow.is_active)

        # hall was created no more then 2 minutes ago
        self.assertTrue(timezone.now() - datetime.timedelta(minutes=2) < self.hall_yellow.created_at < timezone.now())

    def test_hall_activation(self):
        """Tests that hall activation method works correctly"""
        hall_test = Hall.objects.create(
            name='Test hall',
            quantity_seats=12,
            quantity_rows=3,
            description='some text',
            admin=self.admin2
        )
        # when creating new hall is active is False by default
        self.assertFalse(hall_test.is_active)

        self.assertFalse(hall_test.validate_all_seats_created())

        self.assertFalse(hall_test.get_seat_categories())

        result = hall_test.activate_hall()

        self.assertFalse(result['success'])
        self.assertFalse(result['created_seats'])
        self.assertEqual(result['uncreated_seats'], 12)

        for i in range(1, 4):
            hall_test.create_or_update_seats(seat_category=self.seat_category_base, row=i,
                                             number_starts=1, number_ends=4)

        self.assertEqual(Seat.objects.filter(hall=hall_test).count(), 12)
        result = hall_test.activate_hall()
        self.assertTrue(result['success'])
        self.assertTrue(hall_test.is_active)

    def test_seance_model_basic(self):
        """
        Tests that Seance object was created correctly
        """
        seance_test = Seance.objects.create(
            time_starts=datetime.time(8),
            description='some text',
            seance_base=self.seance_base_bond,
            admin=self.admin2
        )
        self.assertEqual(seance_test.time_starts, datetime.time(8))
        self.assertEqual(seance_test.time_ends, datetime.time(9, 50))
        self.assertEqual(seance_test.time_hall_free, datetime.time(10))
        self.assertEqual(seance_test.advertisements_duration, datetime.time(minute=10))
        self.assertEqual(seance_test.cleaning_duration, datetime.time(minute=10))
        self.assertEqual(seance_test.description, 'some text')
        self.assertFalse(seance_test.is_active)
        self.assertEqual(seance_test.seance_base.film.title, 'James Bond')
        self.assertEqual(seance_test.admin.username, 'admin2')

        # seance was created no more then 2 minutes ago
        self.assertTrue(timezone.now() - datetime.timedelta(minutes=2) < seance_test.created_at < timezone.now())

        self.assertFalse(seance_test.in_run)

        self.assertEqual(Seance.get_active_seances_for_day(datetime.date.today()), 6)

    def test_validate_seance_intersect(self):
        """
        Tests that Seance object was created correctly
        """
        seance_morning = Seance.objects.create(
            time_starts=datetime.time(1),
            description='some text',
            seance_base=self.seance_base_bond,
            admin=self.admin2
        )

        seance_day = Seance.objects.create(
            time_starts=datetime.time(20),
            description='some text',
            seance_base=self.seance_base_bond,
            admin=self.admin2
        )

        seance_night = Seance.objects.create(
            time_starts=datetime.time(22),
            cleaning_duration=datetime.time(minute=10),
            time_hall_free=datetime.time(23, 55),
            description='some text',
            seance_base=self.seance_base_bond,
            admin=self.admin2
        )

        intersects_morning = seance_morning.validate_seances_intersect(seance_exclude_pk=seance_morning.pk)
        self.assertEqual(intersects_morning[0].time_starts, datetime.time(23, 50))
        self.assertEqual(intersects_morning.count(), 1)

        intersects_day = seance_day.validate_seances_intersect(seance_exclude_pk=seance_day.pk)
        self.assertEqual(intersects_day[0].time_starts, datetime.time(19))
        self.assertEqual(intersects_day.count(), 1)

        intersects_night = seance_night.validate_seances_intersect(seance_exclude_pk=seance_night.pk)
        self.assertEqual(intersects_night[0].time_starts, datetime.time(23, 50))
        self.assertEqual(intersects_night.count(), 1)

    def test_seance_activation(self):
        """Tests that seance activation works correctly"""
        seance_test = Seance.objects.create(
            time_starts=datetime.time(8),
            description='some text',
            seance_base=self.seance_base_bond,
            admin=self.admin2
        )

        result = seance_test.activate()
        self.assertFalse(result['success'])
        self.assertEqual(len(result['errors_list']), 1)
        self.assertEqual(len(result['seat_categories']), 1)

        price_test = Price.objects.create(
            seance=seance_test,
            seat_category=self.seat_category_base,
            price=200
        )

        self.assertIsNotNone(Price.objects.get(pk=price_test.pk))
        result = seance_test.activate()
        self.assertTrue(result['success'])
        self.assertEqual(len(result['errors_list']), 0)
        self.assertEqual(len(result['seat_categories']), 0)
        self.assertTrue(seance_test.is_active)

    def test_seance_ordering(self):
        """Tests, that seances are ordered by price or by time correctly"""
        seances = Seance.objects.all()
        ordered_cheap_first = Seance.order_queryset('cheap', seances)
        self.assertEqual(ordered_cheap_first[0].prices.all()[0].price, 100)
        self.assertEqual(ordered_cheap_first[5].prices.all()[0].price, 200)

        ordered_expensive_first = Seance.order_queryset('expensive', seances)
        self.assertEqual(ordered_expensive_first[0].prices.all()[0].price, 200)
        self.assertEqual(ordered_expensive_first[5].prices.all()[0].price, 100)

        ordered_latest_first = Seance.order_queryset('latest', seances)
        self.assertEqual(ordered_latest_first[0].time_starts, datetime.time(23, 50))
        self.assertEqual(ordered_latest_first[5].time_starts, datetime.time(12))

        ordered_closest_first = Seance.order_queryset('closest', seances)
        self.assertEqual(ordered_closest_first[0].time_starts, datetime.time(12))
        self.assertEqual(ordered_closest_first[5].time_starts, datetime.time(23, 50))
