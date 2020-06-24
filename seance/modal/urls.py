from django.urls import path

from seance.modal import views


app_name = 'modal'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('ordering_form/', views.ModalOrderingView.as_view(), name='ordering'),
]
