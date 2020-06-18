from unittest.case import TestCase

from django.urls import resolve


class CinemaUrlsTestCase(TestCase):

    def test_root_url_uses_seance_list_view(self):
        """
        Tests that the root of the site resolves to the correct class-based View, and url has correct name
        """
        root = resolve('/')
        self.assertEqual(root.func.__name__, 'SeanceListView')
        self.assertEqual(root.url_name, 'index')

    def test_url_for_registration(self):
        """
        Test that url accounts/register/ exists, resolves to the correct cbv and has expected name
        """
        registration = resolve('/accounts/register/')
        self.assertEqual(registration.func.__name__, 'RegisterUserView')
        self.assertEqual(registration.url_name, 'register')

    def test_url_for_login(self):
        """
        Test that url accounts/login/ exists, resolves to the correct cbv and has expected name
        """
        login = resolve('/accounts/login/')
        self.assertEqual(login.func.__name__, 'UserLoginView')
        self.assertEqual(login.url_name, 'login')

    def test_url_for_logout(self):
        """
        Test that url accounts/login/ exists, resolves to the correct cbv and has expected name
        """
        logout = resolve('/accounts/logout/')
        self.assertEqual(logout.func.__name__, 'UserLogoutView')
        self.assertEqual(logout.url_name, 'logout')

    def test_url_for_profile(self):
        """
        Test that url accounts/profile/ exists, resolves to the correct cbv and has expected name
        """
        registration = resolve('/accounts/profile/')
        self.assertEqual(registration.func.__name__, 'UserProfileView')
        self.assertEqual(registration.url_name, 'profile')

    def test_url_for_basket(self):
        """
        Test that url accounts/profile/ exists, resolves to the correct cbv and has expected name
        """
        registration = resolve('/basket/')
        self.assertEqual(registration.func.__name__, 'BasketView')
        self.assertEqual(registration.url_name, 'basket')

    def test_url_for_seance_detail(self):
        """
        Test that url seance/<int:pk>/ exists, resolves to the correct cbv and has expected name
        """
        registration = resolve(f'/seance/{1}/')
        self.assertEqual(registration.func.__name__, 'SeanceDetailView')
        self.assertEqual(registration.url_name, 'seance_detail')

    def test_url_for_basket_redirect(self):
        """
        Test that url basket/redirect/ exists, resolves to the correct cbv and has expected name
        """
        registration = resolve('/basket/redirect/')
        self.assertEqual(registration.func.__name__, 'BasketRedirectView')
        self.assertEqual(registration.url_name, 'basket-redirect')