/* ================================================
   HENDOSHI - UTILS
   ================================================
   
   Purpose: JavaScript functionality for utils
   
   Contains:
   - Event handlers
   - User interactions
   - Dynamic functionality
   
   Dependencies: utils.js (typically)
   Load Order: Load as needed for specific pages
   ================================================ */

// Auto-dismiss messages after 4 seconds (exclude guide alerts)
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        let alerts = document.querySelectorAll('.alert:not(.guide-alert)');
        alerts.forEach(function(alert) {
            let bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 4000);
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

