from django.urls import path, include
from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view

from API_admin import resources

app_name = 'api_admin'
API_TITLE = 'Cinema admin'
schema_view = get_swagger_view(title=API_TITLE)


router = routers.DefaultRouter()
router.register('seat_category', resources.SeatCategoryViewSet, basename='seat_category')
router.register('price', resources.PriceViewSet, basename='price')
router.register('film', resources.FilmViewSetMixin, basename='film')
router.register('hall', resources.HallViewSetMixin, basename='hall')
router.register('seance_base', resources.SeanceBaseViewSet, basename='seance_base')
router.register('seance', resources.SeanceViewSetMixin, basename='seance')


urlpatterns = [
    path('seance/activate/<int:pk>/', resources.SeanceActivateView.as_view(), name='activate_seance'),
    path('hall/<int:pk>/create-seats/', resources.CreateSeatsAPIView.as_view(), name='create_seats'),
    path('swagger-docs/', schema_view),
    path('', include(router.urls)),
]
