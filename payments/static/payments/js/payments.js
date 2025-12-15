document.addEventListener('DOMContentLoaded', function() {
    console.log("Payment page loaded");
    
    // ===== GET ELEMENTS =====
    const amountButtons = document.querySelectorAll('.amount-btn');
    const customAmountInput = document.getElementById('custom-amount');
    const applyCustomButton = document.getElementById('apply-custom');
    const form = document.getElementById('payment-form');
    
    // ===== GET AMOUNT FROM URL =====
    const urlParams = new URLSearchParams(window.location.search);
    const urlAmount = urlParams.get('amount');
    console.log("URL amount parameter:", urlAmount);
    
    // ===== POPULATE CUSTOM AMOUNT FROM URL =====
    if (urlAmount && customAmountInput) {
        const amountNum = parseFloat(urlAmount);
        // Only populate if not a preset amount
        if (![5, 10, 25].includes(amountNum)) {
            customAmountInput.value = urlAmount;
        }
    }
    
    // ===== UPDATE BUTTON STYLES BASED ON URL AMOUNT =====
    if (urlAmount && amountButtons.length > 0) {
        const amountNum = parseFloat(urlAmount);
        console.log("Setting button styles for amount:", amountNum);
        
        // First, reset all buttons
        amountButtons.forEach(btn => {
            btn.classList.remove('bg-cyan-800', 'text-white');
            btn.classList.add('bg-white', 'border-cyan-800', 'text-cyan-800');
        });
        
        // If it's a preset amount (5, 10, 25), highlight that button
        if ([5, 10, 25].includes(amountNum)) {
            amountButtons.forEach(btn => {
                const btnAmount = parseFloat(btn.getAttribute('data-amount'));
                if (btnAmount === amountNum) {
                    console.log("Highlighting button for amount:", btnAmount);
                    btn.classList.add('bg-cyan-800', 'text-white');
                    btn.classList.remove('bg-white', 'border-cyan-800', 'text-cyan-800');
                }
            });
        }
        // If custom amount, all buttons should be unhighlighted
        else {
            console.log("Custom amount, all buttons unhighlighted");
        }
    }
    
    // ===== AMOUNT SELECTION =====
    // Handle preset amount buttons
    amountButtons.forEach(button => {
        button.addEventListener('click', function() {
            const amount = this.getAttribute('data-amount');
            console.log("Selected amount:", amount);
            
            // Clear custom input
            if (customAmountInput) {
                customAmountInput.value = '';
            }
            
            // Refresh page with selected amount
            const currentUrl = window.location.origin + window.location.pathname;
            window.location.href = currentUrl + '?amount=' + amount;
        });
    });
    
    // Handle custom amount
    if (customAmountInput && applyCustomButton) {
        applyCustomButton.addEventListener('click', function() {
            const amount = customAmountInput.value;
            if (amount && parseFloat(amount) >= 1) {
                console.log("Custom amount:", amount);
                
                // Refresh page with custom amount
                const currentUrl = window.location.origin + window.location.pathname;
                window.location.href = currentUrl + '?amount=' + amount;
            } else {
                alert('Please enter a valid amount (£1 or more)');
            }
        });
        
        // Also allow Enter key
        customAmountInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                applyCustomButton.click();
            }
        });
    }
    
    // ===== STRIPE PAYMENT (only if form exists) =====
    if (form) {
        console.log("Payment form found, initializing Stripe...");
        
        // Update donate amount display
        const donateAmountSpan = document.getElementById('donate-amount');
        const selectedAmountInput = document.getElementById('selected-amount');
        if (donateAmountSpan && selectedAmountInput) {
            donateAmountSpan.textContent = selectedAmountInput.value;
        }
        
        // Get Stripe keys
        const stripePublicKey = JSON.parse(document.getElementById('stripe_public_key').textContent);
        const clientSecret = JSON.parse(document.getElementById('client_secret').textContent);
        
        // Initialize Stripe
        const stripe = Stripe(stripePublicKey);
        const elements = stripe.elements();
        const card = elements.create('card');
        card.mount('#card-element');
        
        // Card errors
        const cardErrors = document.getElementById('card-errors');
        card.addEventListener('change', function(event) {
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
            
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Processing...';
            cardErrors.textContent = '';
            cardErrors.classList.add('hidden');
            
            try {
                const { paymentIntent, error } = await stripe.confirmCardPayment(
                    clientSecret,
                    { payment_method: { card: card } }
                );
                
                if (error) {
                    cardErrors.textContent = error.message;
                    cardErrors.classList.remove('hidden');
                    submitButton.disabled = false;
                    submitButton.innerHTML = 'Donate £' + 
                        document.getElementById('selected-amount').value + ' Now';
                } else {
                    document.getElementById('payment_intent_id').value = paymentIntent.id;
                    form.submit();
                }
            } catch (err) {
                console.error("Payment error:", err);
                cardErrors.textContent = 'An unexpected error occurred. Please try again.';
                cardErrors.classList.remove('hidden');
                submitButton.disabled = false;
                submitButton.innerHTML = 'Donate £' + 
                    document.getElementById('selected-amount').value + ' Now';
            }
        });
        
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
    }
});