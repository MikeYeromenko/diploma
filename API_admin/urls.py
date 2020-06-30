from django.urls import path, include
from rest_framework import routers

from API_admin import resources

app_name = 'api_admin'


router = routers.DefaultRouter()
router.register('seat_category', resources.SeatCategoryViewSet, basename='seat_category')
router.register('price', resources.SeatCategoryViewSet, basename='price')


urlpatterns = [
    path('', include(router.urls)),
]
