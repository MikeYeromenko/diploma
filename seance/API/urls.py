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

urlpatterns = [
    path('', include(router.urls)),
]
