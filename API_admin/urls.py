from django.urls import path, include
from rest_framework import routers

from API_admin import resources

app_name = 'api_admin'


router = routers.DefaultRouter()
router.register('seat_category', resources.SeatCategoryViewSetMixin, basename='seat_category')
router.register('price', resources.PriceViewSet, basename='price')
router.register('film', resources.FilmViewSetMixin, basename='film')
router.register('hall', resources.HallViewSetMixin, basename='hall')
router.register('seance_base', resources.SeanceBaseViewSet, basename='seance_base')
router.register('seance', resources.SeanceViewSetMixin, basename='seance')


urlpatterns = [
    # path('image-update/film/<int:pk>/', resources.ImageUploadAPIView.as_view(), name='upload-image'),
    path('seance/activate/<int:pk>/', resources.SeanceActivateView.as_view(), name='activate_seance'),
    path('hall/<int:pk>/create-seats/', resources.CreateSeatsAPIView.as_view(), name='create_seats'),
    path('', include(router.urls)),
]
