/* ================================================
   HENDOSHI - NEWSLETTER VALIDATION
   ================================================
   
   Purpose: JavaScript functionality for newsletter validation
   
   Contains:
   - Event handlers
   - User interactions
   - Dynamic functionality
   
   Dependencies: utils.js (typically)
   Load Order: Load as needed for specific pages
   ================================================ */

// Newsletter Form Validation
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('newsletterForm');
    if (!form) return;
    
    const emailInput = document.getElementById('newsletter-email');
    const errorDiv = form.querySelector('.newsletter-error');
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Clear previous error
        errorDiv.classList.remove('show');
        emailInput.classList.remove('invalid');
        
        // Validate email
        const email = emailInput.value.trim();
        
        if (!email) {
            showError('Please enter your email address');
            return;
        }
        
        if (!isValidEmail(email)) {
            showError('Please enter a valid email address (e.g., you@example.com)');
            return;
        }
        
        // Consent checkbox (GDPR)
        const consentCheckbox = document.getElementById('newsletter-consent');
        const consent = consentCheckbox ? consentCheckbox.checked : false;
        if (!consent) {
            showError('Please agree to the Privacy Policy to subscribe.');
            return;
        }

        // If validation passes, submit via AJAX to backend
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : '';

        fetch('/notifications/newsletter/subscribe/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `email=${encodeURIComponent(email)}&consent=${consent ? '1' : '0'}`
        })
        .then(response => response.json().then(data => ({status: response.status, body: data})))
        .then(({status, body}) => {
            if (status === 200) {
                // Server tells user to check email for confirmation
                showSuccessMessage(body.message || 'Confirmation email sent. Please check your inbox.');
                emailInput.value = '';
                if (consentCheckbox) consentCheckbox.checked = false;
            } else if (status === 409) {
                showError(body.message || 'Email already subscribed.');
            } else {
                showError(body.message || 'Subscription failed. Please try again later.');
            }
        })
        .catch(() => {
            showError('Network error. Please try again later.');
        });
    });
    
    function showError(message) {
        errorDiv.textContent = message;
        errorDiv.classList.add('show');
        emailInput.classList.add('invalid');
        
        // Auto-hide error after 4 seconds
        setTimeout(function() {
            errorDiv.classList.remove('show');
            emailInput.classList.remove('invalid');
        }, 4000);
    }
    
    function showSuccessMessage(message) {
        errorDiv.textContent = '✓ ' + (message || 'Thanks for subscribing!');
        errorDiv.style.borderLeftColor = '#00ff00';
        errorDiv.style.color = '#00ff00';
        errorDiv.classList.add('show');

        setTimeout(function() {
            errorDiv.classList.remove('show');
            errorDiv.style.borderLeftColor = '';
            errorDiv.style.color = '';
        }, 4500);
    }
    
    function isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
});

