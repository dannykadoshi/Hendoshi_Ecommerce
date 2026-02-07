/**
 * Address Form Scripts
 * Handles visual feedback for filled inputs
 */

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
