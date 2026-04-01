/* ================================================
   HENDOSHI - NEWSLETTER POPUP
   ================================================

   Purpose: Displays a timed newsletter subscription popup for unauthenticated
            visitors, suppressed via a 7-day cookie after dismissal

   Contains:
   - Cookie-based display suppression (hendoshi_newsletter_popup_dismissed, 7-day expiry)
   - Skips popup for authenticated users and newsletter confirmation/unsubscribe pages
   - Popup HTML injected dynamically into the DOM after a 3-second delay
   - AJAX subscription form with email validation and GDPR consent checkbox
   - Close handlers for backdrop click, close button, and post-success auto-dismiss

   Dependencies: None (vanilla JS, fetch API)
   Load Order: Load on all pages via base.html
   ================================================ */

(function() {
    'use strict';

    // Configuration
    const CONFIG = {
        cookieName: 'hendoshi_newsletter_popup_dismissed',
        cookieDays: 7, // Don't show again for 7 days after dismissal
        delayMs: 3000, // Show popup 3 seconds after page load
        showOnce: true // Only show once per session if dismissed
    };

    // Cookie helper functions
    function setCookie(name, value, days) {
        const date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        const expires = "expires=" + date.toUTCString();
        document.cookie = name + "=" + value + ";" + expires + ";path=/;SameSite=Lax";
    }

    function getCookie(name) {
        const nameEQ = name + "=";
        const ca = document.cookie.split(';');
        for(let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) === ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
        }
        return null;
    }

    // Email validation
    function isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(String(email).toLowerCase());
    }

    // Initialize popup
    function initNewsletterPopup() {
        // Check if user is authenticated (signed in)
        const isAuthenticated = document.body.dataset.authenticated === 'true' || 
                               document.querySelector('.user-authenticated') !== null ||
                               document.querySelector('[data-user-authenticated="true"]') !== null;
        
        if (isAuthenticated) {
            // Don't show popup for authenticated users
            return;
        }

        // Check if user has already dismissed the popup
        if (getCookie(CONFIG.cookieName)) {
            return;
        }

        // Check if user is already on newsletter confirmation page
        if (window.location.pathname.includes('/newsletter/confirm') || 
            window.location.pathname.includes('/newsletter/unsubscribe')) {
            return;
        }

        // Create popup HTML
        const popupHTML = `
            <div class="newsletter-popup-backdrop" id="newsletterPopupBackdrop">
                <div class="newsletter-popup">
                    <button class="newsletter-popup-close" id="newsletterPopupClose" aria-label="Close popup">
                        <i class="fas fa-times"></i>
                    </button>
                    
                    <div class="newsletter-popup-content">
                        <div class="newsletter-popup-logo">HENDOSHI</div>
                        
                        <h2 class="newsletter-popup-title">
                            Want 10% Off Your First Order?
                        </h2>
                        
                        <p class="newsletter-popup-subtitle">
                            + Exclusive Offers & Early Access
                        </p>
                        
                        <div class="newsletter-popup-error" id="popupError"></div>
                        <div class="newsletter-popup-success" id="popupSuccess"></div>
                        
                        <form class="newsletter-popup-form" id="newsletterPopupForm">
                            <input 
                                type="email" 
                                class="newsletter-popup-input" 
                                id="popupEmail" 
                                placeholder="Enter your email..."
                                required
                                autocomplete="email"
                            >
                            
                            <div class="newsletter-popup-consent">
                                <input 
                                    type="checkbox" 
                                    id="popupConsent" 
                                    required
                                >
                                <label for="popupConsent">
                                    I agree to receive marketing emails and accept the 
                                    <a href="/privacy/" target="_blank">Privacy Policy</a>
                                </label>
                            </div>
                            
                            <div class="newsletter-popup-buttons">
                                <button type="submit" class="newsletter-popup-btn newsletter-popup-btn-primary">
                                    Sign Me Up
                                </button>
                                <button type="button" class="newsletter-popup-btn newsletter-popup-btn-secondary" id="newsletterPopupDismiss">
                                    No, Thanks
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        `;

        // Inject popup into body
        document.body.insertAdjacentHTML('beforeend', popupHTML);

        // Get elements
        const backdrop = document.getElementById('newsletterPopupBackdrop');
        const closeBtn = document.getElementById('newsletterPopupClose');
        const dismissBtn = document.getElementById('newsletterPopupDismiss');
        const form = document.getElementById('newsletterPopupForm');
        const emailInput = document.getElementById('popupEmail');
        const consentCheckbox = document.getElementById('popupConsent');
        const errorDiv = document.getElementById('popupError');
        const successDiv = document.getElementById('popupSuccess');

        // Show popup after delay
        setTimeout(() => {
            backdrop.classList.add('show');
            // Focus email input for better UX
            setTimeout(() => emailInput.focus(), 400);
        }, CONFIG.delayMs);

        // Close handlers
        function closePopup() {
            backdrop.classList.remove('show');
            setTimeout(() => backdrop.remove(), 300);
            setCookie(CONFIG.cookieName, 'true', CONFIG.cookieDays);
        }

        closeBtn.addEventListener('click', closePopup);
        dismissBtn.addEventListener('click', closePopup);

        // Close on backdrop click (outside popup)
        backdrop.addEventListener('click', (e) => {
            if (e.target === backdrop) {
                closePopup();
            }
        });

        // Close on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && backdrop.classList.contains('show')) {
                closePopup();
            }
        });

        // Show error message
        function showError(message) {
            errorDiv.textContent = message;
            errorDiv.classList.add('show');
            successDiv.classList.remove('show');
            emailInput.classList.add('invalid');
        }

        // Show success message
        function showSuccess(message) {
            successDiv.textContent = message;
            successDiv.classList.add('show');
            errorDiv.classList.remove('show');
            emailInput.classList.remove('invalid');
        }

        // Form submission
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Clear previous messages
            errorDiv.classList.remove('show');
            successDiv.classList.remove('show');
            emailInput.classList.remove('invalid');

            const email = emailInput.value.trim();
            const consent = consentCheckbox.checked;

            // Validation
            if (!email) {
                showError('Please enter your email address');
                return;
            }

            if (!isValidEmail(email)) {
                showError('Please enter a valid email address');
                return;
            }

            if (!consent) {
                showError('Please agree to the Privacy Policy to subscribe');
                return;
            }

            // Get CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';

            // Disable submit button
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.textContent = 'Subscribing...';

            try {
                const response = await fetch('/notifications/newsletter/subscribe/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: `email=${encodeURIComponent(email)}&consent=${consent ? '1' : '0'}`
                });

                const data = await response.json();

                if (response.ok) {
                    showSuccess(data.message || 'Success! Check your email to confirm your subscription.');
                    emailInput.value = '';
                    consentCheckbox.checked = false;
                    
                    // Close popup after 3 seconds
                    setTimeout(closePopup, 3000);
                } else if (response.status === 409) {
                    showError(data.message || 'This email is already subscribed');
                } else if (response.status === 429) {
                    showError(data.message || 'Too many attempts. Please try again later.');
                } else {
                    showError(data.message || 'An error occurred. Please try again.');
                }
            } catch (error) {
                showError('Network error. Please check your connection and try again.');
                console.error('Newsletter subscription error:', error);
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initNewsletterPopup);
    } else {
        initNewsletterPopup();
    }
})();
