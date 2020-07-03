import datetime

from django.db.models import Q
from django.test import TestCase
from django.urls import reverse_lazy
from django.utils import timezone

from seance.models import Seance, Hall, SeanceBase
from seance.tests.test_models import BaseInitial


class SeanceListViewTestCase(TestCase, BaseInitial):

    def setUp(self):
        BaseInitial.__init__(self)
        self.create_seance_objects_for_tests()

    def create_seance_objects_for_tests(self):
        self.seance_base_365 = SeanceBase.objects.get(film=self.film_365)
        self.seance_365_12 = Seance.objects.get(seance_base=self.seance_base_365, time_starts=datetime.time(12))
        self.seance_365_evening = Seance.objects.get(seance_base=self.seance_base_365, time_starts=datetime.time(19))
        self.seance_365_night = Seance.objects.get(seance_base=self.seance_base_365, time_starts=datetime.time(23, 50))

        Hall.objects.create(
            name='Green',
            quantity_rows=15,
            quantity_seats=20,
            is_active=True,
            description='Some text about why this hall is the best',
            admin=self.admin
        )

    def test_basic(self):
        """
        Tests that SeanceListView returns a 200 response, uses correct template and has correct context
        """
        with self.assertTemplateUsed('seance/index.html'):
            response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        quantity = Seance.objects.filter(Q(seance_base__date_starts__lte=datetime.date.today()) &
                                         Q(seance_base__date_ends__gte=datetime.date.today()) &
                                         Q(time_starts__gt=timezone.now()) & Q(is_active=True)).count()

        self.assertEqual(len(response.context['seance_list']), quantity)

        self.assertEqual(response.context['seance_list'][0].seance_base.film.title, 'James Bond')


class AuthenticationTestCase(TestCase, BaseInitial):

    def setUp(self):
        BaseInitial.__init__(self)

    def test_basic_registration(self):
        """
        Tests that RegisterUserView returns a 200 response, uses correct template
        """
        with self.assertTemplateUsed('registration/register_user.html'):
            response = self.client.get(reverse_lazy('seance:register'))
        self.assertEqual(response.status_code, 200)

    def test_deep_registration(self):
        """
        Test RegistrationUserView deeply, with different types of errors
        """
        # username exists
        existed_username = {'username': self.admin.username, 'password1': 'password4321',
                            'password2': 'password4321'}
        response = self.client.post(reverse_lazy('seance:register'), data=existed_username)
        page = response.content.decode()
        self.assertInHTML('<li>A user with that username already exists.</li>', page)

        # common password
        common_password = {'username': 'user1', 'password1': 'pass1234',
                           'password2': 'pass1234'}
        response = self.client.post(reverse_lazy('seance:register'), data=common_password)
        page = response.content.decode()
        self.assertInHTML('<li>This password is too common.</li>', page)

        # password has less than 8 symbols
        short_password = {'username': 'user1', 'password1': 'pass',
                          'password2': 'pass'}
        response = self.client.post(reverse_lazy('seance:register'), data=short_password)
        page = response.content.decode()
        self.assertInHTML('<li>Ensure this value has at least 8 characters (it has 4).</li>', page)

        # password1 and password2 mismatch
        password_mismatch = {'username': 'user1', 'password1': 'pass9513',
                             'password2': 'pass9531'}
        response = self.client.post(reverse_lazy('seance:register'), data=password_mismatch)
        page = response.content.decode()
        self.assertInHTML('<li>passwords mismatch</li>', page)

        # password2 didn't fill in
        password2_not_set = {'username': 'user1', 'password1': 'pass9513',
                             'password2': ''}
        response = self.client.post(reverse_lazy('seance:register'), data=password2_not_set)
        page = response.content.decode()
        self.assertInHTML('<li>This field is required.</li>', page)

        # username short
        username_short = {'username': 'u1', 'password1': 'pass9513',
                          'password2': 'pass9513'}
        response = self.client.post(reverse_lazy('seance:register'), data=username_short)
        page = response.content.decode()
        # post was't sent by browser because username too short
        self.assertFalse(page)

    def test_deep_login(self):
        """
        Tests UserLoginView deeply, with different kinds of errors
        """
        # after successful login user is redirected
        correct_data = {'username': self.admin.username, 'password': 'password1'}
        response = self.client.post(reverse_lazy('seance:login'), data=correct_data)
        self.assertRedirects(response, reverse_lazy('seance:profile'))

        # login with correct data when user is already logged in
        correct_data = {'username': self.admin.username, 'password': 'password1'}
        response = self.client.post(reverse_lazy('seance:login'), data=correct_data)
        page = response.content.decode()
        # post was't sent by browser because user with that credentials is logged in
        self.assertFalse(page)

        self.client.get(reverse_lazy('seance:logout'))

        incorrect_username = {'username': 'wrong', 'password': 'password1'}
        response = self.client.post('/accounts/login/', data=incorrect_username)
        page = response.content.decode()
        self.assertInHTML('<li>Please enter a correct username and password. '
                          'Note that both fields may be case-sensitive.</li>', page)

        incorrect_password = {'username': 'admin', 'password': 'wrong'}
        response = self.client.post(reverse_lazy('seance:login'), data=incorrect_password)
        page = response.content.decode()
        self.assertInHTML('<li>Please enter a correct username and password. '
                          'Note that both fields may be case-sensitive.</li>', page)

        empty_data = {'username': '', 'password': ''}
        response = self.client.post(reverse_lazy('seance:login'), data=empty_data)
        page = response.content.decode()
        self.assertInHTML('<li>This field is required.</li>', page)

    def test_user_detail_view(self):
        """
        Tests that UserDetailView returns a 200 response, uses correct template
        """
        with self.assertTemplateUsed('seance/profile.html'):
            response = self.client.get(reverse_lazy('seance:profile'))
        self.assertEqual(response.status_code, 200)

    def test_basic_login_logout(self):
        """
        Tests that UserLoginView and UserLogoutView returns a 200 response, uses correct template
        After user logged in he is able to logout
        """
        # login
        with self.assertTemplateUsed('registration/login.html'):
            response = self.client.get(reverse_lazy('seance:login'))
        self.assertEqual(response.status_code, 200)

        # logout
        with self.assertTemplateUsed('registration/logged_out.html'):
            response = self.client.get(reverse_lazy('seance:logout'))
        self.assertEqual(response.status_code, 200)
        page = response.content.decode()
        self.assertInHTML('<h4>You have logged out successfully</h4>', page)


