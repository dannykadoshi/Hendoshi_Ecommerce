/* ================================================
   HENDOSHI - PRODUCT DETAIL PAGE
   ================================================

   Purpose: Handles secondary product detail interactions — making related and
            recently-viewed carousel cards clickable, vest (wishlist) toggling, and
            quick add-to-cart from carousel items

   Contains:
   - makeCarouselCardsClickable() — delegated click/touchend handler to navigate to product URL
   - Vest toggle: AJAX POST to /vault/toggle_vest/{slug}/ with icon and badge count update
   - Carousel add-to-cart: AJAX POST to /cart/add/ for .carousel-add-cart-btn buttons

   Dependencies: base.js (showToast)
   Load Order: Load on product detail page only
   ================================================ */

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
        .catch(() => {});
    });

    // Handle add to cart clicks on carousel items
    document.addEventListener('click', function(e) {
        const addBtn = e.target.closest('.carousel-add-cart-btn');
        if (!addBtn) return;

        const productId = addBtn.getAttribute('data-product-id');
        
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
        .catch(() => {});
    });
});

// Carousel Battle Vest functionality
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is authenticated by looking for vest buttons
    const vestButtons = document.querySelectorAll('.product-vest-btn');
    if (vestButtons.length === 0) return;

    // Use event delegation for carousel heart buttons
    document.addEventListener('click', function(e) {
        if (e.target.closest('.product-vest-btn')) {
            e.preventDefault();
            const button = e.target.closest('.product-vest-btn');
            const productSlug = button.dataset.productSlug;

            const isInVest = button.classList.contains('in-vest');

            if (isInVest) {
                // Remove from vest
                removeFromVestCarousel(button, productSlug);
            } else {
                // Add to vest
                addToVestCarousel(button, productSlug);
            }
        }

        // Handle carousel add to cart buttons
        if (e.target.closest('.carousel-add-cart-btn')) {
            e.preventDefault();
            const button = e.target.closest('.carousel-add-cart-btn');
            const productId = button.dataset.productId;
            const productName = button.dataset.productName;
            openAddToCartCarouselModal(productId, productName);
        }
    });

    // Initialize carousel buttons on page load
    initializeCarouselButtons();

    function initializeCarouselButtons() {
        const carouselButtons = document.querySelectorAll('.product-vest-btn[data-product-slug]');

        carouselButtons.forEach(button => {
            const productSlug = button.dataset.productSlug;
            const heartIcon = button.querySelector('i');

            // Check if product is in vest
            fetch(`/products/${productSlug}/check-in-vest/`)
                .then(response => response.json())
                .then(data => {
                    if (data.in_vest) {
                        heartIcon.classList.remove('far');
                        heartIcon.classList.add('fas');
                        button.classList.add('in-vest');
                    }
                })
                .catch(error => console.error('Error checking vest for carousel:', error));
        });
    }

    function addToVestCarousel(button, productSlug) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const heartIcon = button.querySelector('i');

        fetch(`/products/${productSlug}/add-to-vest/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update button to filled heart
                heartIcon.classList.remove('far');
                heartIcon.classList.add('fas');
                button.classList.add('in-vest');

                // Show success toast
                showToast(data.message, 'success');

                // Update count
                updateVestCount(data.item_count);
            } else {
                showToast(data.message, 'info');
            }
        })
        .catch(error => {
            console.error('Error adding to vest from carousel:', error);
            showToast('Failed to add to Battle Vest', 'error');
        });
    }

    function removeFromVestCarousel(button, productSlug) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const heartIcon = button.querySelector('i');

        fetch(`/products/${productSlug}/remove-from-vest/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update button to outline heart
                heartIcon.classList.remove('fas');
                heartIcon.classList.add('far');
                button.classList.remove('in-vest');

                // Show info toast
                showToast(data.message, 'info');

                // Update count
                updateVestCount(data.item_count);
            } else {
                showToast(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error removing from vest from carousel:', error);
            showToast('Failed to remove from Battle Vest', 'error');
        });
    }

    function updateVestCount(count) {
        // Update both mobile and desktop count badges
        const mobileBadge = document.getElementById('battleVestCount');
        const desktopBadge = document.getElementById('battleVestCountDesktop');

        if (mobileBadge) {
            mobileBadge.textContent = count;
            mobileBadge.style.display = count > 0 ? 'inline-block' : 'none';
        }

        if (desktopBadge) {
            desktopBadge.textContent = count;
            desktopBadge.style.display = count > 0 ? 'inline-block' : 'none';
        }
    }

    // Modal logic for Add to Cart from Carousel
    let carouselProductId = null;
    let carouselProductName = '';
    function openAddToCartCarouselModal(productId, productName) {
        carouselProductId = productId;
        carouselProductName = productName;

        const carouselProductIdElement = document.getElementById('carouselProductId');
        if (carouselProductIdElement) {
            carouselProductIdElement.value = productId;
        }

        // Fetch available sizes/colors via AJAX
        fetch(`/products/${productId}/variant-options/`)
            .then(response => response.json())
            .then(data => {
                const sizeSelect = document.getElementById('carouselSizeSelect');
                const colorSelect = document.getElementById('carouselColorSelect');
                const sizeWrapper = document.getElementById('carouselSizeWrapper');
                const colorWrapper = document.getElementById('carouselColorWrapper');

                if (!sizeSelect || !colorSelect || !sizeWrapper || !colorWrapper) {
                    return; // Exit if carousel elements don't exist
                }

                // Deduplicate sizes and colors
                const uniqueSizes = [...new Set(data.sizes)];
                const uniqueColors = [...new Set(data.colors)];

                sizeSelect.innerHTML = '';
                colorSelect.innerHTML = '';

                // Show size field if: required by ProductType OR multiple sizes exist
                // This allows products to have optional size choices even if type doesn't require it
                if ((data.requires_size && uniqueSizes.length > 0) || uniqueSizes.length > 1) {
                    sizeWrapper.style.display = 'block';
                    sizeSelect.required = true;
                    uniqueSizes.forEach(s => {
                        sizeSelect.innerHTML += `<option value="${s}">${s.toUpperCase()}</option>`;
                    });
                } else {
                    sizeWrapper.style.display = 'none';
                    sizeSelect.required = false;
                    // Auto-select the only size if there is one
                    if (uniqueSizes.length === 1) {
                        sizeSelect.innerHTML = `<option value="${uniqueSizes[0]}">${uniqueSizes[0].toUpperCase()}</option>`;
                    }
                }

                // Show color field if: required by ProductType OR multiple colors exist
                if ((data.requires_color && uniqueColors.length > 0) || uniqueColors.length > 1) {
                    colorWrapper.style.display = 'block';
                    colorSelect.required = true;
                    uniqueColors.forEach(c => {
                        colorSelect.innerHTML += `<option value="${c}">${c.charAt(0).toUpperCase() + c.slice(1)}</option>`;
                    });
                } else {
                    colorWrapper.style.display = 'none';
                    colorSelect.required = false;
                    // Auto-select the only color if there is one
                    if (uniqueColors.length === 1) {
                        colorSelect.innerHTML = `<option value="${uniqueColors[0]}">${uniqueColors[0].charAt(0).toUpperCase() + uniqueColors[0].slice(1)}</option>`;
                    }
                }

                // Show modal
                const modalElement = document.getElementById('addToCartCarouselModal');
                if (modalElement) {
                    const modal = new bootstrap.Modal(modalElement);
                    modal.show();
                } else {
                    console.error('Modal element not found');
                }
            })
            .catch(() => {
                if (typeof showToast === 'function') {
                    showToast('Could not load product options. Redirecting...', 'error');
                }
                // Try to find the slug in the DOM for this product card
                var cards = document.querySelectorAll('.product-card');
                var slug = null;
                cards.forEach(function(c) {
                    var link = c.querySelector('a[href*="/products/"]');
                    if (link) {
                        var href = link.getAttribute('href');
                        var match = href.match(/\/products\/([^\/]+)\//);
                        if (match) {
                            slug = match[1];
                        }
                    }
                });
                if (slug) {
                    window.location.href = `/products/${slug}/`;
                } else {
                    window.location.href = '/products/';
                }
            });
    }

    // Handle form submission for carousel add to cart
    const carouselForm = document.getElementById('addToCartCarouselForm');
    if (carouselForm) {
        carouselForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = new FormData(this);

            fetch('/cart/add/' + carouselProductId + '/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Close modal properly
                    const modalElement = document.getElementById('addToCartCarouselModal');
                    const modalInstance = bootstrap.Modal.getInstance(modalElement);
                    if (modalInstance) {
                        modalInstance.hide();
                    }

                    // Remove any lingering backdrops
                    setTimeout(() => {
                        const backdrops = document.querySelectorAll('.modal-backdrop');
                        backdrops.forEach(backdrop => backdrop.remove());
                        document.body.classList.remove('modal-open');
                        document.body.style.overflow = '';
                        document.body.style.paddingRight = '';
                    }, 100);

                    // Update cart count first
                    if (typeof updateCartCount === 'function') {
                        updateCartCount(data.cart_count);
                    }

                    // Show cart drawer
                    setTimeout(() => {
                        if (typeof showCartDrawer === 'function' && data.item) {
                            showCartDrawer(data);
                        } else if (typeof showToast === 'function') {
                            showToast(data.message || 'Added to cart!', 'success');
                        }
                    }, 200);
                } else {
                    if (typeof showToast === 'function') {
                        showToast(data.message, 'error');
                    }
                }
            });
        });
    }
});
