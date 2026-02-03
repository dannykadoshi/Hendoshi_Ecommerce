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
    
});
