from django.views.generic import ListView, DetailView
from django.shortcuts import render
from django.db.models import Q
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
        qs = Animal.objects.filter(is_active=True)

        search = self.request.GET.get('q', '')
        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(category__name__icontains=search)
            )

        category_slug = self.kwargs.get('slug')
        if category_slug:
            qs = qs.filter(category__slug=category_slug)

        category = self.request.GET.get('category', '')
        if category:
            qs = qs.filter(category__name__iexact=category)

        return qs


class AnimalDetailView(DetailView):
    model = Animal
    template_name = 'animals/animal_detail.html'
    context_object_name = 'animal'
