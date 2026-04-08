/* ================================================
   HENDOSHI - UTILS
   ================================================

   Purpose: Provides lightweight global utilities used across all pages:
            auto-dismissing Bootstrap alerts and smooth anchor scroll

   Contains:
   - Auto-dismiss: closes all .alert elements (except .guide-alert) after 4 seconds via Bootstrap Alert
   - Smooth scroll: intercepts clicks on anchor links (href^="#") and scrolls smoothly to the target

   Dependencies: Bootstrap 5 (Alert)
   Load Order: Load on all pages via base.html (before page-specific scripts)
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

// Password visibility toggle
document.addEventListener('click', function(e) {
    const btn = e.target.closest('.password-toggle');
    if (!btn) return;
    const wrapper = btn.closest('.password-field-wrapper');
    if (!wrapper) return;
    const input = wrapper.querySelector('input[type="password"], input[type="text"]');
    if (!input) return;
    const isHidden = input.type === 'password';
    input.type = isHidden ? 'text' : 'password';
    const icon = btn.querySelector('i');
    if (icon) {
        icon.classList.toggle('fa-eye', !isHidden);
        icon.classList.toggle('fa-eye-slash', isHidden);
    }
    btn.setAttribute('aria-label', isHidden ? 'Hide password' : 'Show password');
});

// Smooth scroll for anchor links (exclude href="#")
document.querySelectorAll('a[href^="#"]:not([href="#"])').forEach(anchor => {
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

