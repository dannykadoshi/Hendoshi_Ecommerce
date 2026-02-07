/**
 * Payment Page JavaScript
 * Handles cart totals updates, shipping rate selection, and order summary synchronization
 */

(function() {
    'use strict';

    // Get the totals URL from data attribute
    const paymentContainer = document.querySelector('.checkout-page');
    const totalsUrl = paymentContainer?.dataset.totalsUrl;

    if (!totalsUrl) {
        console.warn('Payment: Totals URL not found');
    }

    /**
     * Format amount as currency
     * @param {number|string} amount - Amount to format
     * @returns {string} Formatted currency string
     */
    function formatMoney(amount) {
        return '€' + Number(amount).toFixed(2);
    }

    /**
     * Update order summary totals in the UI
     * @param {Object} data - Cart totals data from server
     */
    function updateTotals(data) {
        try {
            // Update subtotal
            const subtotalEl = document.getElementById('summary-subtotal');
            if (subtotalEl) {
                subtotalEl.textContent = formatMoney(data.cart_subtotal);
            }

            // Shipping handling - always show shipping row
            const shippingRow = document.getElementById('shipping-row');
            const shippingAmountEl = document.getElementById('summary-shipping-amount');
            if (shippingRow && shippingAmountEl) {
                if (typeof data.shipping_cost !== 'undefined' && Number(data.shipping_cost) > 0) {
                    shippingAmountEl.innerHTML = formatMoney(data.shipping_cost);
                } else {
                    shippingAmountEl.innerHTML = '<span class="text-success fw-bold">FREE</span>';
                }
                shippingRow.style.display = '';
            }

            // Discount handling
            const discountRow = document.getElementById('discount-row');
            if (data.discount_amount && Number(data.discount_amount) > 0) {
                if (discountRow) {
                    const discountValueEl = document.getElementById('summary-discount-value');
                    if (discountValueEl) {
                        discountValueEl.textContent = '-' + formatMoney(data.discount_amount).replace('€', '');
                    }
                    
                    if (data.discount_code) {
                        const discountCodeEl = document.getElementById('summary-discount-code');
                        if (discountCodeEl) {
                            discountCodeEl.textContent = data.discount_code;
                        }
                    }
                    
                    discountRow.style.display = '';
                }
            } else {
                if (discountRow) {
                    discountRow.style.display = 'none';
                }
            }

            // Update total
            const totalEl = document.getElementById('summary-total-amount');
            if (totalEl) {
                totalEl.textContent = formatMoney(data.cart_total);
            }

            // Update pay button amount if present (keep icon/text structure)
            const submitBtn = document.getElementById('submitPayment');
            if (submitBtn) {
                const payAmount = submitBtn.querySelector('.pay-amount');
                if (payAmount) {
                    payAmount.textContent = formatMoney(data.cart_total);
                } else {
                    // fallback for older markup
                    const defaultText = submitBtn.querySelector('.default-text');
                    if (defaultText) {
                        defaultText.textContent = 'Pay ' + formatMoney(data.cart_total);
                    }
                }
            }

            // Update item count badge in summary header if present
            const badge = document.getElementById('summary-item-count');
            if (badge && typeof data.cart_total_items !== 'undefined') {
                badge.textContent = data.cart_total_items + ' item' + (data.cart_total_items !== 1 ? 's' : '');
            }
        } catch (e) {
            console.warn('Payment: updateTotals failed', e);
        }
    }

    /**
     * Fetch latest cart totals from server
     */
    async function fetchTotals() {
        if (!totalsUrl) return;

        try {
            const resp = await fetch(totalsUrl, {
                credentials: 'same-origin',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!resp.ok) return;

            const data = await resp.json();
            updateTotals(data);
        } catch (e) {
            console.warn('Payment: Could not fetch cart totals', e);
        }
    }

    /**
     * Initialize shipping rate selection modal
     */
    function initShippingModal() {
        const shippingModal = document.getElementById('shippingModal');
        if (!shippingModal) return;

        const confirmBtn = document.getElementById('confirmShippingBtn');
        const radios = document.querySelectorAll('.shipping-rate-radio-modal');
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;
        
        // Get update URL from data attribute
        const updateUrl = shippingModal.dataset.updateUrl;
        const orderData = {
            subtotal: parseFloat(shippingModal.dataset.orderSubtotal || '0'),
            discountAmount: parseFloat(shippingModal.dataset.orderDiscount || '0'),
            itemCount: parseInt(shippingModal.dataset.orderItems || '0', 10)
        };

        if (!updateUrl) {
            console.warn('Payment: Shipping update URL not found');
            return;
        }

        // Handle confirm button
        if (confirmBtn) {
            confirmBtn.addEventListener('click', async function() {
                const selectedRadio = document.querySelector('.shipping-rate-radio-modal:checked');
                if (!selectedRadio) {
                    if (window.showToast) {
                        window.showToast('Please select a shipping rate', 'warning');
                    } else {
                        alert('Please select a shipping rate.');
                    }
                    return;
                }

                const selectedId = selectedRadio.value;
                
                try {
                    const resp = await fetch(updateUrl, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrfToken,
                            'Content-Type': 'application/x-www-form-urlencoded'
                        },
                        body: `selected_shipping_id=${encodeURIComponent(selectedId)}`
                    });

                    if (!resp.ok) {
                        const error = await resp.json().catch(() => ({}));
                        const errorMsg = error.error || 'Failed to update shipping';
                        
                        if (window.showToast) {
                            window.showToast(errorMsg, 'error');
                        } else {
                            alert('Error: ' + errorMsg);
                        }
                        return;
                    }

                    const data = await resp.json();
                    
                    // Update the UI with new shipping cost
                    updateTotals({
                        cart_subtotal: orderData.subtotal,
                        shipping_cost: data.shipping_cost,
                        discount_amount: orderData.discountAmount,
                        cart_total: data.total_amount,
                        cart_total_items: orderData.itemCount
                    });

                    // Update Stripe PaymentIntent if needed
                    if (window.stripe && data.client_secret) {
                        // The stripe-payment.js file should handle PaymentIntent updates
                        // if the amount has changed
                    }

                    // Close modal
                    const modalInstance = bootstrap.Modal.getInstance(shippingModal);
                    if (modalInstance) {
                        modalInstance.hide();
                    }

                    // Show success message
                    if (window.showToast) {
                        window.showToast('Shipping rate updated successfully', 'success');
                    }

                } catch (e) {
                    console.error('Payment: Failed to update shipping', e);
                    
                    if (window.showToast) {
                        window.showToast('Failed to update shipping. Please try again.', 'error');
                    } else {
                        alert('Failed to update shipping. Please try again.');
                    }
                }
            });
        }

        // Handle radio button changes for visual feedback
        radios.forEach(radio => {
            radio.addEventListener('change', function() {
                // Remove active class from all labels
                document.querySelectorAll('#shippingModal .list-group-item').forEach(item => {
                    item.classList.remove('active');
                });
                // Add active class to selected label
                const parentItem = this.closest('.list-group-item');
                if (parentItem) {
                    parentItem.classList.add('active');
                }
            });
        });
    }

    /**
     * Initialize prominent shipping selector on payment page
     */
    function initProminentShippingSelector() {
        const radios = document.querySelectorAll('.shipping-rate-radio-payment');
        if (radios.length === 0) return;

        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;
        const paymentForm = document.getElementById('paymentForm');
        const orderNumber = paymentForm?.dataset.orderNumber;
        
        if (!orderNumber) {
            console.warn('Payment: Order number not found');
            return;
        }

        const updateUrl = `/checkout/update-shipping/${orderNumber}/`;

        radios.forEach(radio => {
            radio.addEventListener('change', async function() {
                const selectedId = this.value;
                
                // Remove selected class from all options
                document.querySelectorAll('.shipping-rate-option').forEach(option => {
                    option.classList.remove('selected');
                });
                
                // Add selected class to current option
                const parentOption = this.closest('.shipping-rate-option');
                if (parentOption) {
                    parentOption.classList.add('selected');
                }

                // Update shipping on backend
                try {
                    const resp = await fetch(updateUrl, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrfToken,
                            'Content-Type': 'application/x-www-form-urlencoded'
                        },
                        body: `selected_shipping_id=${encodeURIComponent(selectedId)}`
                    });

                    if (!resp.ok) {
                        throw new Error('Failed to update shipping');
                    }

                    const data = await resp.json();
                    
                    // Fetch and update totals
                    fetchTotals();

                    // Show success message
                    if (window.showToast) {
                        window.showToast('Shipping updated', 'success');
                    }

                } catch (e) {
                    console.error('Payment: Failed to update shipping', e);
                    
                    if (window.showToast) {
                        window.showToast('Failed to update shipping. Please try again.', 'error');
                    }
                }
            });
        });
    }

    /**
     * Initialize polling for cart totals updates
     */
    function initPolling() {
        // Fetch on load
        fetchTotals();

        // Fetch when the page becomes visible (user switched back to this tab)
        document.addEventListener('visibilitychange', function() {
            if (document.visibilityState === 'visible') {
                fetchTotals();
            }
        });

        // Also fetch on window focus
        window.addEventListener('focus', fetchTotals);

        // Poll every 30s while page is visible
        setInterval(function() {
            if (document.visibilityState === 'visible') {
                fetchTotals();
            }
        }, 30000);
    }

    /**
     * Initialize all payment page functionality
     */
    function init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                initProminentShippingSelector();
                initShippingModal();
                initPolling();
            });
        } else {
            initProminentShippingSelector();
            initShippingModal();
            initPolling();
        }
    }

    // Start initialization
    init();

})();
