from .models import Category

def categories_context(request):
    """Make categories available to all templates."""
    try:
        categories = Category.objects.all()
        return {'categories': categories}
    except Exception:
        # If database isn't ready yet (e.g., during migrations)
        return {'categories': []}