class BasketViewTestCase(TestCase, BaseInitial):

    def setUp(self):
        BaseInitial.__init__(self)

    def test_basket_view(self):
        """
        Test that basket view works correctly
        """
        # only for logged in users
        response = self.client.get(reverse_lazy('seance:basket'))
        self.assertEqual(response.status_code, 302)

        # login user
        self.client.login(username=self.user.username, password='password1234')
        with self.assertTemplateUsed('seance/basket.html'):
            response = self.client.get(reverse_lazy('seance:basket'))
        self.assertEqual(response.status_code, 200)

    def basket_redirect_view(self):
        """
        Test that basket redirect view works correctly
        """
        # only for logged in users
        response = self.client.get(reverse_lazy('seance:basket-redirect'))
        self.assertEqual(response.status_code, 302)

        # login user
        self.client.login(username=self.user.username, password='password1234')
        response = self.client.get(reverse_lazy('seance:basket-redirect'))
        self.assertEqual(response.status_code, 302)

    def test_basket_is_in_context(self):
        """Test that 'basket' was added to context"""
        # seat_pk, seance_pk, seance_date, row, number

        self.client.login(username='test_user', password='password1234')

        self.client.get(reverse_lazy('seance:basket-redirect'), data={
            'row': 1,
            'seat_pk': 1,
            'seance': self.seance_bond_night.pk,
            'seance_date': datetime.date.today(),
            'number': 2
        })

        response = self.client.get(reverse_lazy('seance:basket'))

        self.assertIsNotNone(response.context.get('basket'))


class SeanceDetailViewTestCase(TestCase, BaseInitial):

    def setUp(self):
        BaseInitial.__init__(self)

    def test_basic(self):
        """
        Test that basket view works correctly
        """
        with self.assertTemplateUsed('seance/seance_detail.html'):
            response = self.client.get(reverse_lazy('seance:seance_detail', kwargs={'pk': self.seance_bond_12.pk}))
        self.assertEqual(response.status_code, 200)

