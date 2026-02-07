/**
 * Password Reset Page Scripts
 * Shows error toast if form has errors
 */

document.addEventListener('DOMContentLoaded', function() {
    const hasErrors = document.querySelector('.alert-danger') || document.querySelector('[data-form-errors="true"]');
    if (hasErrors) {
        if (typeof showToast === 'function') {
            showToast('Please enter a valid email address.', 'error');
        }
    }
});
