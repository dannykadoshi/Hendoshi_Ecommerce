/* ================================================
   HENDOSHI - LOGIN PAGE
   ================================================

   Purpose: Detects Django form authentication errors on the login page and
            surfaces them as a toast notification

   Contains:
   - DOMContentLoaded handler that checks for .alert-danger or [data-form-errors="true"]
   - Calls showToast() with an invalid credentials message if errors are found

   Dependencies: base.js (showToast)
   Load Order: Load on login page only
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
