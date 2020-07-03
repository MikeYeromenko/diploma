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
        profile = resolve('/accounts/profile/')
        self.assertEqual(profile.func.__name__, 'UserProfileView')
        self.assertEqual(profile.url_name, 'profile')

    def test_url_for_basket(self):
        """
        Test that url accounts/profile/ exists, resolves to the correct cbv and has expected name
        """
        basket = resolve('/basket/')
        self.assertEqual(basket.func.__name__, 'BasketView')
        self.assertEqual(basket.url_name, 'basket')

    def test_url_for_seance_detail(self):
        """
        Test that url seance/<int:pk>/ exists, resolves to the correct cbv and has expected name
        """
        detail = resolve(f'/seance/{1}/')
        self.assertEqual(detail.func.__name__, 'SeanceDetailView')
        self.assertEqual(detail.url_name, 'seance_detail')
        self.assertEqual(detail.kwargs.get('pk'), 1)

    def test_url_for_basket_redirect(self):
        """
        Test that url basket/redirect/ exists, resolves to the correct cbv and has expected name
        """
        basket = resolve('/basket/redirect/')
        self.assertEqual(basket.func.__name__, 'BasketRedirectView')
        self.assertEqual(basket.url_name, 'basket-redirect')

    def test_url_for_basket_cancel(self):
        """
        Test that url basket/cancel/ exists, resolves to the correct cbv and has expected name
        """
        basket = resolve('/basket/cancel/')
        self.assertEqual(basket.func.__name__, 'BasketCancelView')
        self.assertEqual(basket.url_name, 'basket-cancel')

    def test_url_for_buying(self):
        """
        Test that url buy/ exists, resolves to the correct cbv and has expected name
        """
        url = resolve('/buy/')
        self.assertEqual(url.func.__name__, 'PurchaseCreateView')
        self.assertEqual(url.url_name, 'buy')

    def test_url_for_purchases(self):
        """
        Test that url my_tickets/ exists, resolves to the correct cbv and has expected name
        """
        url = resolve('/my_tickets/')
        self.assertEqual(url.func.__name__, 'PurchaseListView')
        self.assertEqual(url.url_name, 'my_tickets')


