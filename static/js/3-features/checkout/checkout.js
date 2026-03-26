/**
 * Checkout Page Functionality
 * Address selection, form filling, shipping rate selection
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // ========================================
    // SAVED ADDRESS SELECTION
    // ========================================
    
    const savedAddressCards = document.querySelectorAll('.saved-address-card');
    const useNewAddressBtn = document.getElementById('useNewAddressBtn');
    const checkoutForm = document.getElementById('checkoutForm');
    
    // Auto-fill form from selected address
    const fillFormFromAddress = function(card) {
        if (card) {
            document.querySelector('[name="full_name"]').value = card.dataset.fullName || '';
            document.querySelector('[name="phone"]').value = card.dataset.phone || '';
            document.querySelector('[name="address"]').value = card.dataset.address || '';
            document.querySelector('[name="address_line_2"]').value = card.dataset.addressLine2 || '';
            document.querySelector('[name="city"]').value = card.dataset.city || '';
            document.querySelector('[name="state_or_county"]').value = card.dataset.state || '';
            document.querySelector('[name="country"]').value = card.dataset.country || '';
            document.querySelector('[name="postal_code"]').value = card.dataset.postal || '';
            
            // Add has-value class to filled inputs
            document.querySelectorAll('.checkout-form .form-control').forEach(input => {
                if (input.value.trim() !== '') {
                    input.classList.add('has-value');
                }
            });
        }
    };
    
    // Handle address card selection
    if (savedAddressCards) {
        savedAddressCards.forEach(card => {
            card.addEventListener('click', function() {
                // Remove selected class from all cards
                savedAddressCards.forEach(c => c.classList.remove('selected'));
                // Add selected class to clicked card
                this.classList.add('selected');
                // Hide the form using Bootstrap class
                const formContainer = document.getElementById('addressFormContainer');
                if (formContainer) {
                    formContainer.classList.add('d-none');
                }
                // Fill form
                fillFormFromAddress(this);
            });
        });
    }
    
    // Auto-fill from default address on load
    const defaultCard = document.querySelector('.saved-address-card.selected');
    if (defaultCard) {
        fillFormFromAddress(defaultCard);
    }
    
    // Show form if there are validation errors
    const formContainer = document.getElementById('addressFormContainer');
    const hasFormErrors = document.querySelectorAll('.form-error-text').length > 0;
    if (formContainer && hasFormErrors) {
        formContainer.classList.remove('d-none');
    }
    
    // Handle "Use new address" button
    if (useNewAddressBtn) {
        useNewAddressBtn.addEventListener('click', function() {
            // Remove selected class from all address cards
            savedAddressCards.forEach(c => c.classList.remove('selected'));
            
            // Show the form using Bootstrap class
            if (formContainer) {
                formContainer.classList.remove('d-none');
            }
            
            // Clear form
            document.querySelectorAll('.checkout-form .form-control').forEach(input => {
                input.value = '';
                input.classList.remove('has-value');
            });
            
            // Scroll to form
            if (checkoutForm) {
                checkoutForm.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    }
    
    // ========================================
    // COUNTRY/STATE LABEL UPDATE
    // ========================================
    
    const countrySelect = document.querySelector('select[name="country"]');
    const stateInput = document.querySelector('input[name="state_or_county"]');
    const stateLabel = document.querySelector('label[for="id_state_or_county"]');
    
    if (countrySelect && stateLabel) {
        const updateStateLabel = function() {
            if (countrySelect.value === 'US') {
                stateLabel.textContent = 'State';
                stateInput.placeholder = 'State';
            } else {
                stateLabel.textContent = 'State/County';
                stateInput.placeholder = 'State/County';
            }
        };
        
        countrySelect.addEventListener('change', updateStateLabel);
        updateStateLabel(); // Initial call
    }

    // ========================================
    // FORM VALIDATION FEEDBACK
    // ========================================
    
    const formInputs = document.querySelectorAll('.checkout-form .form-control, .checkout-form .form-select');
    
    formInputs.forEach(input => {
        // Remove error on input
        input.addEventListener('input', function() {
            const errorElement = this.closest('div').querySelector('.form-error-text');
            if (errorElement) {
                errorElement.style.display = 'none';
            }
            // Add visual feedback that field has been touched
            this.classList.add('has-value');
        });
        
        // Also remove error on change for selects
        input.addEventListener('change', function() {
            const errorElement = this.closest('div').querySelector('.form-error-text');
            if (errorElement && this.value.trim() !== '') {
                errorElement.style.display = 'none';
            }
        });
        
        // Check if field has initial value
        if (input.value.trim() !== '') {
            input.classList.add('has-value');
        }
    });
    
    //========================================
    // SHIPPING RATE SELECTION  
    // ========================================
    
    const shippingRadios = document.querySelectorAll('input[name="selected_shipping"]');
    const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    const csrftoken = csrfInput ? csrfInput.value : null;

    function updateTotalsDisplay(data) {
        const sub = document.getElementById('summary-subtotal');
        const ship = document.getElementById('summary-shipping');
        const disc = document.getElementById('summary-discount');
        const total = document.getElementById('summary-total');
        if (sub) sub.textContent = `€${parseFloat(data.cart_subtotal).toFixed(2)}`;
        if (ship) ship.textContent = `€${parseFloat(data.shipping_cost).toFixed(2)}`;
        if (disc) disc.textContent = `-€${parseFloat(data.discount_amount).toFixed(2)}`;
        if (total) total.textContent = `€${parseFloat(data.cart_total).toFixed(2)}`;
    }

    async function refreshTotals() {
        try {
            const resp = await fetch('/cart/totals/');
            if (!resp.ok) return;
            const data = await resp.json();
            updateTotalsDisplay(data);
        } catch (e) {
            console.warn('Could not refresh totals', e);
        }
    }

    async function persistSelection(selectedId) {
        if (!csrftoken) return;
        try {
            const resp = await fetch('/checkout/select-shipping-rate/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: `selected_shipping_id=${encodeURIComponent(selectedId)}`
            });
            if (resp.ok) {
                await refreshTotals();
            }
        } catch (e) {
            console.warn('Failed to persist shipping selection', e);
        }
    }

    if (shippingRadios) {
        shippingRadios.forEach(r => {
            r.addEventListener('change', function() {
                persistSelection(this.value);
                // also mark form inputs visual state
                shippingRadios.forEach(x => x.closest('label').classList.remove('active'));
                this.closest('label').classList.add('active');
            });
        });

        // Initial totals fetch
        refreshTotals();
    }
    
});
