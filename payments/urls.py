from django.urls import path
from . import views

urlpatterns = [
    path('test-create/', views.create_test_payment, name='test_create_payment'),
]