# Tests for user's API

    def test_url_for_api_registration(self):
        """
        Test that url api/rest-auth/registration/ exists, resolves to the correct controller and has expected name
        """
        url = resolve('/api/rest-auth/registration/')
        self.assertEqual(url.func.__name__, 'RegisterView')
        self.assertEqual(url.url_name, 'rest_register')

    def test_url_for_api_auth(self):
        """
        Test that urls for login and logout exist, resolve to the correct controller and have expected name
        """
        url_login = resolve('/api/rest-auth/login/')
        self.assertEqual(url_login.func.__name__, 'LoginView')
        self.assertEqual(url_login.url_name, 'rest_login')

        url_logout = resolve('/api/rest-auth/logout/')
        self.assertEqual(url_logout.func.__name__, 'LogoutView')
        self.assertEqual(url_logout.url_name, 'rest_logout')

    def test_url_for_api_basket_add(self):
        """
        Test that url api/basket/add/ exists, resolves to the correct controller and has expected name
        """
        url = resolve('/api/basket/add/')
        self.assertEqual(url.func.__name__, 'BasketAddAPIView')
        self.assertEqual(url.url_name, 'basket-add')

    def test_url_for_api_basket_cancel(self):
        """
        Test that url api/basket/cancel/ exists, resolves to the correct controller and has expected name
        """
        url = resolve('/api/basket/cancel/')
        self.assertEqual(url.func.__name__, 'BasketCancelAPIView')
        self.assertEqual(url.url_name, 'basket-cancel')

    def test_url_for_api_basket(self):
        """
        Test that url api/basket/ exists, resolves to the correct controller and has expected name
        """
        url = resolve('/api/basket/')
        self.assertEqual(url.func.__name__, 'BasketAPIView')
        self.assertEqual(url.url_name, 'basket')

    def test_url_for_api_seance(self):
        """
        Test that urls for seance model exists, resolve to the correct controller and have expected name
        """
        url_list = resolve('/api/seance/')
        self.assertEqual(url_list.func.__name__, 'SeanceViewSet')
        self.assertEqual(url_list.url_name, 'seance-list')

        url_detail = resolve('/api/seance/1/')
        self.assertEqual(url_detail.func.__name__, 'SeanceViewSet')
        self.assertEqual(url_detail.url_name, 'seance-detail')
        self.assertEqual(url_detail.kwargs.get('pk'), '1')

    def test_url_for_api_seance_base(self):
        """
        Test that urls for seance_base model exists, resolve to the correct controller and have expected name
        """
        url_list = resolve('/api/seance_base/')
        self.assertEqual(url_list.func.__name__, 'SeanceBaseViewSet')
        self.assertEqual(url_list.url_name, 'seance_base-list')

        url_detail = resolve('/api/seance_base/1/')
        self.assertEqual(url_detail.func.__name__, 'SeanceBaseViewSet')
        self.assertEqual(url_detail.url_name, 'seance_base-detail')
        self.assertEqual(url_detail.kwargs.get('pk'), '1')

    def test_url_for_api_hall(self):
        """
        Test that urls for hall model exists, resolve to the correct controller and have expected name
        """
        url_list = resolve('/api/hall/')
        self.assertEqual(url_list.func.__name__, 'HallViewSet')
        self.assertEqual(url_list.url_name, 'hall-list')

        url_detail = resolve('/api/hall/1/')
        self.assertEqual(url_detail.func.__name__, 'HallViewSet')
        self.assertEqual(url_detail.url_name, 'hall-detail')
        self.assertEqual(url_detail.kwargs.get('pk'), '1')

    def test_url_for_api_film(self):
        """
        Test that urls for film model exists, resolve to the correct controller and have expected name
        """
        url_list = resolve('/api/film/')
        self.assertEqual(url_list.func.__name__, 'FilmViewSet')
        self.assertEqual(url_list.url_name, 'film-list')

        url_detail = resolve('/api/film/1/')
        self.assertEqual(url_detail.func.__name__, 'FilmViewSet')
        self.assertEqual(url_detail.url_name, 'film-detail')
        self.assertEqual(url_detail.kwargs.get('pk'), '1')

    def test_url_for_api_user(self):
        """
        Test that urls for user model exists, resolve to the correct controller and have expected name
        """

        url_detail = resolve('/api/user/1/')
        self.assertEqual(url_detail.func.__name__, 'AdvUserViewSet')
        self.assertEqual(url_detail.url_name, 'user-detail')
        self.assertEqual(url_detail.kwargs.get('pk'), '1')

    def test_url_for_api_price(self):
        """
        Test that urls for price model exists, resolve to the correct controller and have expected name
        """
        url_list = resolve('/api/price/')
        self.assertEqual(url_list.func.__name__, 'PriceViewSet')
        self.assertEqual(url_list.url_name, 'price-list')

        url_detail = resolve('/api/price/1/')
        self.assertEqual(url_detail.func.__name__, 'PriceViewSet')
        self.assertEqual(url_detail.url_name, 'price-detail')
        self.assertEqual(url_detail.kwargs.get('pk'), '1')

    def test_url_for_api_seat_category(self):
        """
        Test that urls for seat_category model exists, resolve to the correct controller and have expected name
        """

        url_detail = resolve('/api/seat_category/1/')
        self.assertEqual(url_detail.func.__name__, 'SeatCategoryViewSet')
        self.assertEqual(url_detail.url_name, 'seat_category-detail')
        self.assertEqual(url_detail.kwargs.get('pk'), '1')

    def test_url_for_api_purchase(self):
        """
        Test that urls for purchase model exists, resolve to the correct controller and have expected name
        """
        url_list = resolve('/api/purchase/')
        self.assertEqual(url_list.func.__name__, 'PurchaseViewSet')
        self.assertEqual(url_list.url_name, 'purchase-list')




