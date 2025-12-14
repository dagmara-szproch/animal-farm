from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from animals.models import Animal
from .models import Payment


@login_required
def create_test_payment(request):
    """Temporary view to verify Payment model and admin integration."""
    animal = Animal.objects.first()

    payment = Payment.objects.create(
        user=request.user,
        animal=animal,
        amount=5,
        email=request.user.email,
        donor_name=request.user.get_full_name() or request.user.username,
        status='pending',
    )

    return HttpResponse(f"Test payment created with id {payment.id}")
