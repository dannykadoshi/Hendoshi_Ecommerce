/* ================================================
   HENDOSHI - BATTLE VEST
   ================================================

   Purpose: Handles the Add-to-Cart modal flow for Battle Vest
   products. Fetches available variant options (sizes and colours)
   via AJAX, builds toggle button UI dynamically, manages quantity
   +/- controls, and submits the selected variant to the cart.

   Contains:
   - openAddToCartVestModal(productId) — fetches /products/{id}/variant-options/
   - Dynamic size/colour toggle button rendering
   - Quantity increment/decrement handlers
   - Add-to-cart form submission handler

   Dependencies: Fetch API (no external libraries)
   Load Order: Load on product detail and product listing pages
   ================================================ */

let vestProductId = null;
let vestProductName = '';
let vestSlugToRemove = null;

// Add to Cart Modal
window.openAddToCartVestModal = function(productId, productName) {
    vestProductId = productId;
    vestProductName = productName;
    document.getElementById('vestProductId').value = productId;

    fetch(`/products/${productId}/variant-options/`)
        .then(response => response.json())
        .then(data => {
            const sizeButtons = document.getElementById('vestSizeButtons');
            const colorButtons = document.getElementById('vestColorButtons');
            const sizeInput = document.getElementById('vestSizeInput');
            const colorInput = document.getElementById('vestColorInput');
            const sizeWrapper = document.getElementById('vestSizeWrapper');
            const colorWrapper = document.getElementById('vestColorWrapper');

            const uniqueSizes = [...new Set(data.sizes)];
            const uniqueColors = [...new Set(data.colors)];

            sizeButtons.innerHTML = '';
            colorButtons.innerHTML = '';
            sizeInput.value = '';
            colorInput.value = '';

            // Size toggle buttons
            if ((data.requires_size && uniqueSizes.length > 0) || uniqueSizes.length > 1) {
                sizeWrapper.style.display = 'block';
                uniqueSizes.forEach(s => {
                    const btn = document.createElement('button');
                    btn.type = 'button';
                    btn.className = 'size-btn';
                    btn.textContent = s.toUpperCase();
                    btn.dataset.value = s;
                    btn.addEventListener('click', function() {
                        sizeButtons.querySelectorAll('.size-btn').forEach(b => b.classList.remove('selected'));
                        this.classList.add('selected');
                        sizeInput.value = s;
                    });
                    sizeButtons.appendChild(btn);
                });
            } else {
                sizeWrapper.style.display = 'none';
                if (uniqueSizes.length === 1) sizeInput.value = uniqueSizes[0];
            }

            // Color toggle buttons
            if ((data.requires_color && uniqueColors.length > 0) || uniqueColors.length > 1) {
                colorWrapper.style.display = 'block';
                uniqueColors.forEach(c => {
                    const btn = document.createElement('button');
                    btn.type = 'button';
                    btn.className = 'color-btn';
                    btn.textContent = c.charAt(0).toUpperCase() + c.slice(1);
                    btn.dataset.value = c;
                    btn.dataset.color = c.toLowerCase();
                    btn.addEventListener('click', function() {
                        colorButtons.querySelectorAll('.color-btn').forEach(b => b.classList.remove('selected'));
                        this.classList.add('selected');
                        colorInput.value = c;
                    });
                    colorButtons.appendChild(btn);
                });
            } else {
                colorWrapper.style.display = 'none';
                if (uniqueColors.length === 1) colorInput.value = uniqueColors[0];
            }

            // Reset quantity
            document.getElementById('vestQuantitySelect').value = 1;

            const modal = new bootstrap.Modal(document.getElementById('addToCartVestModal'));
            modal.show();
        })
        .catch(() => {
            if (typeof showToast === 'function') {
                showToast('Could not load product options. Redirecting...', 'error');
            }
            var cards = document.querySelectorAll('.vest-item-card');
            var slug = null;
            cards.forEach(function(c) {
                if (c.innerHTML.indexOf('value="' + productId + '"') !== -1) {
                    slug = c.getAttribute('data-slug');
                }
            });
            window.location.href = slug ? `/products/${slug}/` : '/products/';
        });
};

// Remove Modal
window.openRemoveVestModal = function(slug) {
    vestSlugToRemove = slug;
    const modal = new bootstrap.Modal(document.getElementById('removeVestModal'));
    modal.show();
};

