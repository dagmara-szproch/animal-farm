from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('donate/<slug:animal_slug>/', views.create_donation, name='create_donation'),
    path('process/<slug:animal_slug>/', views.process_donation, name='process_donation'),
    path('success/', views.payment_success, name='success'),
]