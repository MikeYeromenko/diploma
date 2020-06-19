from django.urls import path

from myadmin import views

app_name = 'myadmin'


urlpatterns = [
    path('price/create/', views.PriceCreateView.as_view(), name='price_create'),
    path('price/delete/<int:pk>/', views.PriceDeleteView.as_view(), name='price_delete'),
    path('price/update/<int:pk>/', views.PriceUpdateView.as_view(), name='price_update'),
    path('price/list/', views.PriceTemplateView.as_view(), name='price_list'),
    path('seat/category/delete/<int:pk>/', views.SeatCategoryDeleteView.as_view(), name='seat_category_delete'),
    path('seat/category/update/<int:pk>/', views.SeatCategoryCRUDView.as_view(), name='seat_category_update'),
    path('seat/category/', views.SeatCategoryCRUDView.as_view(), name='seat_category_crud'),
    path('film/delete/<int:pk>/', views.FilmDeleteView.as_view(), name='film_delete'),
    path('film/create/', views.FilmCreateView.as_view(), name='film_create'),
    path('films/<int:pk>/', views.FilmUpdateView.as_view(), name='film_update'),
    path('films/', views.FilmListView.as_view(), name='film_list'),
    path('', views.AdminMainView.as_view(), name='main'),
]
