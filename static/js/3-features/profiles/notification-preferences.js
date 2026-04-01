/* ================================================
   HENDOSHI - NOTIFICATION PREFERENCES
   ================================================

   Purpose: Controls the master email notification toggle on the
   notification preferences page. Enables or disables the full
   #notificationOptions section based on the master checkbox state,
   preventing sub-options from being submitted when email is off.

   Contains:
   - Master toggle change listener on email_notifications_enabled
   - Enable/disable logic for #notificationOptions fieldset

   Dependencies: None
   Load Order: Load on the notification preferences page
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
