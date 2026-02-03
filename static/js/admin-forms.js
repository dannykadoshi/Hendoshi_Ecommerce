/**
 * Admin Forms Utilities
 * Simple form enhancements for admin pages
 */

// ========================================
// VAULT CONFIRMATION MODAL (GLOBAL SCOPE for onclick)
// ========================================
let currentFormToSubmit = null;

window.showVaultConfirmModal = function(title, message, iconClass, confirmText, confirmClass, form) {
    // Update modal content
    document.getElementById('modal-title-text').textContent = title;
    document.getElementById('modal-message').textContent = message;
    document.getElementById('modal-main-icon').className = `fas ${iconClass} vault-modal-main-icon`;
    document.getElementById('modal-confirm-text').textContent = confirmText;

    // Update confirm button styling
    const confirmBtn = document.getElementById('modal-confirm-btn');
    confirmBtn.className = `btn ${confirmClass} vault-modal-btn-confirm`;
    
    // Store form reference
    currentFormToSubmit = form;
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('vaultConfirmModal'));
    modal.show();
};

// Discount code confirmation function (GLOBAL for onclick)
window.confirmDiscountCodeDelete = function(codeId, codeName) {
    const form = document.querySelector(`form[action*="delete"][action*="/${codeId}/"]`);
    window.showVaultConfirmModal(
        'Delete Discount Code',
        `Are you sure you want to permanently delete the discount code "${codeName}"? This action cannot be undone!`,
        'fa-trash',
        'Delete Forever',
        'btn-danger',
        form
    );
    return false;
};

// Shipping rate confirmation function (GLOBAL for onclick)
window.confirmShippingRateDelete = function(rateId, rateName) {
    const form = document.querySelector(`form[action*="/shipping/${rateId}/delete/"]`);
    if (!form) return;
    window.showVaultConfirmModal(
        'Delete Shipping Rate',
        `Are you sure you want to permanently delete the shipping rate "${rateName}"? This action cannot be undone!`,
        'fa-trash',
        'Delete Forever',
        'btn-danger',
        form
    );
    return false;
};

// Theme confirmation function (GLOBAL for onclick)
window.confirmThemeDelete = function(themeId, themeName) {
    const form = document.querySelector(`form[action*="delete"][action*="/${themeId}/"]`);
    window.showVaultConfirmModal(
        'Delete Seasonal Theme',
        `Are you sure you want to permanently delete the theme "${themeName}"? This action cannot be undone!`,
        'fa-trash',
        'Delete Forever',
        'btn-danger',
        form
    );
    return false;
};

