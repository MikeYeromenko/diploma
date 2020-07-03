import datetime
from django.contrib.auth import get_user_model
from django.db.models import ProtectedError
from django.test import TestCase
from django.utils import timezone

from seance.models import Film, Hall, Seance, AdvUser, Purchase, Ticket, SeanceBase


class BaseInitial:
    def __init__(self):

        self.film_bond = Film.objects.get(title='James Bond')
        self.film_365 = Film.objects.get(title='365 Days')
        self.hall_yellow = Hall.objects.get(name='Yellow')
        self.hall_red = Hall.objects.get(name='Red')
        self.seance_base_bond = SeanceBase.objects.get(film=self.film_bond)
        self.seance_bond_12 = Seance.objects.get(time_starts=datetime.time(12), seance_base=self.seance_base_bond)
        self.seance_bond_18 = Seance.objects.get(time_starts=datetime.time(19), seance_base=self.seance_base_bond)

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

        self.seance_base_365 = SeanceBase.objects.create(
            film=self.film_365,
            hall=self.hall_red,
            date_starts=datetime.date.today()
        )

        self.seance_365_12 = Seance.objects.create(
            time_starts=datetime.time(12),
            description='Some text about why this seance is the best',
            seance_base=self.seance_base_365,
            admin=self.admin,
        )

        self.seance_365_14 = Seance.objects.create(
            time_starts=datetime.time(14, 30),
            description='Some text about why this seance is the best',
            seance_base=self.seance_base_365,
            admin=self.admin,
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
            seance=self.seance_bond_12,
            date_seance=datetime.date.today() + datetime.timedelta(days=3),
            purchase=self.purchase,
            seat=self.hall_yellow.seats.all()[0],
            price=100
        )

        self.ticket2 = Ticket.objects.create(
            seance=self.seance_bond_18,
            date_seance=datetime.date.today() + datetime.timedelta(days=3),
            purchase=self.purchase,
            seat=self.hall_yellow.seats.all()[1],
            price=180
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
        self.assertEqual(self.user.sum_money_spent, 280)

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

    def test_seance_model_basic(self):
        """
        Tests that Seance object was created correctly
        """
        self.assertEqual(self.seance_bond_12.time_starts, datetime.time(12))
        self.assertEqual(self.seance_bond_12.time_ends, datetime.time(14))
        self.assertEqual(self.seance_bond_12.time_hall_free, datetime.time(14, 10))
        self.assertEqual(self.seance_bond_12.advertisements_duration, datetime.time(minute=10))
        self.assertEqual(self.seance_bond_12.cleaning_duration, datetime.time(minute=10))
        self.assertEqual(self.seance_bond_12.description, 'For those who have long dinner time)')
        self.assertTrue(self.seance_bond_12.is_active)
        self.assertEqual(self.seance_bond_12.admin.username, 'initial_admin')

        # seance was created no more then 2 minutes ago
        self.assertTrue(timezone.now() - datetime.timedelta(minutes=2) < self.seance_bond_12.created_at < timezone.now())
