from django.urls import path

from seance.custom_admin import AdminMainView
from seance.views import SeanceListView, RegisterUserView, UserLoginView, UserProfileView, UserLogoutView, BasketView, \
    SeanceDetailView, BasketRedirectView, BasketCancelView, PurchaseCreateView, PurchaseListView

app_name = 'seance'

urlpatterns = [
    path('admin/main/', AdminMainView.as_view(), name='admin_main'),
    path('buy/', PurchaseCreateView.as_view(), name='buy'),
    path('my_tickets/', PurchaseListView.as_view(), name='my_tickets'),
    path('basket/cancel/', BasketCancelView.as_view(), name='basket-cancel'),
    path('basket/redirect/', BasketRedirectView.as_view(), name='basket-redirect'),
    path('basket/', BasketView.as_view(), name='basket'),
    path('accounts/profile/', UserProfileView.as_view(), name='profile'),
    path('accounts/logout/', UserLogoutView.as_view(), name='logout'),
    path('accounts/login/', UserLoginView.as_view(), name='login'),
    path('accounts/register/', RegisterUserView.as_view(), name='register'),
    path('seance/<int:pk>/', SeanceDetailView.as_view(), name='seance_detail'),
    path('', SeanceListView.as_view(), name='index'),

]