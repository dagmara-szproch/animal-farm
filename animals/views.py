from django.views.generic import ListView, DetailView
from django.shortcuts import render
from .models import Animal, Category


def home(request):
    # Get active animals
    animals = Animal.objects.filter(is_active=True)
    return render(request, 'home.html', {'animals': animals})

def categories_context(request):
    return {'categories': Category.objects.all()}

class AnimalListView(ListView):
    model = Animal
    template_name = 'animals/animal_list.html'
    context_object_name = 'animals'
    paginate_by = 12

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
