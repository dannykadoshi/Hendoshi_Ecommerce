/**
 * Product Detail Page
 * Handles carousel interactions, vest toggles, and add to cart for carousels
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // Make carousel cards clickable
    function makeCarouselCardsClickable(containerSelector, itemSelector) {
        const container = document.querySelector(containerSelector);
        if (!container) return;

        // Use delegated listeners on the track to avoid per-item handlers
        container.addEventListener('click', function(e) {
            // Ignore clicks on real controls or links
            if (e.target.closest('a, button, .product-vest-btn, .edit-product-icon, .carousel-add-cart-btn')) return;
            const item = e.target.closest(itemSelector);
            if (!item) return;
            const link = item.querySelector('a[href*="/products/"]');
            if (link && link.href) {
                window.location.href = link.href;
            }
        });

        // Also handle touchend for mobile where click may be suppressed after drag
        container.addEventListener('touchend', function(e) {
            if (e.target.closest('a, button, .product-vest-btn, .edit-product-icon, .carousel-add-cart-btn')) return;
            const item = e.target.closest(itemSelector);
            if (!item) return;
            const link = item.querySelector('a[href*="/products/"]');
            if (link && link.href) {
                window.location.href = link.href;
            }
        }, {passive: true});
    }

    makeCarouselCardsClickable('#related-products-track', '.related-product-item');
    makeCarouselCardsClickable('#recently-viewed-products-track', '.recently-viewed-product-item');

    // Handle vest button clicks on carousel items
    document.addEventListener('click', function(e) {
        const vestBtn = e.target.closest('.product-vest-btn');
        if (!vestBtn) return;

        const productSlug = vestBtn.getAttribute('data-product-slug');
        if (!productSlug) return;

        const icon = vestBtn.querySelector('i');
        const isInVest = vestBtn.classList.contains('in-vest');

        fetch(`/vault/toggle_vest/${productSlug}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (isInVest) {
                    vestBtn.classList.remove('in-vest');
                    icon.classList.remove('fas');
                    icon.classList.add('far');
                } else {
                    vestBtn.classList.add('in-vest');
                    icon.classList.remove('far');
                    icon.classList.add('fas');
                }
                
                // Update vest badge count
                if (typeof data.vest_count !== 'undefined') {
                    const vestBadges = document.querySelectorAll('.vest-count-badge');
                    vestBadges.forEach(badge => {
                        badge.textContent = String(data.vest_count);
                        if (data.vest_count > 0) {
                            badge.style.display = 'flex';
                        } else {
                            badge.style.display = 'none';
                        }
                    });
                }
                
                if (window.showToast) {
                    window.showToast(data.message, 'success');
                }
            }
        })
        .catch(error => {});
    });

    // Handle add to cart clicks on carousel items
    document.addEventListener('click', function(e) {
        const addBtn = e.target.closest('.carousel-add-cart-btn');
        if (!addBtn) return;

        const productId = addBtn.getAttribute('data-product-id');
        const productName = addBtn.getAttribute('data-product-name');
        
        if (!productId) return;

        const formData = new FormData();
        formData.append('product_id', productId);
        formData.append('quantity', '1');

        fetch('/cart/add/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update cart count
                const cartBadges = document.querySelectorAll('.cart-count-badge');
                cartBadges.forEach(badge => {
                    badge.textContent = data.cart_count;
                    if (data.cart_count > 0) {
                        badge.style.display = 'flex';
                    }
                });
                
                // Show cart drawer
                if (window.showCartDrawer && data.item) {
                    window.showCartDrawer(data);
                } else if (window.showToast) {
                    window.showToast('Added to cart!', 'success');
                }
            } else {
                if (window.showToast) {
                    window.showToast(data.message || 'Could not add to cart', 'error');
                }
            }
        })
        .catch(error => {});
    });
});
