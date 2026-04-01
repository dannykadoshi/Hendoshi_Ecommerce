/* ================================================
   HENDOSHI - SHOPPING CART PAGE
   ================================================

   Purpose: Manages all cart page interactions — quantity updates via AJAX,
            item removal with confirmation modal, and live total/badge sync

   Contains:
   - incrementQty() / decrementQty() — adjust quantity inputs with stock-limit checks
   - updateCartAjax() — AJAX POST to update item quantity; updates subtotals, totals, and cart badge
   - confirmRemove() — shows a Bootstrap confirmation modal before item removal
   - updateCartCountBadge() — syncs the navbar cart badge count after any change
   - syncCheckoutButtons() — enables/disables checkout buttons based on cart item count

   Dependencies: base.js (showToast), Bootstrap 5 (Modal)
   Load Order: Load on cart page only
   ================================================ */

(function() {
    'use strict';

    // Initial cart count from Django template (will be set via data attribute)
    let cartContainer = null;
    let initialCartCount = 0;
    
    // Helper to get cart container (may not exist immediately)
    function getCartContainer() {
        if (!cartContainer) {
            // Try cart-page-layout first (new structure), then fall back to cart-container
            cartContainer = document.querySelector('.cart-page-layout') || document.querySelector('.cart-container');
        }
        return cartContainer;
    }

    /**
     * Get CSRF token from cookies
     */
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    /**
     * Increment quantity in cart item
     */
    window.incrementQty = function(button) {
        const input = button.parentElement.querySelector('.qty-input-sm');
        const max = parseInt(input.getAttribute('data-max')) || parseInt(input.max);
        const currentValue = parseInt(input.value);
        
        if (currentValue < max) {
            input.value = currentValue + 1;
            updateCartAjax(button);
        } else {
            if (typeof showToast === 'function') {
                showToast('Maximum stock reached', 'warning');
            }
        }
    };

    /**
     * Decrement quantity in cart item
     */
    window.decrementQty = function(button) {
        const input = button.parentElement.querySelector('.qty-input-sm');
        const min = parseInt(input.min);
        const currentValue = parseInt(input.value);
        
        if (currentValue > min) {
            input.value = currentValue - 1;
            updateCartAjax(button);
        }
    };

    /**
     * Update cart via AJAX when quantity changes
     */
    function updateCartAjax(button) {
        const form = button.closest('.quantity-form');
        const formData = new FormData(form);
        const itemId = form.getAttribute('data-item-id');
        
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update item subtotal
                const subtotalElement = document.querySelector(`.subtotal-value[data-item-id="${itemId}"]`);
                if (subtotalElement && data.item_total) {
                    subtotalElement.textContent = '€' + data.item_total.toFixed(2);
                }
                
                // Update cart totals (use cart_total if backend returned adjusted total)
                if (data.cart_subtotal !== undefined) {
                    const cartSubtotal = document.getElementById('cart-subtotal');
                    if (cartSubtotal) {
                        cartSubtotal.textContent = '€' + data.cart_subtotal.toFixed(2);
                    }
                }
                const totalToShow = (data.cart_total !== undefined) ? data.cart_total : data.cart_subtotal;
                if (totalToShow !== undefined) {
                    const cartTotal = document.getElementById('cart-total');
                    if (cartTotal) {
                        cartTotal.textContent = '€' + totalToShow.toFixed(2);
                    }
                    // Update mobile checkout bar total
                    const mobileTotal = document.getElementById('mobile-cart-total');
                    if (mobileTotal) {
                        mobileTotal.textContent = '€' + totalToShow.toFixed(2);
                    }
                }

                // Also update hero subtotal at top of page
                if (data.cart_subtotal !== undefined) {
                    const hero = document.getElementById('hero-subtotal');
                    if (hero) {
                        hero.textContent = data.cart_subtotal.toFixed(2);
                    }
                }

                // Update saved amount (discount) if available or compute from subtotal/total
                let discountAmount;
                if (data.discount_amount !== undefined) {
                    discountAmount = parseFloat(data.discount_amount);
                } else if (data.cart_subtotal !== undefined && data.cart_total !== undefined) {
                    discountAmount = parseFloat((data.cart_subtotal - data.cart_total).toFixed(2));
                }
                if (discountAmount !== undefined) {
                    const savedEl = document.getElementById('savedAmount');
                    if (savedEl) {
                        savedEl.textContent = discountAmount.toFixed(2);
                    }
                }

                // Update cart count in navbar
                updateCartCountBadge(data.cart_total_items);

                syncCheckoutButtons(data.cart_total_items);

                if (typeof showToast === 'function') {
                    showToast('Cart updated successfully', 'success');
                }
            } else if (data.error) {
                if (typeof showToast === 'function') {
                    showToast(data.error, 'error');
                }
                // Reset to previous value
                location.reload();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            if (typeof showToast === 'function') {
                showToast('Failed to update cart', 'error');
            }
        });
    }

    /**
     * Confirm item removal with custom modal
     */
    window.confirmRemove = function(event, itemId, productName) {
        event.preventDefault();
        
        // Find the link element using the item ID
        const link = document.querySelector(`a.remove-link[data-item-id="${itemId}"]`);
        if (!link) {
            console.error('Remove link not found for item:', itemId);
            return false;
        }
        
        // Store the link data for execution
        window.pendingRemovalLink = link;
        window.pendingRemovalItemId = itemId;
        
        // Show custom confirmation modal
        showConfirmationModal(`Are you sure you want to remove "${productName}" from your cart?`);
        
        return false;
    };

    /**
     * Show confirmation modal
     */
    function showConfirmationModal(message) {
        const messageEl = document.getElementById('confirmationMessage');
        if (messageEl) {
            messageEl.textContent = message;
        }
        const modal = document.getElementById('confirmationModal');
        if (modal) {
            modal.classList.remove('d-none');
            modal.style.display = 'flex';
        }
    }

    /**
     * Close confirmation modal
     */
    window.closeConfirmationModal = function() {
        const modal = document.getElementById('confirmationModal');
        if (modal) {
            modal.classList.add('d-none');
            modal.style.display = 'none';
        }
        window.pendingRemovalLink = null;
        window.pendingRemovalItemId = null;
    };

    /**
     * Execute confirmed removal action
     */
    window.executeConfirmation = function() {
        const link = window.pendingRemovalLink;
        const itemId = window.pendingRemovalItemId;
        
        if (!link || !itemId) return;
        
        closeConfirmationModal();
        
        fetch(link.href, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Remove cart item from DOM with animation
                const cartItem = document.querySelector(`.cart-card[data-item-id="${itemId}"]`);
                if (cartItem) {
                    cartItem.style.opacity = '0';
                    cartItem.style.transform = 'translateX(-20px)';
                    setTimeout(() => {
                        cartItem.remove();
                        
                        // Check if cart is now empty
                        const remainingItems = document.querySelectorAll('.cart-card');
                        if (remainingItems.length === 0) {
                            location.reload();
                        }
                    }, 300);
                }
                
                // Update cart totals (use adjusted cart_total if provided)
                if (data.cart_subtotal !== undefined) {
                    const cartSubtotal = document.getElementById('cart-subtotal');
                    if (cartSubtotal) {
                        cartSubtotal.textContent = '€' + data.cart_subtotal.toFixed(2);
                    }
                    const hero = document.getElementById('hero-subtotal');
                    if (hero) {
                        hero.textContent = data.cart_subtotal.toFixed(2);
                    }
                }
                const newTotal = (data.cart_total !== undefined) ? data.cart_total : data.cart_subtotal;
                if (newTotal !== undefined) {
                    const cartTotal = document.getElementById('cart-total');
                    if (cartTotal) {
                        cartTotal.textContent = '€' + newTotal.toFixed(2);
                    }
                    // Update mobile checkout bar total
                    const mobileTotal = document.getElementById('mobile-cart-total');
                    if (mobileTotal) {
                        mobileTotal.textContent = '€' + newTotal.toFixed(2);
                    }
                }

                // Update saved amount when item removed
                let removedDiscount;
                if (data.discount_amount !== undefined) {
                    removedDiscount = parseFloat(data.discount_amount);
                } else if (data.cart_subtotal !== undefined && data.cart_total !== undefined) {
                    removedDiscount = parseFloat((data.cart_subtotal - data.cart_total).toFixed(2));
                }
                if (removedDiscount !== undefined) {
                    const savedEl = document.getElementById('savedAmount');
                    if (savedEl) {
                        savedEl.textContent = removedDiscount.toFixed(2);
                    }
                }
                
                // Update cart count in navbar
                updateCartCountBadge(data.cart_total_items);

                // Update cart item count header
                const cartHeader = document.querySelector('.cart-item-count');
                if (cartHeader) {
                    const itemText = data.cart_total_items === 1 ? 'item' : 'items';
                    cartHeader.textContent = `${data.cart_total_items} ${itemText}`;
                }

                syncCheckoutButtons(data.cart_total_items);
                
                if (typeof showToast === 'function') {
                    showToast(data.message, 'success');
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            if (typeof showToast === 'function') {
                showToast('Failed to remove item', 'error');
            }
        });
    };

    /**
     * Update cart count badge in navbar
     */
    function updateCartCountBadge(count) {
        const cartBadge = document.getElementById('cartCountBadge');
        if (cartBadge) {
            cartBadge.textContent = count;
            // Use the same badge-hidden class as base-global.js
            if (count > 0) {
                cartBadge.classList.remove('badge-hidden');
            } else {
                cartBadge.classList.add('badge-hidden');
            }
        }
    }

    /**
     * Enable/disable checkout buttons based on cart state
     */
    function syncCheckoutButtons(totalItems) {
        // console.log('syncCheckoutButtons called with totalItems:', totalItems);
        const disabled = totalItems <= 0;
        // console.log('Button should be disabled:', disabled);
        document.querySelectorAll('.checkout-btn').forEach(btn => {
            // console.log('Processing checkout button:', btn);
            if (disabled) {
                btn.classList.add('disabled');
                btn.setAttribute('aria-disabled', 'true');
                btn.setAttribute('tabindex', '-1');
                // console.log('Button disabled');
            } else {
                btn.classList.remove('disabled');
                btn.setAttribute('aria-disabled', 'false');
                btn.setAttribute('tabindex', '0');
                // console.log('Button enabled');
            }
        });
    }

    /**
     * Sync mobile checkout buttons with cart state
     */
    function syncMobileCheckout(totalItems) {
        const disabled = totalItems <= 0;
        document.querySelectorAll('.mobile-checkout-btn').forEach(btn => {
            btn.classList.toggle('disabled', disabled);
            if (disabled) {
                btn.setAttribute('aria-disabled', 'true');
                btn.setAttribute('tabindex', '-1');
            } else {
                btn.removeAttribute('aria-disabled');
                btn.removeAttribute('tabindex');
            }
        });
    }

    /**
     * Apply discount/promo code
     */
    window.applyCoupon = async function(event) {
        event.preventDefault();
        const codeInput = document.getElementById('couponCode');
        const code = codeInput ? codeInput.value.trim() : '';
        const messageEl = document.getElementById('couponMessage');
        const applyBtn = document.querySelector('.coupon-apply-btn');

        if (!code) {
            if (messageEl) messageEl.textContent = 'Enter a promo code.';
            return false;
        }

        // Show loading spinner
        if (applyBtn) {
            applyBtn.disabled = true;
            const btnText = applyBtn.querySelector('.btn-text');
            const btnSpinner = applyBtn.querySelector('.btn-spinner');
            if (btnText) btnText.classList.add('d-none');
            if (btnSpinner) btnSpinner.classList.remove('d-none');
        }

        const formData = new URLSearchParams();
        formData.append('discount_code', code);

        // Get apply discount URL from data attribute
        const container = getCartContainer();
        const applyUrl = container ? container.dataset.applyDiscountUrl : '';
        
        if (!applyUrl) {
            console.error('Apply discount URL not found');
            if (typeof showToast === 'function') showToast('Configuration error. Please refresh the page.', 'error');
            if (applyBtn) {
                applyBtn.disabled = false;
                const btnText = applyBtn.querySelector('.btn-text');
                const btnSpinner = applyBtn.querySelector('.btn-spinner');
                if (btnText) btnText.classList.remove('d-none');
                if (btnSpinner) btnSpinner.classList.add('d-none');
            }
            return false;
        }

        try {
            const response = await fetch(applyUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: formData.toString()
            });
            
            // Check if response is ok
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const resp = await response.json();

            if (resp.success) {
                // Update totals without reload
                const cartSubtotal = document.getElementById('cart-subtotal');
                const cartTotal = document.getElementById('cart-total');
                const mobileTotal = document.getElementById('mobile-cart-total');
                const hero = document.getElementById('hero-subtotal');
                
                if (cartSubtotal) cartSubtotal.textContent = '€' + parseFloat(resp.cart_subtotal).toFixed(2);
                if (cartTotal) cartTotal.textContent = '€' + parseFloat(resp.cart_total).toFixed(2);
                if (mobileTotal) mobileTotal.textContent = '€' + parseFloat(resp.cart_total).toFixed(2);
                if (hero) hero.textContent = parseFloat(resp.cart_subtotal).toFixed(2);

                // Replace the coupon form with applied coupon UI
                const discountCode = resp.code || resp.discount_code || code;
                const promoSection = document.querySelector('.summary-promo');
                if (promoSection) {
                    promoSection.innerHTML = `
                        <div class="promo-applied">
                            <div class="promo-info">
                                <i class="fas fa-tag"></i>
                                <span>${discountCode}</span>
                                <span class="promo-savings">-€<span id="savedAmount">${parseFloat(resp.discount_amount).toFixed(2)}</span></span>
                            </div>
                            <button type="button" id="removeCouponBtn" class="promo-remove"><i class="fas fa-times"></i></button>
                        </div>
                    `;
                }

                // Update cart count and sync checkout buttons
                if (resp.cart_count !== undefined) {
                    updateCartCountBadge(resp.cart_count);
                    syncCheckoutButtons(resp.cart_count);
                    syncMobileCheckout(resp.cart_count);
                }

                if (typeof showToast === 'function') showToast(resp.message || 'Discount applied!', 'success');
            } else {
                if (typeof showToast === 'function') showToast(resp.error || 'Invalid code.', 'error');
                
                // Reset button state on error only (on success, button is replaced)
                if (applyBtn) {
                    applyBtn.disabled = false;
                    const btnText = applyBtn.querySelector('.btn-text');
                    const btnSpinner = applyBtn.querySelector('.btn-spinner');
                    if (btnText) btnText.classList.remove('d-none');
                    if (btnSpinner) btnSpinner.classList.add('d-none');
                }
            }
        } catch (error) {
            console.error('Coupon apply error:', error);
            if (typeof showToast === 'function') showToast('Network error. Please try again.', 'error');
            
            // Reset button on error
            if (applyBtn) {
                applyBtn.disabled = false;
                const btnText = applyBtn.querySelector('.btn-text');
                const btnSpinner = applyBtn.querySelector('.btn-spinner');
                if (btnText) btnText.classList.remove('d-none');
                if (btnSpinner) btnSpinner.classList.add('d-none');
            }
        }

        return false;
    };

    /**
     * Remove discount code handler
     */
    function handleRemoveCoupon() {
        const container = getCartContainer();
        const removeUrl = container ? container.dataset.removeDiscountUrl : '';
        
        if (!removeUrl) {
            console.error('Remove discount URL not found');
            if (typeof showToast === 'function') showToast('Configuration error. Please refresh the page.', 'error');
            return;
        }
        
        fetch(removeUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        }).then(r => r.json()).then(data => {
            if (data && data.success) {
                // Update totals without reload
                const newSubtotal = data.cart_subtotal || data.new_total;
                const newTotal = data.cart_total || data.new_total || newSubtotal;

                if (newSubtotal !== undefined) {
                    const cartSubtotal = document.getElementById('cart-subtotal');
                    if (cartSubtotal) {
                        cartSubtotal.textContent = '€' + parseFloat(newSubtotal).toFixed(2);
                    }
                    const hero = document.getElementById('hero-subtotal');
                    if (hero) {
                        hero.textContent = parseFloat(newSubtotal).toFixed(2);
                    }
                }
                if (newTotal !== undefined) {
                    const cartTotal = document.getElementById('cart-total');
                    if (cartTotal) {
                        cartTotal.textContent = '€' + parseFloat(newTotal).toFixed(2);
                    }
                    const mobileTotal = document.getElementById('mobile-cart-total');
                    if (mobileTotal) {
                        mobileTotal.textContent = '€' + parseFloat(newTotal).toFixed(2);
                    }
                }

                // Replace applied coupon with form
                const promoSection = document.querySelector('.summary-promo');
                if (promoSection) {
                    promoSection.innerHTML = `
                        <form id="couponForm" class="promo-form" onsubmit="return applyCoupon(event)">
                            <input type="hidden" name="csrfmiddlewaretoken" value="${getCookie('csrftoken')}">
                            <label for="couponCode" class="sr-only">Enter promo code</label>
                            <input type="text" id="couponCode" name="discount_code" placeholder="Promo code" aria-label="Enter promo code">
                            <button type="submit" class="promo-btn" aria-label="Apply coupon code">
                                <span class="btn-text">Apply</span>
                                <span class="btn-spinner d-none"><span class="spinner-border spinner-border-sm"></span></span>
                            </button>
                        </form>
                        <div id="couponMessage" class="promo-message"></div>
                    `;
                }

                // Update cart count and sync checkout buttons
                if (data.cart_count !== undefined) {
                    updateCartCountBadge(data.cart_count);
                    syncCheckoutButtons(data.cart_count);
                    syncMobileCheckout(data.cart_count);
                }

                if (typeof showToast === 'function') showToast(data.message || 'Discount removed', 'success');
            } else {
                if (typeof showToast === 'function') showToast(data.message || 'No discount to remove', 'warning');
            }
        }).catch((err) => {
            console.error('Error removing coupon:', err);
            if (typeof showToast === 'function') showToast('Error removing discount', 'error');
        });
    }

    /**
     * Initialize cart functionality on DOM ready
     */
    document.addEventListener('DOMContentLoaded', function() {
        // Get initial cart count from data attribute now that DOM is ready
        const container = getCartContainer();
        if (container) {
            initialCartCount = parseInt(container.dataset.initialCartCount || '0');
            // console.log('Initial cart count from data attribute:', initialCartCount);
        } else {
            // console.log('Cart container not found');
        }
        
        // console.log('DOMContentLoaded fired, initialCartCount:', initialCartCount);
        syncCheckoutButtons(initialCartCount);
        syncMobileCheckout(initialCartCount);

        // Add click handler to all checkout buttons to check disabled state
        document.addEventListener('click', function(e) {
            const checkoutBtn = e.target.closest('.checkout-btn');
            if (checkoutBtn && checkoutBtn.classList.contains('disabled')) {
                // console.log('Preventing click on disabled checkout button');
                e.preventDefault();
                if (typeof showToast === 'function') {
                    showToast('Add items to your cart to proceed to checkout.', 'warning');
                }
            } else if (checkoutBtn) {
                // console.log('Checkout button clicked and enabled, allowing navigation');
            }
        });

        // Handle manual input change
        document.querySelectorAll('.qty-input-sm').forEach(input => {
            input.addEventListener('change', function() {
                const button = this.parentElement.querySelector('.qty-btn-sm');
                updateCartAjax(button);
            });
        });

        // Remove coupon button click handler (event delegation)
        document.addEventListener('click', function(e) {
            // Use closest() to handle clicks on the icon inside the button
            if (e.target && e.target.closest('#removeCouponBtn')) {
                handleRemoveCoupon();
            }
        });
    });

})();
