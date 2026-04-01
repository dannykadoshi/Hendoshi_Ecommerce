/* ================================================
   HENDOSHI - COOKIE SETTINGS
   ================================================

   Purpose: Manages the cookie consent settings page. Handles the
   Save, Accept All, and Reject All buttons by POSTing the user's
   toggle preferences to /cookies/update-consent/ via the Fetch API,
   then shows a success/error message and redirects on success.

   Contains:
   - Save settings handler (reads individual toggle states)
   - Accept All handler (enables all consent categories)
   - Reject All handler (disables all non-essential categories)
   - updateToggles(settings) — syncs toggle UI to a consent object
   - showMessage(text, type) — displays inline feedback message

   Dependencies: Fetch API (no external libraries)
   Load Order: Load only on the cookie settings page
   ================================================ */

document.addEventListener('DOMContentLoaded', function() {
    const saveBtn = document.getElementById('save-preferences');
    const acceptAllBtn = document.getElementById('accept-all');
    const rejectAllBtn = document.getElementById('reject-all');

    saveBtn.addEventListener('click', function() {
        const settings = {
            essential: true,
            analytics: document.getElementById('analytics-toggle').checked,
            marketing: document.getElementById('marketing-toggle').checked,
            preferences: document.getElementById('preferences-toggle').checked
        };
        updateCookieConsent(settings);
    });

    acceptAllBtn.addEventListener('click', function() {
        const settings = {
            essential: true,
            analytics: true,
            marketing: true,
            preferences: true
        };
        updateCookieConsent(settings);
        updateToggles(settings);
    });

    rejectAllBtn.addEventListener('click', function() {
        const settings = {
            essential: true,
            analytics: false,
            marketing: false,
            preferences: false
        };
        updateCookieConsent(settings);
        updateToggles(settings);
    });

    function updateCookieConsent(settings) {
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
                showMessage('Cookie preferences saved successfully!', 'success');
            } else {
                showMessage('Error saving preferences. Please try again.', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage('Error saving preferences. Please try again.', 'error');
        });
    }

    function updateToggles(settings) {
        document.getElementById('analytics-toggle').checked = settings.analytics;
        document.getElementById('marketing-toggle').checked = settings.marketing;
        document.getElementById('preferences-toggle').checked = settings.preferences;
    }

    function showMessage(message, type) {
        const existing = document.querySelector('.cookie-message');
        if (existing) existing.remove();

        const msg = document.createElement('div');
        msg.className = `cookie-message ${type}`;
        msg.textContent = message;
        msg.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 10001;
            animation: slideInRight 0.3s ease-out;
        `;

        if (type === 'success') {
            msg.style.background = 'var(--neon-pink)';
        } else {
            msg.style.background = '#dc3545';
        }

        document.body.appendChild(msg);

        setTimeout(() => {
            if (msg.parentNode) {
                msg.style.animation = 'slideOutRight 0.3s ease-in';
                setTimeout(() => msg.remove(), 300);
            }
        }, 3000);
    }

    function getCsrfToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
});

const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);
