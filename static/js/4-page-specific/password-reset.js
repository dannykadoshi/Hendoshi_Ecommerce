/* ================================================
   HENDOSHI - PASSWORD RESET PAGE
   ================================================

   Purpose: Detects Django form errors on the password reset page and
            surfaces them as a toast notification

   Contains:
   - DOMContentLoaded handler that checks for .alert-danger or [data-form-errors="true"]
   - Calls showToast() with a "valid email required" message if errors are found

   Dependencies: base.js (showToast)
   Load Order: Load on password reset page only
   ================================================ */

document.addEventListener('DOMContentLoaded', function() {
    const hasErrors = document.querySelector('.alert-danger') || document.querySelector('[data-form-errors="true"]');
    if (hasErrors) {
        if (typeof showToast === 'function') {
            showToast('Please enter a valid email address.', 'error');
        }
    }
});
