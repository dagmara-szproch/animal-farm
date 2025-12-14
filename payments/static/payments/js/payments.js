document.addEventListener('DOMContentLoaded', function() {
    // ===== AMOUNT SELECTION =====
    const amountButtons = document.querySelectorAll('.amount-btn');
    const customAmountInput = document.getElementById('custom-amount');
    const selectedAmountInput = document.getElementById('selected-amount');
    const displayAmountSpan = document.getElementById('display-amount');
    
    function updateAmount(amount) {
        selectedAmountInput.value = amount;
        displayAmountSpan.textContent = amount;
        
        if (customAmountInput && [5, 10, 25].includes(amount)) {
            customAmountInput.value = '';
        }
        
        amountButtons.forEach(button => {
            const buttonAmount = parseFloat(button.getAttribute('data-amount'));
            if (buttonAmount === amount) {
                button.classList.add('bg-cyan-800', 'text-white');
                button.classList.remove('bg-white', 'border-cyan-800', 'text-cyan-800');
            } else {
                button.classList.remove('bg-cyan-800', 'text-white');
                button.classList.add('bg-white', 'border-cyan-800', 'text-cyan-800');
            }
        });
    }
    
    amountButtons.forEach(button => {
        button.addEventListener('click', function() {
            const amount = parseFloat(this.getAttribute('data-amount'));
            updateAmount(amount);
        });
    });
    
    if (customAmountInput) {
        customAmountInput.addEventListener('input', function() {
            const amount = parseFloat(this.value);
            if (amount && amount > 0) {
                updateAmount(amount);
                amountButtons.forEach(button => {
                    button.classList.remove('bg-cyan-800', 'text-white');
                    button.classList.add('bg-white', 'border-cyan-800', 'text-cyan-800');
                });
            }
        });
    }
    
    // ===== MESSAGE COUNTER =====
    const messageTextarea = document.getElementById('message');
    const charCounter = document.getElementById('char-counter');
    
    if (messageTextarea && charCounter) {
        messageTextarea.addEventListener('input', function() {
            const length = this.value.length;
            charCounter.textContent = `${length}/500`;
            
            if (length > 500) {
                charCounter.classList.add('text-red-600');
                this.value = this.value.substring(0, 500);
            } else {
                charCounter.classList.remove('text-red-600');
            }
        });
    }
    
    // ===== STRIPE PAYMENT =====
    const form = document.getElementById('payment-form');
    if (!form) return;
    
    // Get Stripe public key and initialize
    const stripePublicKey = JSON.parse(document.getElementById('stripe_public_key').textContent);
    const stripe = Stripe(stripePublicKey);
    const elements = stripe.elements();
    const card = elements.create('card');
    card.mount('#card-element');
    
    // Card errors
    card.addEventListener('change', function(event) {
        const cardErrors = document.getElementById('card-errors');
        if (event.error) {
            cardErrors.textContent = event.error.message;
            cardErrors.classList.remove('hidden');
        } else {
            cardErrors.textContent = '';
            cardErrors.classList.add('hidden');
        }
    });
    
    // Form submission
    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        
        const submitButton = document.getElementById('submit-button');
        const cardErrors = document.getElementById('card-errors');
        const clientSecret = JSON.parse(document.getElementById('client_secret').textContent);
        
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Processing...';
        cardErrors.textContent = '';
        cardErrors.classList.add('hidden');
        
        const { paymentIntent, error } = await stripe.confirmCardPayment(
            clientSecret,
            { payment_method: { card: card } }
        );
        
        if (error) {
            cardErrors.textContent = error.message;
            cardErrors.classList.remove('hidden');
            submitButton.disabled = false;
            submitButton.innerHTML = 'Donate £<span id="display-amount">' + 
                document.getElementById('selected-amount').value + '</span> Now';
        } else {
            document.getElementById('payment_intent_id').value = paymentIntent.id;
            form.submit();
        }
    });
    
    // Initialize amount
    const initialAmount = parseFloat(selectedAmountInput.value) || 5;
    updateAmount(initialAmount);
});