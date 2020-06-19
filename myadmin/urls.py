from django.urls import path

from myadmin import views

app_name = 'myadmin'


urlpatterns = [
    path('films/', views.FilmListView.as_view(), name='film_list'),
    path('', views.AdminMainView.as_view(), name='main'),
]
