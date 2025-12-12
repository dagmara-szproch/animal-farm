from django.urls import path
from .views import AnimalListView, AnimalDetailView

app_name = 'animals'

urlpatterns = [
    # /animals/
    path('', AnimalListView.as_view(), name='list'),
    # /animals/category/category-slug/
    path('category/<slug:slug>/', AnimalListView.as_view(), name='by_category'),
    # /animals/animal-slug/
    path('<slug:slug>/', AnimalDetailView.as_view(), name='detail'),
]
