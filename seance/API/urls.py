from django.urls import path, include
from rest_framework import routers

from seance.API import resources

app_name = 'api'

router = routers.DefaultRouter()
router.register('seance', resources.SeanceViewSet, basename='seance')
router.register('seance_base', resources.SeanceBaseViewSet, basename='seance_base')
router.register('hall', resources.HallViewSet, basename='hall')
router.register('film', resources.FilmViewSet, basename='film')
router.register('user', resources.AdvUserViewSet, basename='user')
router.register('price', resources.PriceViewSet, basename='price')
router.register('seat_category', resources.SeatCategoryViewSet, basename='seat_category')
router.register('purchase', resources.PurchaseViewSet, basename='purchase')

urlpatterns = [
    path('rest-auth/registration/', include('rest_auth.registration.urls')),
    path('rest-auth/', include('rest_auth.urls')),
    path('basket/cancel/', resources.BasketCancelAPIView.as_view(), name='basket-cancel'),
    path('basket/add/', resources.BasketAddAPIView.as_view(), name='basket-add'),
    path('basket/', resources.BasketAPIView.as_view(), name='basket'),
    path('', include(router.urls)),
]
