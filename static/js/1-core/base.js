/* ================================================
   HENDOSHI BASE JS - Entry Point
   ================================================
   
   This file serves as the main entry point.
   All functionality has been extracted to modular files:
   
   - theme-toggle.js (theme switching)
   - navigation-dropdown.js (dropdown hover behaviors)
   - hero-carousel.js (homepage hero carousel)
   - newsletter-validation.js (newsletter form validation)
   - carousels.js (products & collections carousels)
   - utils.js (smooth scroll, auto-dismiss messages)
   - newsletter-popup.js (popup modal)
   - vault.js (vault gallery functionality)
   - stripe-payment.js (payment processing)
   
   Load these files in base.html as needed.
   ================================================ */

// Reserved for global initialization if needed
// console.log('HENDOSHI Base JS loaded');

// Conditional logo navigation
// If user is on home page, clicking logo goes to products
// If user is on any other page, clicking logo goes to home
document.addEventListener('DOMContentLoaded', function() {
    const logoLink = document.querySelector('.navbar-brand');
    if (logoLink) {
        logoLink.addEventListener('click', function(e) {
            const currentPath = window.location.pathname;
            
            // Check if we're on the home page
            if (currentPath === '/' || currentPath === '/home/') {
                e.preventDefault();
                window.location.href = '/products/';
            }
            // For all other pages, default behavior (go to home) works fine
        });
    }
});
