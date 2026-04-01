/* ================================================
   HENDOSHI - CONTACT FORM
   ================================================
   
   Purpose: JavaScript functionality for contact form
   
   Contains:
   - Event handlers
   - User interactions
   - Dynamic functionality
   
   Dependencies: utils.js (typically)
   Load Order: Load as needed for specific pages
   ================================================ */

document.addEventListener('DOMContentLoaded', function() {
    const messageField = document.querySelector('textarea[name="message"]');
    const charCount = document.getElementById('charCount');
    const maxChars = 1000;

    if (messageField && charCount) {
        // Update character count on input
        messageField.addEventListener('input', function() {
            const count = this.value.length;
            charCount.textContent = count;

            // Update styling based on count
            const counter = charCount.parentElement;
            counter.classList.remove('warning', 'danger');

            if (count >= maxChars) {
                counter.classList.add('danger');
            } else if (count >= maxChars * 0.8) {
                counter.classList.add('warning');
            }
        });

        // Initialize count on page load
        charCount.textContent = messageField.value.length;
    }

    // Form validation
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            const name = document.querySelector('input[name="name"]');
            const email = document.querySelector('input[name="email"]');
            const subject = document.querySelector('select[name="subject"]');
            const message = document.querySelector('textarea[name="message"]');

            let isValid = true;

            // Validate name
            if (!name.value.trim()) {
                showValidationError('Please enter your name.');
                isValid = false;
            }
            // Validate email
            else if (!email.value.trim() || !isValidEmail(email.value)) {
                showValidationError('Please enter a valid email address.');
                isValid = false;
            }
            // Validate subject
            else if (!subject.value) {
                showValidationError('Please select a subject.');
                isValid = false;
            }
            // Validate message
            else if (!message.value.trim()) {
                showValidationError('Please enter your message.');
                isValid = false;
            }
            // Validate message length
            else if (message.value.length > maxChars) {
                showValidationError('Message must be 1000 characters or less.');
                isValid = false;
            }

            if (!isValid) {
                e.preventDefault();
            }
        });
    }

    function isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    function showValidationError(message) {
        if (typeof showToast === 'function') {
            showToast(message, 'warning');
        } else if (typeof window.alert !== 'undefined') {
            window.alert(message);
        }
    }
});
