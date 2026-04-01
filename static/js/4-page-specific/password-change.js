/* ================================================
   HENDOSHI - PASSWORD CHANGE PAGE
   ================================================

   Purpose: Enhances the password change form with inline error clearing
            and has-value class toggling for floating label styling

   Contains:
   - input and change event handlers on #passwordChangeForm .form-control inputs
   - Hides .form-error-text elements when user begins correcting a field
   - Adds/removes .has-value class to drive floating label CSS transitions
   - Initialises .has-value on fields that already contain a value on page load

   Dependencies: None (vanilla JS)
   Load Order: Load on password change page only
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
