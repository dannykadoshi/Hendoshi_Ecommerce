/* ================================================
   HENDOSHI - PASSWORD RESET PAGE
   ================================================
   
   Purpose: JavaScript functionality for password reset page
   
   Contains:
   - Event handlers
   - User interactions
   - Dynamic functionality
   
   Dependencies: utils.js (typically)
   Load Order: Load as needed for specific pages
   ================================================ */

document.addEventListener('DOMContentLoaded', function() {
    const hasErrors = document.querySelector('.alert-danger') || document.querySelector('[data-form-errors="true"]');
    if (hasErrors) {
        if (typeof showToast === 'function') {
            showToast('Please enter a valid email address.', 'error');
        }
    }
});