document.addEventListener('DOMContentLoaded', function() {
    
    // ========================================
    // DISCOUNT CODE FORM
    // ========================================
    
    // Auto-uppercase discount code input
    const discountCodeInput = document.getElementById('id_code');
    if (discountCodeInput) {
        discountCodeInput.addEventListener('input', function(e) {
            e.target.value = e.target.value.toUpperCase();
        });
    }
    
    // Update discount value help text based on type selection
    const discountTypeSelect = document.getElementById('id_discount_type');
    if (discountTypeSelect) {
        discountTypeSelect.addEventListener('change', function(e) {
            const helpText = e.target.closest('.col-12').querySelector('.form-text');
            if (helpText) {
                if (e.target.value === 'percentage') {
                    helpText.textContent = 'Percentage (0-100)';
                } else {
                    helpText.textContent = 'Fixed amount in €';
                }
            }
        });
    }
    
    // ========================================
    // THEME FORM
    // ========================================
    
    // Theme type descriptions
    const themeDescriptions = {
        'new_years': { emoji: '🎆✨', desc: 'Gold/silver confetti, champagne bubbles, and firework sparkles' },
        'valentines': { emoji: '❤️💕', desc: 'Floating hearts and rose petals with soft pink glow' },
        'st_patricks': { emoji: '☘️🍀', desc: 'Shamrocks, gold coins, and rainbow accents' },
        'mothers_day': { emoji: '🌸🦋', desc: 'Delicate flower petals and butterflies' },
        'fathers_day': { emoji: '🔧👔', desc: 'Subtle geometric shapes with navy/gray tones' },
        'fourth_july': { emoji: '🎆⭐', desc: 'Fireworks and stars in red, white, and blue' },
        'rock_n_roll': { emoji: '🎸⚡', desc: 'Guitar picks, lightning bolts, and musical notes' },
        'thanksgiving': { emoji: '🍂🍁', desc: 'Autumn leaves and warm harvest colors' },
        'christmas': { emoji: '❄️🎄', desc: 'Snowflakes, ornaments, and twinkling lights' },
        'everyday': { emoji: '💀🦇', desc: 'Skulls, flames, bats, and dark gothic vibes' },
        'celebration': { emoji: '🎉🎊', desc: 'Colorful confetti, sparkles, and party vibes' }
    };

    const themeTypeSelect = document.getElementById('id_theme_type');
    const previewDiv = document.getElementById('themeTypePreview');
    const emojiSpan = document.getElementById('themeEmoji');
    const descSpan = document.getElementById('themeDescription');

    function updateThemePreview() {
        const selectedType = themeTypeSelect.value;
        if (selectedType && themeDescriptions[selectedType]) {
            const info = themeDescriptions[selectedType];
            emojiSpan.textContent = info.emoji;
            descSpan.textContent = info.desc;
            previewDiv.style.display = 'flex';
        } else {
            previewDiv.style.display = 'none';
        }
    }

    if (themeTypeSelect) {
        themeTypeSelect.addEventListener('change', updateThemePreview);
        updateThemePreview();
    }

    // Message Strip toggle functionality
    const showStripCheckbox = document.getElementById('id_show_message_strip');
    const stripSettingsContainer = document.getElementById('stripSettingsContainer');
    const stripColorContainer = document.getElementById('stripColorContainer');
    const stripCustomGradientContainer = document.getElementById('stripCustomGradientContainer');
    const stripSpeedContainer = document.getElementById('stripSpeedContainer');
    const stripColorScheme = document.getElementById('id_strip_color_scheme');

    function toggleStripSettings() {
        const isChecked = showStripCheckbox.checked;
        stripSettingsContainer.style.display = isChecked ? 'block' : 'none';
        stripColorContainer.style.display = isChecked ? 'block' : 'none';
        stripSpeedContainer.style.display = isChecked ? 'block' : 'none';
        if (isChecked) {
            toggleCustomGradient();
        } else {
            stripCustomGradientContainer.style.display = 'none';
        }
    }

    function toggleCustomGradient() {
        const isCustom = stripColorScheme.value === 'custom';
        stripCustomGradientContainer.style.display = isCustom ? 'block' : 'none';
    }

    if (showStripCheckbox) {
        showStripCheckbox.addEventListener('change', toggleStripSettings);
        stripColorScheme.addEventListener('change', toggleCustomGradient);
        toggleStripSettings();
    }
    
    // ========================================
    // VAULT CONFIRMATION MODAL HANDLER
    // ========================================
    
    const modalConfirmBtn = document.getElementById('modal-confirm-btn');
    if (modalConfirmBtn) {
        modalConfirmBtn.addEventListener('click', function() {
            if (currentFormToSubmit) {
                currentFormToSubmit.submit();
            }
        });
    }
    
    // ========================================
    // REVIEWS ADMIN - Status Selection
    // ========================================
    
    document.querySelectorAll('.status-select').forEach(select => {
        select.addEventListener('change', function() {
            const reviewId = this.dataset.reviewId;
            const status = this.value;
            updateReviewStatus(reviewId, status);
        });
    });
    
    // ========================================
    // PRODUCTS ADMIN - Select All Checkboxes
    // ========================================
    
    const selectAllEl = document.getElementById('select-all');
    if (selectAllEl) {
        selectAllEl.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('.product-checkbox, .review-checkbox');
            checkboxes.forEach(cb => cb.checked = this.checked);
        });
    }
    
});

// ========================================
// REVIEWS ADMIN FUNCTIONS (GLOBAL for onclick)
// ========================================

window.toggleAllCheckboxes = function() {
    const selectAll = document.getElementById('select-all');
    const checkboxes = document.querySelectorAll('.review-checkbox');
    checkboxes.forEach(cb => cb.checked = selectAll.checked);
};

window.bulkUpdateStatus = function(status) {
    const selectedReviews = document.querySelectorAll('.review-checkbox:checked');
    if (selectedReviews.length === 0) {
        alert('Please select reviews to update.');
        return;
    }

    if (!confirm(`Update ${selectedReviews.length} review(s) to ${status}?`)) {
        return;
    }

    selectedReviews.forEach(cb => {
        updateReviewStatus(cb.value, status);
    });
};

function updateReviewStatus(reviewId, status) {
    fetch(`/products/admin/reviews/${reviewId}/status/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: `status=${status}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const select = document.querySelector(`[data-review-id="${reviewId}"]`);
            if (select) {
                select.value = status;
            }
            if (typeof showToast === 'function') {
                showToast(`Review ${status}`, 'success');
            }
        } else {
            if (typeof showToast === 'function') {
                showToast('Failed to update review status', 'error');
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        if (typeof showToast === 'function') {
            showToast('Failed to update review status', 'error');
        }
    });
}

