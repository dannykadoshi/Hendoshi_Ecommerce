/**
 * Quick Add Modal - Shared functionality
 * Used by: products.html, sale.html, new_drops.html, design_products.html
 */

document.addEventListener('DOMContentLoaded', function() {
    const quickAddModal = document.getElementById('quickAddModalUnified');
    if (!quickAddModal) return;

    const quickAddForm = document.getElementById('quickAddFormUnified');
    const quickAddProductId = document.getElementById('quickAddProductId');
    const quickAddSizeButtons = document.getElementById('quickAddSizeButtons');
    const quickAddColorButtons = document.getElementById('quickAddColorButtons');
    const quickAddSizeInput = document.getElementById('quickAddSizeInput');
    const quickAddColorInput = document.getElementById('quickAddColorInput');
    const quickAddSizeWrapper = document.getElementById('quickAddSizeWrapper');
    const quickAddColorWrapper = document.getElementById('quickAddColorWrapper');
    const quickAddQuantitySelect = document.getElementById('quickAddQuantitySelect');
    const quickAddModalTitle = document.getElementById('quickAddModalTitle');

    // Quantity controls
    const qtyMinus = document.querySelector('.quick-add-qty-minus');
    const qtyPlus = document.querySelector('.quick-add-qty-plus');
    
    if (qtyMinus) {
        qtyMinus.addEventListener('click', function() {
            const input = quickAddQuantitySelect;
            const currentVal = parseInt(input.value) || 1;
            if (currentVal > 1) {
                input.value = currentVal - 1;
            }
        });
    }
    
    if (qtyPlus) {
        qtyPlus.addEventListener('click', function() {
            const input = quickAddQuantitySelect;
            const currentVal = parseInt(input.value) || 1;
            const maxVal = parseInt(input.max) || 99;
            if (currentVal < maxVal) {
                input.value = currentVal + 1;
            }
        });
    }

    function initProductCardBindings(root) {
        const scope = root || document;

        // Handle both product-grid-add-bag-btn and carousel-add-cart-btn
        const quickAddBtns = scope.querySelectorAll('.product-grid-add-bag-btn:not([data-quickadd-bound]), .carousel-add-cart-btn:not([data-quickadd-bound])');
        quickAddBtns.forEach(btn => {
            btn.dataset.quickaddBound = 'true';
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                const productId = btn.getAttribute('data-product-id');
                const productSlug = btn.getAttribute('data-product-slug');
                const productName = btn.getAttribute('data-product-name');
                quickAddProductId.value = productId;
                quickAddModalTitle.textContent = `Add ${productName}`;

                fetch(`/products/${productId}/variant-options/`)
                    .then(response => response.json())
                    .then(data => {
                        quickAddSizeButtons.innerHTML = '';
                        quickAddColorButtons.innerHTML = '';
                        quickAddSizeInput.value = '';
                        quickAddColorInput.value = '';

                        const uniqueSizes = [...new Set(data.sizes)];
                        const uniqueColors = [...new Set(data.colors)];

                        // Create size buttons
                        if ((data.requires_size && uniqueSizes.length > 0) || uniqueSizes.length > 1) {
                            quickAddSizeWrapper.style.display = 'block';
                            uniqueSizes.forEach(s => {
                                const btn = document.createElement('button');
                                btn.type = 'button';
                                btn.className = 'size-btn';
                                btn.textContent = s.toUpperCase();
                                btn.dataset.value = s;
                                btn.addEventListener('click', function() {
                                    quickAddSizeButtons.querySelectorAll('.size-btn').forEach(b => b.classList.remove('selected'));
                                    this.classList.add('selected');
                                    quickAddSizeInput.value = s;
                                });
                                quickAddSizeButtons.appendChild(btn);
                            });
                        } else {
                            quickAddSizeWrapper.style.display = 'none';
                            if (uniqueSizes.length === 1) {
                                quickAddSizeInput.value = uniqueSizes[0];
                            }
                        }

                        // Create color buttons
                        if ((data.requires_color && uniqueColors.length > 0) || uniqueColors.length > 1) {
                            quickAddColorWrapper.style.display = 'block';
                            uniqueColors.forEach(c => {
                                const btn = document.createElement('button');
                                btn.type = 'button';
                                btn.className = 'color-btn';
                                btn.textContent = c.charAt(0).toUpperCase() + c.slice(1);
                                btn.dataset.value = c;
                                btn.dataset.color = c.toLowerCase();
                                btn.addEventListener('click', function() {
                                    quickAddColorButtons.querySelectorAll('.color-btn').forEach(b => b.classList.remove('selected'));
                                    this.classList.add('selected');
                                    quickAddColorInput.value = c;
                                });
                                quickAddColorButtons.appendChild(btn);
                            });
                        } else {
                            quickAddColorWrapper.style.display = 'none';
                            if (uniqueColors.length === 1) {
                                quickAddColorInput.value = uniqueColors[0];
                            }
                        }

                        const modal = new bootstrap.Modal(quickAddModal);
                        modal.show();
                    })
                    .catch(() => {
                        window.location.href = `/products/${productSlug}/`;
                    });
            });
        });

        // Battle vest button handling
        const vestButtons = scope.querySelectorAll('.product-vest-btn[data-product-slug]:not([data-vest-bound])');
        vestButtons.forEach(btn => {
            btn.dataset.vestBound = 'true';
            const slug = btn.dataset.productSlug;

            fetch(`/products/${slug}/check-in-vest/`)
                .then(response => response.json())
                .then(data => {
                    if (data.in_vest) {
                        btn.classList.add('in-vest');
                        btn.querySelector('i').classList.remove('far');
                        btn.querySelector('i').classList.add('fas');
                    }
                })
                .catch(error => console.error('Error checking vest:', error));

            btn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();

                const icon = this.querySelector('i');
                const isInVest = this.classList.contains('in-vest');
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

                const url = (isInVest ?
                    `/products/${slug}/remove-from-vest/` :
                    `/products/${slug}/add-to-vest/`);

                fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        if (isInVest) {
                            this.classList.remove('in-vest');
                            icon.classList.remove('fas');
                            icon.classList.add('far');
                        } else {
                            this.classList.add('in-vest');
                            icon.classList.remove('far');
                            icon.classList.add('fas');
                        }
                        // Update vest badge count
                        if (typeof data.item_count !== 'undefined') {
                            const vestBadges = document.querySelectorAll('.vest-count-badge');
                            vestBadges.forEach(badge => {
                                badge.textContent = String(data.item_count);
                                if (data.item_count > 0) {
                                    badge.classList.remove('badge-hidden');
                                } else {
                                    badge.classList.add('badge-hidden');
                                }
                            });
                        }
                        if (window.showToast) {
                            window.showToast(data.message, 'success');
                        }
                    }
                });
            });
        });
    }

    // Initialize on page load
    initProductCardBindings();

    // Form submission
    if (quickAddForm) {
        quickAddForm.onsubmit = function(e) {
            e.preventDefault();
            const productId = quickAddProductId.value;
            const size = quickAddSizeInput.value;
            const color = quickAddColorInput.value;
            const quantity = quickAddQuantitySelect.value;
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch(`/cart/add/${productId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: `size=${size}&color=${color}&quantity=${quantity}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    bootstrap.Modal.getInstance(quickAddModal).hide();
                    
                    // Update cart count
                    const cartBadges = document.querySelectorAll('.cart-count-badge');
                    cartBadges.forEach(badge => {
                        badge.textContent = data.cart_count;
                        if (data.cart_count > 0) {
                            badge.classList.remove('badge-hidden');
                        } else {
                            badge.classList.add('badge-hidden');
                        }
                    });

                    // Update vest count if returned from server
                    if (typeof data.item_count !== 'undefined') {
                        const vestBadges = document.querySelectorAll('.vest-count-badge');
                        vestBadges.forEach(badge => {
                            badge.textContent = String(data.item_count);
                            if (data.item_count > 0) {
                                badge.classList.remove('badge-hidden');
                            } else {
                                badge.classList.add('badge-hidden');
                            }
                        });
                    }
                    
                    // Show cart drawer with a small delay to avoid modal conflicts
                    setTimeout(() => {
                        if (window.showCartDrawer && data.item) {
                            window.showCartDrawer(data);
                        } else if (window.showToast) {
                            window.showToast('Added to cart!', 'success');
                        }
                    }, 300);
                } else {
                    if (window.showToast) {
                        window.showToast(data.message || 'Could not add to cart', 'error');
                    }
                }
            })
            .catch(() => {});
        };
    }

    // Make initProductCardBindings global for dynamic content
    window.initProductCardBindings = initProductCardBindings;
});
