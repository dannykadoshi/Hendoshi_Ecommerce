/* ================================================
   HENDOSHI - PASSWORD CHANGE PAGE
   ================================================
   
   Purpose: JavaScript functionality for password change page
   
   Contains:
   - Event handlers
   - User interactions
   - Dynamic functionality
   
   Dependencies: utils.js (typically)
   Load Order: Load as needed for specific pages
   ================================================ */

document.addEventListener('DOMContentLoaded', function() {
    const formInputs = document.querySelectorAll('#passwordChangeForm .form-control');
    
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