window.viewReviewDetail = function(reviewId) {
    window.open(`/products/admin/reviews/${reviewId}/`, '_blank');
};

// ========================================
// PRODUCTS ADMIN FUNCTIONS (GLOBAL for onclick)
// ========================================

window.submitBulkAction = function(action) {
    const checkedBoxes = document.querySelectorAll('.product-checkbox:checked');
    if (checkedBoxes.length === 0) {
        alert('Please select at least one product.');
        return;
    }

    if (action === 'delete') {
        showBulkDeleteModal(checkedBoxes);
        return;
    }

    document.getElementById('bulk-action').value = action;
    document.getElementById('bulk-action-form').submit();
};

function showBulkDeleteModal(checkedBoxes) {
    const productList = document.getElementById('bulk-delete-product-list');
    const countElement = document.getElementById('bulk-delete-count');
    
    productList.innerHTML = '';
    countElement.textContent = checkedBoxes.length;
    
    const bulkDeleteForm = document.getElementById('bulk-delete-form');
    if (bulkDeleteForm) {
        const previousInputs = bulkDeleteForm.querySelectorAll('input[name="product_ids"]');
        previousInputs.forEach(i => i.remove());
    }

    checkedBoxes.forEach(checkbox => {
        const row = checkbox.closest('tr') || checkbox.closest('.card');
        let productName = '';
        let productCollection = '';
        let productType = '';
        let productPrice = '';
        let productStatus = '';
        
        if (row) {
            const cells = row.querySelectorAll('td');
            if (cells.length >= 5) {
                productName = cells[1].textContent.trim();
                productCollection = cells[2].textContent.trim();
                productType = cells[3].textContent.trim();
                productPrice = cells[4].textContent.trim();
                productStatus = cells[5].textContent.trim();
            } else {
                const nameElement = row.querySelector('h6');
                productName = nameElement ? nameElement.textContent.trim() : 'Unknown Product';
                
                const details = row.querySelectorAll('div small + div');
                if (details.length >= 4) {
                    productCollection = details[0].textContent.trim();
                    productType = details[1].textContent.trim();
                    productPrice = details[2].textContent.trim();
                    productStatus = details[3].textContent.trim();
                }
            }
        }
        
        const productItem = document.createElement('div');
        productItem.className = 'bulk-delete-product-item';
        productItem.innerHTML = `
            <div class="bulk-delete-product-info">
                <strong>${productName}</strong>
                <small class="text-muted">${productCollection} • ${productType} • ${productPrice} • ${productStatus}</small>
            </div>
        `;
        productList.appendChild(productItem);
        
        if (bulkDeleteForm) {
            const hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.name = 'product_ids';
            hiddenInput.value = checkbox.value;
            bulkDeleteForm.appendChild(hiddenInput);
        }
    });
    
    const modal = new bootstrap.Modal(document.getElementById('bulkDeleteModal'));
    modal.show();
}

window.confirmDeleteProduct = function(productId, productName, productCollection, productType, productPrice, productStatus, productVariants, productCreated, productImageUrl, deleteUrl) {
    document.getElementById('product-name').textContent = productName;
    document.getElementById('modal-product-name').textContent = productName;
    document.getElementById('modal-product-collection').textContent = productCollection;
    document.getElementById('modal-product-type').textContent = productType;
    document.getElementById('modal-product-price').textContent = '$' + productPrice;
    document.getElementById('modal-product-status').textContent = productStatus;
    document.getElementById('modal-product-variants').textContent = productVariants;
    document.getElementById('modal-product-created').textContent = productCreated;

    const imageContainer = document.getElementById('modal-product-image-container');
    const imageElement = document.getElementById('modal-product-image');
    if (productImageUrl) {
        imageElement.src = productImageUrl;
        imageContainer.style.display = 'block';
    } else {
        imageContainer.style.display = 'none';
    }

    const form = document.getElementById('delete-product-form');
    form.action = deleteUrl;

    const modal = new bootstrap.Modal(document.getElementById('deleteProductModal'));
    modal.show();
};

window.confirmDeleteCollection = function(collectionId, collectionName, deleteUrl) {
    document.getElementById('collection-name').textContent = collectionName;
    const form = document.getElementById('delete-collection-form');
    form.action = deleteUrl;
    const modal = new bootstrap.Modal(document.getElementById('deleteCollectionModal'));
    modal.show();
};

window.confirmDeleteProductType = function(productTypeId, productTypeName, deleteUrl) {
    document.getElementById('product-type-name').textContent = productTypeName;
    const form = document.getElementById('delete-product-type-form');
    form.action = deleteUrl;
    const modal = new bootstrap.Modal(document.getElementById('deleteProductTypeModal'));
    modal.show();
};
