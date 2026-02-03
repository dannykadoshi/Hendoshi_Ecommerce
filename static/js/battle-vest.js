/**
 * Battle Vest - Add to cart modal, remove items, update stats
 */

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
            const sizeSelect = document.getElementById('vestSizeSelect');
            const colorSelect = document.getElementById('vestColorSelect');
            const sizeWrapper = document.getElementById('vestSizeWrapper');
            const colorWrapper = document.getElementById('vestColorWrapper');

            const uniqueSizes = [...new Set(data.sizes)];
            const uniqueColors = [...new Set(data.colors)];

            sizeSelect.innerHTML = '';
            colorSelect.innerHTML = '';

            // Show size field if required or multiple sizes exist
            if ((data.requires_size && uniqueSizes.length > 0) || uniqueSizes.length > 1) {
                sizeWrapper.style.display = 'block';
                sizeSelect.required = true;
                uniqueSizes.forEach(s => {
                    sizeSelect.innerHTML += `<option value="${s}">${s.toUpperCase()}</option>`;
                });
            } else {
                sizeWrapper.style.display = 'none';
                sizeSelect.required = false;
                if (uniqueSizes.length === 1) {
                    sizeSelect.innerHTML = `<option value="${uniqueSizes[0]}">${uniqueSizes[0].toUpperCase()}</option>`;
                }
            }

            // Show color field if required or multiple colors exist
            if ((data.requires_color && uniqueColors.length > 0) || uniqueColors.length > 1) {
                colorWrapper.style.display = 'block';
                colorSelect.required = true;
                uniqueColors.forEach(c => {
                    colorSelect.innerHTML += `<option value="${c}">${c.charAt(0).toUpperCase() + c.slice(1)}</option>`;
                });
            } else {
                colorWrapper.style.display = 'none';
                colorSelect.required = false;
                if (uniqueColors.length === 1) {
                    colorSelect.innerHTML = `<option value="${uniqueColors[0]}">${uniqueColors[0].charAt(0).toUpperCase() + uniqueColors[0].slice(1)}</option>`;
                }
            }

            const modal = new bootstrap.Modal(document.getElementById('addToCartVestModal'));
            modal.show();
        })
        .catch(() => {
            if (typeof showToast === 'function') {
                showToast('Could not load product options. Redirecting...', 'error');
            }
            
            var card = document.querySelector('.vest-item-card[data-slug] input[value="' + productId + '"]');
            var slug = null;
            if (card) {
                slug = card.closest('.vest-item-card').getAttribute('data-slug');
            }
            if (!slug) {
                var cards = document.querySelectorAll('.vest-item-card');
                cards.forEach(function(c) {
                    if (c.innerHTML.indexOf('value="' + productId + '"') !== -1) {
                        slug = c.getAttribute('data-slug');
                    }
                });
            }
            if (slug) {
                window.location.href = `/products/${slug}/`;
            } else {
                window.location.href = '/products/';
            }
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
    // Add to Cart Form submit
    const addToCartVestForm = document.getElementById('addToCartVestForm');
    if (addToCartVestForm) {
        addToCartVestForm.onsubmit = function(e) {
            e.preventDefault();
            const productId = document.getElementById('vestProductId').value;
            const size = document.getElementById('vestSizeSelect').value;
            const color = document.getElementById('vestColorSelect').value;
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
            .catch(error => {
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
