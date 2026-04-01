/* ================================================
   HENDOSHI - COOKIE CONSENT
   ================================================

   Purpose: Manages the GDPR cookie consent banner and customisation modal,
            persisting consent choices to the server and conditionally loading analytics

   Contains:
   - Banner buttons: Accept All, Reject All, Customize, and Close
   - Settings modal: granular toggle for analytics, marketing, and preference cookies
   - setCookieConsent() — AJAX POST to /cookies/update-consent/ and sets a local cookie
   - loadCurrentSettings() — reads existing cookie_consent cookie to pre-populate modal toggles
   - loadAnalytics() — conditionally loads analytics scripts when consent is granted

   Dependencies: base.js (getCookie, getCsrfToken helpers expected globally)
   Load Order: Load on all pages via base.html
   ================================================ */

document.addEventListener('DOMContentLoaded', function() {
    const banner = document.getElementById('cookie-consent-banner');
    const modal = document.getElementById('cookie-settings-modal');

    // Check if user has already made a choice
    const consentCookie = getCookie('cookie_consent');
    if (!consentCookie) {
        banner.classList.remove('d-none');
    }

    // Banner buttons
    document.getElementById('accept-all-cookies').addEventListener('click', function() {
        setCookieConsent({
            essential: true,
            analytics: true,
            marketing: true,
            preferences: true
        });
        banner.classList.add("d-none");
    });

    document.getElementById('customize-cookies').addEventListener('click', function() {
        banner.classList.add("d-none");
        modal.classList.remove("d-none");
        loadCurrentSettings();
    });

    document.getElementById('reject-all-cookies').addEventListener('click', function() {
        setCookieConsent({
            essential: true,
            analytics: false,
            marketing: false,
            preferences: false
        });
        banner.classList.add("d-none");
    });

    document.getElementById('close-cookie-banner').addEventListener('click', function() {
        banner.classList.add("d-none");
    });

    // Modal buttons
    document.getElementById('close-cookie-modal').addEventListener('click', function() {
        modal.classList.add("d-none");
        banner.classList.remove("d-none");
    });

    document.getElementById('save-cookie-settings').addEventListener('click', function() {
        const settings = {
            essential: true,
            analytics: document.getElementById('analytics-cookies').checked,
            marketing: document.getElementById('marketing-cookies').checked,
            preferences: document.getElementById('preference-cookies').checked
        };
        setCookieConsent(settings);
        modal.classList.add("d-none");
    });

    document.getElementById('accept-all-modal').addEventListener('click', function() {
        setCookieConsent({
            essential: true,
            analytics: true,
            marketing: true,
            preferences: true
        });
        modal.classList.add("d-none");
    });

    function setCookieConsent(settings) {
        fetch('/cookies/update-consent/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify(settings)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Cookie consent updated successfully');
                document.cookie = `cookie_consent=${JSON.stringify(settings)}; path=/; max-age=31536000; SameSite=Lax`;
                
                if (settings.analytics) {
                    loadAnalytics();
                }
                if (settings.marketing) {
                    loadMarketing();
                }
            } else {
                console.error('Failed to update cookie consent');
            }
        })
        .catch(error => console.error('Error updating cookie consent:', error));
    }

    function loadCurrentSettings() {
        const consentCookie = getCookie('cookie_consent');
        if (consentCookie) {
            try {
                const settings = JSON.parse(consentCookie);
                document.getElementById('analytics-cookies').checked = settings.analytics || false;
                document.getElementById('marketing-cookies').checked = settings.marketing || false;
                document.getElementById('preference-cookies').checked = settings.preferences || false;
            } catch (e) {
                console.error('Error parsing cookie settings:', e);
            }
        }
    }

    function loadAnalytics() {
        console.log('Loading analytics scripts...');
    }

    function loadMarketing() {
        console.log('Loading marketing scripts...');
    }

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) {
            return decodeURIComponent(parts.pop().split(';').shift());
        }
        return null;
    }

    function getCsrfToken() {
        const metaToken = document.querySelector('meta[name="csrf-token"]');
        if (metaToken) return metaToken.content;
        
        const inputToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (inputToken) return inputToken.value;
        
        return getCookie('csrftoken');
    }
});
