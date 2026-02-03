/**
 * Login Page Scripts
 * Shows error toast if form has errors
 */

document.addEventListener('DOMContentLoaded', function() {
    // Trigger from template conditional - check for .alert or form errors
    const hasErrors = document.querySelector('.alert-danger') || document.querySelector('[data-form-errors="true"]');
    if (hasErrors) {
        if (typeof showToast === 'function') {
            showToast('Invalid username/email or password. Please try again.', 'error');
        }
    }
});
