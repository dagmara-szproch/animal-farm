from django.views.generic import ListView, DetailView
from django.shortcuts import render
from .models import Animal, Category


def home(request):
    # Get active animals
    animals = Animal.objects.filter(is_active=True)
    return render(request, 'home.html', {'animals': animals})


class AnimalListView(ListView):
    model = Animal
    template_name = 'animals/animal_list.html'
    context_object_name = 'animals'

    def get_queryset(self):
        qs = Animal.objects.filter(is_active=True).select_related('category')
        category_slug = self.kwargs.get('slug')
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        return qs


class AnimalDetailView(DetailView):
    model = Animal
    template_name = 'animals/animal_detail.html'
    context_object_name = 'animal'
