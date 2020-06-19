from django.urls import path

from myadmin import views

app_name = 'myadmin'


urlpatterns = [
    path('film/create/', views.FilmCreateView.as_view(), name='film_create'),
    path('films/<int:pk>/', views.FilmUpdateView.as_view(), name='film_update'),
    path('films/', views.FilmListView.as_view(), name='film_list'),
    path('', views.AdminMainView.as_view(), name='main'),
]
