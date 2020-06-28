from django.urls import path, include, re_path
from django.views.decorators.http import require_GET
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
    # re_path(r'(^seance/(?P<date>=(20[23]\d-(0[1-9]|1[0-2])-(0[1-9]|[1,2]\d|3[0,1])))(&P<ordering>=\w+)?/$)',
    #         resources.SeanceViewSet.as_view({'get': 'list'})),
    # re_path(r'(^seance/(?P<date>=(\d{4}-\d{2}-\d{2}))(&P<ordering>=\w+)?/$)',
    #         resources.SeanceListSortedViewSet.as_view({'get': 'list'})),
    # re_path(r'^seance/\?date=.*/$',
    #         resources.SeanceListSortedViewSet.as_view({'get': 'list'}), name='seance-list'),
    # path('seances/?date=<str:date>&ordering=<str:ordering>/', resources.SeanceListViewSet.as_view({'get': 'list'}),
    #      name='seance-list'),
    # re_path(r'^seances/(?P<date>[^/.]*)/$', resources.SeanceListViewSet.as_view({'get': 'list'}),
    #      name='seance-list'),
    path('', include(router.urls)),
]
