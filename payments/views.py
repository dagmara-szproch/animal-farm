import stripe
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from animals.models import Animal
from .models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def create_donation(request, animal_slug):
    animal = get_object_or_404(Animal, slug=animal_slug)

    # Get preset amount from URL or default to 5
    preset_amount = request.GET.get('amount', '5')
    try:
        preset_amount = float(preset_amount)
    except (ValueError, TypeError):
        preset_amount = 5

    # Convert to pence
    amount_pence = int(preset_amount * 100)

    # Initialize variables
    client_secret = None
    error_message = None

    try:
        intent = stripe.PaymentIntent.create(
            amount=amount_pence,
            currency='gbp',
            metadata={
                'animal_id': animal.id,
                'animal_name': animal.name,
                'user_id': request.user.id,
            },
            automatic_payment_methods={
                'enabled': True,
            },
        )
        client_secret = intent.client_secret

    except stripe.error.StripeError as e:
        error_message = f'Stripe error: {e.user_message}'
    except Exception as e:
        error_message = f'Error: {str(e)}'

    # If we have an error, redirect
    if error_message:
        messages.error(request, error_message)
        return redirect('animals:detail', slug=animal_slug)

    # If success, render template
    context = {
        'animal': animal,
        'preset_amount': preset_amount,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'client_secret': client_secret,
    }

    return render(request, 'payments/donation_form.html', context)


@login_required
@require_POST
def process_donation(request, animal_slug):
    """
    Process donation - traditional POST with PaymentIntent confirmation.
    Like e-commerce checkout process.
    """
    animal = get_object_or_404(Animal, slug=animal_slug)

    try:
        # Get form data
        amount = float(request.POST.get('amount', 5))
        message = request.POST.get('message', '').strip()
        payment_intent_id = request.POST.get('payment_intent_id')

        if not payment_intent_id:
            messages.error(request, 'Payment information missing.')
            return redirect('payments:create_donation',
                            animal_slug=animal_slug)

        # Retrieve the PaymentIntent to check status
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        if intent.status != 'succeeded':
            messages.error(request, 'Payment was not successful.')
            return redirect('payments:create_donation',
                            animal_slug=animal_slug)

        # Get donor info
        donor_name = request.user.get_full_name() or request.user.username

        # Create payment record
        payment = Payment.objects.create(
            user=request.user,
            animal=animal,
            amount=amount,
            email=request.user.email,
            donor_name=donor_name,
            message=message[:500],
            stripe_payment_intent_id=payment_intent_id,
            status='succeeded'
        )

        # Generate donation reference (no model change needed)
        donation_ref = f"DON-{payment.id:06d}"

        # Store in session for success page
        request.session['last_donation_ref'] = donation_ref
        request.session['last_donation_id'] = payment.id

        return redirect('payments:success')

    except stripe.error.StripeError as e:
        messages.error(request, f'Payment error: {e.user_message}')
        return redirect('payments:create_donation', animal_slug=animal_slug)
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('payments:create_donation', animal_slug=animal_slug)


@login_required
def payment_success(request):
    """Show success page after donation."""
    donation_ref = request.session.get('last_donation_ref', '')
    donation_id = request.session.get('last_donation_id')

    # Clear session
    if 'last_donation_ref' in request.session:
        del request.session['last_donation_ref']
    if 'last_donation_id' in request.session:
        del request.session['last_donation_id']

    # Get payment if ID
    payment = None
    animal = None
    if donation_id:
        try:
            payment = Payment.objects.get(id=donation_id, user=request.user)
            animal = payment.animal
        except Payment.DoesNotExist:
            pass

    context = {
        'payment': payment,
        'animal': animal,
        'donation_ref': donation_ref,
    }

    return render(request, 'payments/success.html', context)
