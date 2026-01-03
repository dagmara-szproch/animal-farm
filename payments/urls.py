from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('donate/<slug:animal_slug>/', views.create_donation, name='create_donation'),
    path('process/<slug:animal_slug>/', views.process_donation, name='process_donation'),
    path('success/', views.payment_success, name='success'),
    path('message/<int:payment_id>/edit/', views.edit_message, name='edit_message'),
    path('message/<int:payment_id>/delete/', views.delete_message, name='delete_message'),
]
