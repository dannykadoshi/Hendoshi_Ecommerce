/**
 * Notification Preferences Scripts
 * Handles master toggle for email notifications
 */

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
