/**
 * Signup Page Scripts
 * Form input error handling and visual feedback
 */

document.addEventListener('DOMContentLoaded', function() {
    // Show error toast if form has errors
    const hasErrors = document.querySelector('.alert-danger') || document.querySelector('.form-error-text');
    if (hasErrors) {
        if (typeof showToast === 'function') {
            showToast('Please fix the errors below to complete your registration.', 'error');
        }
    }

    // Form input handling
    const formInputs = document.querySelectorAll('#signupForm .form-control');
    
    formInputs.forEach(input => {
        // Remove error on input
        input.addEventListener('input', function() {
            const errorElement = this.closest('div').querySelector('.form-error-text');
            if (errorElement) {
                errorElement.style.display = 'none';
            }
            // Add green border when user starts typing
            if (this.value.trim() !== '') {
                this.classList.add('has-value');
            } else {
                this.classList.remove('has-value');
            }
        });
        
        // Also handle change for good measure
        input.addEventListener('change', function() {
            const errorElement = this.closest('div').querySelector('.form-error-text');
            if (errorElement && this.value.trim() !== '') {
                errorElement.style.display = 'none';
            }
            if (this.value.trim() !== '') {
                this.classList.add('has-value');
            } else {
                this.classList.remove('has-value');
            }
        });
        
        // Check if field has initial value (from form re-render after error)
        if (input.value.trim() !== '') {
            input.classList.add('has-value');
        }
    });
});
