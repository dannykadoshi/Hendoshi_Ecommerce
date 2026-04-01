/* ================================================
   HENDOSHI - NOTIFICATION PREFERENCES
   ================================================
   
   Purpose: JavaScript functionality for notification preferences
   
   Contains:
   - Event handlers
   - User interactions
   - Dynamic functionality
   
   Dependencies: utils.js (typically)
   Load Order: Load as needed for specific pages
   ================================================ */

document.addEventListener('DOMContentLoaded', function() {
    const masterToggle = document.getElementById('email_notifications_enabled');
    const optionsSection = document.getElementById('notificationOptions');

    function updateOptionsState() {
        if (masterToggle.checked) {
            optionsSection.classList.remove('disabled');
        } else {
            optionsSection.classList.add('disabled');
        }
    }

    masterToggle.addEventListener('change', updateOptionsState);
    updateOptionsState();
});