function removeFromVest(slug) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    fetch(`/products/${slug}/remove-from-vest/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const itemCard = document.querySelector(`[data-slug="${slug}"]`);
            if (itemCard) {
                itemCard.style.animation = 'fadeOut 0.3s ease-out';
                setTimeout(() => {
                    itemCard.remove();
                    const remainingItems = document.querySelectorAll('.vest-item-card');
                    if (remainingItems.length === 0) {
                        location.reload();
                    } else {
                        updateVestHeroStats();
                    }
                }, 300);
            }
            updateVestCount(data.item_count);
            if (typeof showToast === 'function') {
                showToast(data.message, 'info');
            }
        } else {
            if (typeof showToast === 'function') {
                showToast(data.message || 'Failed to remove item', 'info');
            }
            if (data.in_vest) {
                const itemCard = document.querySelector(`[data-slug="${slug}"]`);
                if (itemCard) {
                    itemCard.classList.add('in-vest');
                }
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        if (typeof showToast === 'function') {
            showToast('Failed to remove item from Battle Vest', 'error');
        }
    });
}

function updateVestHeroStats() {
    const remainingItems = document.querySelectorAll('.vest-item-card');
    const itemCount = remainingItems.length;
    
    let totalValue = 0;
    remainingItems.forEach(item => {
        const priceElement = item.querySelector('.vest-item-price');
        if (priceElement) {
            const priceText = priceElement.textContent.trim();
            const matches = priceText.match(/€([\d.]+)/g);
            if (matches && matches.length > 0) {
                const lastPrice = matches[matches.length - 1];
                const price = parseFloat(lastPrice.replace('€', ''));
                if (!isNaN(price)) {
                    totalValue += price;
                }
            }
        }
    });
    
    const itemCountElement = document.querySelector('.vest-hero-stat .fa-tshirt');
    if (itemCountElement && itemCountElement.parentElement) {
        itemCountElement.parentElement.innerHTML = `<i class="fas fa-tshirt"></i> ${itemCount} Item${itemCount !== 1 ? 's' : ''}`;
    }
    
    const totalValueElement = document.querySelector('.vest-hero-stat .fa-coins');
    if (totalValueElement && totalValueElement.parentElement) {
        totalValueElement.parentElement.innerHTML = `<i class="fas fa-coins"></i> Total Value: €${totalValue.toFixed(2)}`;
    }
}

function updateVestCount(count) {
    const mobileBadge = document.getElementById('battleVestCount');
    const desktopBadge = document.getElementById('battleVestCountDesktop');

    if (mobileBadge) {
        mobileBadge.textContent = count;
        mobileBadge.style.display = count > 0 ? 'flex' : 'none';
    }

    if (desktopBadge) {
        desktopBadge.textContent = count;
        desktopBadge.style.display = count > 0 ? 'flex' : 'none';
    }
}

function updateCartCount(count) {
    const cartBadge = document.getElementById('cartCountBadge');
    if (cartBadge) {
        cartBadge.textContent = count;
        cartBadge.style.display = count > 0 ? 'flex' : 'none';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // +/- quantity buttons
    const qtyMinus = document.querySelector('.vest-qty-minus');
    const qtyPlus = document.querySelector('.vest-qty-plus');
    const qtyInput = document.getElementById('vestQuantitySelect');

    if (qtyMinus && qtyInput) {
        qtyMinus.addEventListener('click', function() {
            const val = parseInt(qtyInput.value) || 1;
            if (val > 1) qtyInput.value = val - 1;
        });
    }
    if (qtyPlus && qtyInput) {
        qtyPlus.addEventListener('click', function() {
            const val = parseInt(qtyInput.value) || 1;
            if (val < 99) qtyInput.value = val + 1;
        });
    }

    // Add to Cart Form submit
    const addToCartVestForm = document.getElementById('addToCartVestForm');
    if (addToCartVestForm) {
        addToCartVestForm.onsubmit = function(e) {
            e.preventDefault();
            const productId = document.getElementById('vestProductId').value;
            const size = document.getElementById('vestSizeInput').value;
            const color = document.getElementById('vestColorInput').value;
            const quantity = document.getElementById('vestQuantitySelect').value;
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
                    // Show cart drawer with item details
                    if (typeof showCartDrawer === 'function') {
                        showCartDrawer(data);
                    } else if (typeof showToast === 'function') {
                        showToast(`${vestProductName} added to cart!`, 'success');
                    }
                    bootstrap.Modal.getInstance(document.getElementById('addToCartVestModal')).hide();
                    updateCartCount(data.cart_count);
                } else {
                    if (typeof showToast === 'function') {
                        showToast(data.message || 'Could not add to cart', 'info');
                    }
                }
            })
            .catch(() => {
                if (typeof showToast === 'function') {
                    showToast('Could not add to cart', 'error');
                }
            });
        };
    }

    // Remove confirmation button
    const confirmBtn = document.getElementById('confirmRemoveVestBtn');
    if (confirmBtn) {
        confirmBtn.onclick = function() {
            if (vestSlugToRemove) {
                removeFromVest(vestSlugToRemove);
                vestSlugToRemove = null;
                bootstrap.Modal.getInstance(document.getElementById('removeVestModal')).hide();
            }
        };
    }

    // Add fadeOut animation style
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeOut {
            from { opacity: 1; transform: scale(1); }
            to { opacity: 0; transform: scale(0.9); }
        }
    `;
    document.head.appendChild(style);
});
