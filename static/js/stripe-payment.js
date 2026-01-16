// Stripe payment flow for Hendoshi checkout

document.addEventListener('DOMContentLoaded', () => {
    const paymentForm = document.getElementById('paymentForm');
    if (!paymentForm) return;

    const stripePublicKey = paymentForm.dataset.publicKey;
    const clientSecret = paymentForm.dataset.clientSecret;
    if (!stripePublicKey || !clientSecret) return;

    const stripe = Stripe(stripePublicKey);
    const elements = stripe.elements();
    const cardElement = elements.create('card', {
        hidePostalCode: true,
        style: {
            base: {
                color: '#F5F5F5',
                fontFamily: 'inherit',
                fontSize: '16px',
                '::placeholder': { color: '#888' },
            },
            invalid: {
                color: '#FF1493',
            },
        },
    });

    const cardContainer = document.getElementById('card-element');
    if (!cardContainer) return;
    cardElement.mount(cardContainer);

    // Hide autofill link by injecting CSS
    const style = document.createElement('style');
    style.textContent = `
        .StripeElement__iframe[title*="Autofill"],
        [role="button"][aria-label*="Autofill"] {
            display: none !important;
        }
    `;
    document.head.appendChild(style);

    const submitButton = document.getElementById('submitPayment');
    const loadingOverlay = document.getElementById('paymentLoading');
    const cardErrors = document.getElementById('card-errors');
    const postalInput = document.getElementById('billingPostalCode');
    const cardholderInput = document.getElementById('cardholderName');

    const fullName = paymentForm.dataset.fullName || '';
    const email = paymentForm.dataset.email || '';
    const addressLine = paymentForm.dataset.address || '';
    const city = paymentForm.dataset.city || '';
    const country = paymentForm.dataset.country || '';
    const fallbackPostal = paymentForm.dataset.postal || '';

    cardElement.on('change', event => {
        if (!cardErrors) return;
        if (event.error) {
            cardErrors.textContent = event.error.message;
            cardErrors.classList.add('show');
        } else {
            cardErrors.textContent = '';
            cardErrors.classList.remove('show');
        }
    });

    paymentForm.addEventListener('submit', async event => {
        event.preventDefault();
        setLoading(true);

        try {
            // Build billing details object, only including non-empty values
            const billingDetails = {
                name: cardholderInput?.value?.trim() || fullName,
                email,
            };

            // Only add address if country is provided
            if (country) {
                billingDetails.address = {
                    line1: addressLine || undefined,
                    city: city || undefined,
                    country: country,
                    postal_code: (postalInput?.value || '').trim() || fallbackPostal || undefined,
                };
            }

            // Create payment method from card element
            const { paymentMethod, error: pmError } = await stripe.createPaymentMethod({
                type: 'card',
                card: cardElement,
                billing_details: billingDetails,
            });

            if (pmError) {
                showError(pmError.message || 'Payment failed. Please try again.');
                setLoading(false);
                return;
            }

            // Confirm payment with the payment method
            const { error, paymentIntent } = await stripe.confirmCardPayment(clientSecret, {
                payment_method: paymentMethod.id,
            });

            if (error) {
                showError(error.message || 'Payment failed. Please try again.');
                setLoading(false);
                return;
            }

            // If payment succeeded, notify server
            if (paymentIntent && (paymentIntent.status === 'succeeded' || paymentIntent.status === 'processing')) {
                await notifyServer(paymentIntent.id);
            }
        } catch (err) {
            showError(err.message || 'An error occurred. Please try again.');
            setLoading(false);
        }
    });

    function showError(message) {
        if (!cardErrors) return;
        cardErrors.textContent = message;
        cardErrors.classList.add('show');
        cardContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    function setLoading(isLoading) {
        const loadingText = submitButton?.querySelector('.loading-text');
        const defaultText = submitButton?.querySelector('.default-text');

        if (isLoading) {
            submitButton?.setAttribute('disabled', 'disabled');
            loadingText?.classList.remove('d-none');
            defaultText?.classList.add('d-none');
            loadingOverlay?.classList.remove('d-none');
        } else {
            submitButton?.removeAttribute('disabled');
            loadingText?.classList.add('d-none');
            defaultText?.classList.remove('d-none');
            loadingOverlay?.classList.add('d-none');
        }
    }

    async function notifyServer(paymentIntentId) {
        const response = await fetch(paymentForm.action, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({ payment_intent_id: paymentIntentId }),
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Payment could not be completed.');
        }

        if (data.redirect_url) {
            window.location.href = data.redirect_url;
        }
    }

    function getCsrfToken() {
        const name = 'csrftoken=';
        const decodedCookie = decodeURIComponent(document.cookie);
        const cookies = decodedCookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let c = cookies[i];
            while (c.charAt(0) === ' ') {
                c = c.substring(1);
            }
            if (c.indexOf(name) === 0) {
                return c.substring(name.length, c.length);
            }
        }
        return '';
    }
});
