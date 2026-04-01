/* ================================================
   HENDOSHI - ADDRESS FORM
   ================================================

   Purpose: Adds the .has-value CSS class to address form inputs
   that already contain a value on page load, enabling CSS-driven
   visual feedback (e.g. floating labels, filled-field styles) for
   pre-populated fields without waiting for a change event.

   Contains:
   - DOMContentLoaded handler that iterates .address-form inputs
   - .has-value class toggling based on input.value truthiness

   Dependencies: None
   Load Order: Load on any page that renders the address form
   ================================================ */

document.addEventListener('DOMContentLoaded', function() {
    // Add has-value class for filled inputs
    const formInputs = document.querySelectorAll('.address-form .profile-form-input');
    
    formInputs.forEach(input => {
        // Add visual feedback on input
        input.addEventListener('input', function() {
            if (this.value.trim() !== '') {
                this.classList.add('has-value');
            } else {
                this.classList.remove('has-value');
            }
        });
        
        // Check if field has initial value
        if (input.value.trim() !== '') {
            input.classList.add('has-value');
        }
    });
});
