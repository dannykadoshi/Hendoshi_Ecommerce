/* ================================================
   HENDOSHI - LOGIN PAGE
   ================================================
   
   Purpose: JavaScript functionality for login page
   
   Contains:
   - Event handlers
   - User interactions
   - Dynamic functionality
   
   Dependencies: utils.js (typically)
   Load Order: Load as needed for specific pages
   ================================================ */

document.addEventListener('DOMContentLoaded', function() {
    // Trigger from template conditional - check for .alert or form errors
    const hasErrors = document.querySelector('.alert-danger') || document.querySelector('[data-form-errors="true"]');
    if (hasErrors) {
        if (typeof showToast === 'function') {
            showToast('Invalid username/email or password. Please try again.', 'error');
        }
    }
});
