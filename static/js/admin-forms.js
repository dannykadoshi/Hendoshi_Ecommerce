/**
 * Admin Forms Utilities
 * Simple form enhancements for admin pages
 */

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
    
});
