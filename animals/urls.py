from django.urls import path
from .views import AnimalListView, AnimalDetailView

app_name = 'animals'

urlpatterns = [
    path('', AnimalListView.as_view(), name='list'),              # /animals/
    path('category/<slug:slug>/', AnimalListView.as_view(), name='by_category'),  # /animals/category/horses/
    path('<slug:slug>/', AnimalDetailView.as_view(), name='detail'),  # /animals/animal-slug/
]
