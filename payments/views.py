import stripe
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST, require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from animals.models import Animal
from .models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def create_donation(request, animal_slug):
    """
    Show donation form. PaymentIntent is created only when amount is selected.
    """
    animal = get_object_or_404(Animal, slug=animal_slug)

    # Check if amount is selected via URL parameter
    selected_amount = request.GET.get('amount')
    client_secret = None

    if selected_amount:
        try:
            amount = float(selected_amount)
            if amount >= 1:
                # Create PaymentIntent with selected amount
                amount_pence = int(amount * 100)
                intent = stripe.PaymentIntent.create(
                    amount=amount_pence,
                    currency='gbp',
                    metadata={
                        'animal_id': animal.id,
                        'user_id': request.user.id,
                    },
                    automatic_payment_methods={'enabled': True},
                )
                client_secret = intent.client_secret
            else:
                messages.error(request, 'Amount must be at least £1')
                return redirect('payments:create_donation',
                                animal_slug=animal_slug)
        except (ValueError, TypeError):
            messages.error(request, 'Invalid amount')
            return redirect('payments:create_donation',
                            animal_slug=animal_slug)

    context = {
        'animal': animal,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'client_secret': client_secret,  # None if no amount selected
        'selected_amount': selected_amount,
    }

    return render(request, 'payments/donation_form.html', context)


@login_required
@require_POST
def process_donation(request, animal_slug):
    """Process the payment after Stripe.js confirmation"""
    animal = get_object_or_404(Animal, slug=animal_slug)

    try:
        # Get data from form
        amount = float(request.POST.get('amount', 0))
        message = request.POST.get('message', '').strip()
        payment_intent_id = request.POST.get('payment_intent_id')

        if not payment_intent_id:
            messages.error(request, 'Payment information missing.')
            return redirect('payments:create_donation',
                            animal_slug=animal_slug)

        # Verify the payment succeeded
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        if intent.status != 'succeeded':
            messages.error(request, 'Payment was not successful.')
            return redirect('payments:create_donation',
                            animal_slug=animal_slug)

        # Create payment record
        payment = Payment.objects.create(
            user=request.user,
            animal=animal,
            amount=amount,
            email=request.user.email,
            donor_name=request.user.get_full_name() or request.user.username,
            message=message[:500],
            stripe_payment_intent_id=payment_intent_id,
            status='succeeded'
        )

        # Store in session for success page
        request.session['last_donation_id'] = payment.id
        request.session['last_donation_ref'] = f"DON-{payment.id:06d}"

        return redirect('payments:success')

    except stripe.error.StripeError as e:
        messages.error(request, f'Payment error: {e.user_message}')
        return redirect('payments:create_donation', animal_slug=animal_slug)
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('payments:create_donation', animal_slug=animal_slug)


@login_required
def payment_success(request):
    """Show success page"""
    donation_id = request.session.get('last_donation_id')
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
        'donation_ref': request.session.get('last_donation_ref', ''),
    }

    # Clear session
    if 'last_donation_id' in request.session:
        del request.session['last_donation_id']
    if 'last_donation_ref' in request.session:
        del request.session['last_donation_ref']

    return render(request, 'payments/success.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def edit_message(request, payment_id):
    """Edit a message associated with a donation"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)

    if request.method == 'GET':
        # Return message data for editing
        return JsonResponse({
            'message': payment.message,
            'animal_name': payment.animal.name if payment.animal else None,
            'created_at': payment.created_at.strftime('%d %b %Y')
        })

    elif request.method == 'POST':
        # Update message
        try:
            data = json.loads(request.body)
            new_message = data.get('message', '').strip()[:500]

            payment.message = new_message
            # Reset to pending for admin review
            payment.message_status = 'pending'
            payment.save()

            messages.success(request,
                             'Message updated and is pending approval.')
            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False,
                                 'error': str(e)}, status=400)


@login_required
@require_POST
def delete_message(request, payment_id):
    """Delete a message"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    payment.message = ''
    payment.message_status = 'rejected'
    payment.save()

    messages.success(request, 'Message deleted successfully.')
    return JsonResponse({'success': True})
