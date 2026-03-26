/* ================================================
   HENDOSHI - STRIPE PAYMENT
   ================================================
   
   Purpose: JavaScript functionality for stripe payment
   
   Contains:
   - Event handlers
   - User interactions
   - Dynamic functionality
   
   Dependencies: utils.js (typically)
   Load Order: Load as needed for specific pages
   ================================================ */

// Stripe payment flow for Hendoshi checkout
// console.log('JS loaded');

document.addEventListener('DOMContentLoaded', () => {
    const paymentForm = document.getElementById('paymentForm');
    // Clean up any diagnostic outlines or box-shadows left behind by previous debug runs
    try {
        document.querySelectorAll('[style]').forEach(el => {
            try {
                if (el.style.outline) el.style.outline = '';
                if (el.style.boxShadow) el.style.boxShadow = '';
            } catch (e) {}
        });
    } catch (e) {}
    if (!paymentForm) {
        console.error('Payment form (#paymentForm) not found on the page');
        return;
    }

    // Log dataset for visibility
    // console.log('Payment form dataset:', paymentForm.dataset);

    const stripePublicKey = paymentForm.dataset.publicKey;
    const clientSecret = paymentForm.dataset.clientSecret;
    if (!stripePublicKey || !clientSecret) {
        console.error('Stripe public key or client secret missing:', { stripePublicKey, clientSecret });
        const mountError = document.createElement('div');
        mountError.className = 'card-mount-error';
        mountError.textContent = 'Payment fields unavailable — Stripe is not configured on this environment.';
        const parent = document.getElementById('card-element') || paymentForm;
        if (parent && parent.parentNode) {
            parent.parentNode.insertBefore(mountError, document.getElementById('card-element')?.nextSibling || null);
        }
        return;
    }

    // Defer Stripe-dependent initialization in a function so we can load Stripe dynamically if needed
    // Prepare shared variables for Stripe instance and element
    let stripeInstance = null;
    let cardElement = null;
    let submitButton, loadingOverlay, cardErrors, postalInput, cardholderInput;
    const cardContainer = document.getElementById('card-element');
    if (!cardContainer) {
        console.error('Card container (#card-element) not found');
        return;
    }

    function startStripeInit() {
        if (typeof Stripe === 'undefined') {
            console.warn('Stripe still undefined at init time. Aborting init.');
            const mountError = document.createElement('div');
            mountError.className = 'card-mount-error';
            mountError.textContent = 'Payment provider script not loaded. Check console for CSP or network errors.';
            const parent = cardContainer || paymentForm;
            if (parent && parent.parentNode) {
                parent.parentNode.insertBefore(mountError, cardContainer?.nextSibling || null);
            }
            return;
        }

        try {
            stripeInstance = Stripe(stripePublicKey);
            // console.log('Stripe initialized');
        } catch (err) {
            console.error('Stripe() initialization failed:', err);
            const mountError = document.createElement('div');
            mountError.className = 'card-mount-error';
            mountError.textContent = 'Payment initialization failed. See console for details.';
            const parent = cardContainer || paymentForm;
            if (parent && parent.parentNode) {
                parent.parentNode.insertBefore(mountError, cardContainer?.nextSibling || null);
            }
            return;
        }

        const elements = stripeInstance.elements();
        cardElement = elements.create('card', {
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

        try {
            cardElement.mount(cardContainer);
            // console.log('Stripe card element mounted');
        } catch (err) {
            console.error('Error mounting Stripe card element:', err);
            return;
        }

        // Accessibility: focus the card element when its label is clicked
        const cardLabel = document.getElementById('card-element-label');
        if (cardLabel) {
            cardLabel.addEventListener('click', function(e) {
                e.preventDefault();
                try {
                    cardElement.focus();
                    // console.log('cardElement.focus() called from label click');
                } catch (err) {
                    try { cardContainer.focus(); } catch (e) {}
                    console.warn('cardElement.focus() failed, focused container instead', err);
                }
            });
        } else {
            console.warn('Card label (#card-element-label) not found');
        }

        // Diagnostic: detect element blocking the stripe iframe by checking element at card center
        function detectBlockingElement() {
            if (!cardContainer) return null;
            const rect = cardContainer.getBoundingClientRect();
            const x = rect.left + rect.width / 2;
            const y = rect.top + rect.height / 2;
            const el = document.elementFromPoint(x, y);
            // console.log('Element at card center (diagnostic):', el);
            if (el && !cardContainer.contains(el)) {
                // console.warn('Found element blocking card input (diagnostic):', el);
            }
            return el;
        }

        // Run detection shortly after mount and on resize/scroll
        setTimeout(detectBlockingElement, 300);
        window.addEventListener('resize', detectBlockingElement);
        window.addEventListener('scroll', detectBlockingElement, { passive: true });

        // Log iframe presence
        setTimeout(function() {
            // iframe not used but kept for diagnostic purposes
            // const iframe = cardContainer.querySelector('iframe');
            // console.log('Stripe iframe found:', iframe);
            // if (!iframe) console.warn('Stripe iframe not found inside #card-element — mount may not have succeeded or Stripe may be blocked');
        }, 400);

        // Hide autofill link by injecting CSS
        const style = document.createElement('style');
        style.textContent = `
            .StripeElement__iframe[title*="Autofill"],
            [role="button"][aria-label*="Autofill"] {
                display: none !important;
            }
        `;
        document.head.appendChild(style);

        // Wire up element change handler
        cardElement.on('change', event => {
            const cardErrors = document.getElementById('card-errors');
            if (!cardErrors) return;
            if (event.error) {
                cardErrors.textContent = event.error.message;
                cardErrors.classList.add('show');
            } else {
                cardErrors.textContent = '';
                cardErrors.classList.remove('show');
            }
        });

        // Form submit handling
        submitButton = document.getElementById('submitPayment');
        loadingOverlay = document.getElementById('paymentLoading');
        postalInput = document.getElementById('billingPostalCode');
        cardholderInput = document.getElementById('cardholderName');
        cardErrors = document.getElementById('card-errors');

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

        paymentForm.addEventListener('submit', async event => {
            event.preventDefault();
            setLoading(true);

            try {
                const billingDetails = {
                    name: cardholderInput?.value?.trim() || (paymentForm.dataset.fullName || ''),
                    email: paymentForm.dataset.email || '',
                };

                if (paymentForm.dataset.country) {
                    billingDetails.address = {
                        line1: paymentForm.dataset.address || undefined,
                        city: paymentForm.dataset.city || undefined,
                        country: paymentForm.dataset.country,
                        postal_code: (postalInput?.value || '').trim() || paymentForm.dataset.postal || undefined,
                    };
                }

                const { paymentMethod, error: pmError } = await stripeInstance.createPaymentMethod({
                    type: 'card',
                    card: cardElement,
                    billing_details: billingDetails,
                });

                if (pmError) {
                    showError(pmError.message || 'Payment failed. Please try again.');
                    setLoading(false);
                    return;
                }

                const { error, paymentIntent } = await stripeInstance.confirmCardPayment(clientSecret, {
                    payment_method: paymentMethod.id,
                });

                if (error) {
                    showError(error.message || 'Payment failed. Please try again.');
                    setLoading(false);
                    return;
                }

                if (paymentIntent && (paymentIntent.status === 'succeeded' || paymentIntent.status === 'processing')) {
                    await notifyServer(paymentIntent.id);
                }
            } catch (err) {
                showError(err.message || 'An error occurred. Please try again.');
                setLoading(false);
            }
        });
    }
    // If Stripe is not defined yet on load, try to inject the Stripe script dynamically and initialize after load
    function ensureStripeScriptAndInit() {
        if (typeof Stripe !== 'undefined') {
            // console.log('Stripe already present, initializing immediately');
            startStripeInit();
            return;
        }

        // Check if script tag already exists
        let script = document.querySelector('script[src="https://js.stripe.com/v3/"]');
        if (script) {
            // console.log('Stripe script tag exists but Stripe is undefined — waiting for load');
            // Attach load handlers
            script.addEventListener('load', function() { /* console.log('External Stripe script loaded'); */ startStripeInit(); });
            script.addEventListener('error', function(e) { console.error('External Stripe script failed to load', e); });
            return;
        }

        // console.log('Stripe script missing, injecting script tag dynamically');
        script = document.createElement('script');
        script.src = 'https://js.stripe.com/v3/';
        script.async = true;
        script.onload = function() { /* console.log('Injected Stripe script loaded'); */ startStripeInit(); };
        script.onerror = function(e) { console.error('Injected Stripe script failed to load', e); };
        document.head.appendChild(script);
    }

    try {
        ensureStripeScriptAndInit();
    } catch (e) {
        console.error('Error ensuring Stripe script and init:', e);
    }

    // Accessibility: focus the card element when its label is clicked
    const cardLabel = document.getElementById('card-element-label');
    if (cardLabel) {
        cardLabel.addEventListener('click', function(e) {
            e.preventDefault();
            try {
                // Stripe Elements exposes focus() on the element instance
                cardElement.focus();
                console.log('cardElement.focus() called from label click');
            } catch (err) {
                // As a fallback, blur and focus the container
                try { cardContainer.focus(); } catch (e) {}
                console.warn('cardElement.focus() failed, focused container instead', err);
            }
        });
    } else {
        console.warn('Card label (#card-element-label) not found');
    }

    // Note: diagnostic highlighting was intentionally removed — detection remains inside init.
    // Log iframe presence as a final check
    setTimeout(function() {
        const iframe = cardContainer.querySelector('iframe');
        // console.log('Stripe iframe (post-init) found:', iframe);
        if (!iframe) console.warn('Stripe iframe not found inside #card-element — mount may not have succeeded or Stripe may be blocked');
    }, 400);

    // Hide autofill link by injecting CSS
    const style = document.createElement('style');
    style.textContent = `
        .StripeElement__iframe[title*="Autofill"],
        [role="button"][aria-label*="Autofill"] {
            display: none !important;
        }
    `;
    document.head.appendChild(style);

});
