/* ================================================
   HENDOSHI - PROFILE PAGE
   ================================================

   Purpose: Handles interactive behaviour on the user profile page:
   address deletion confirmation flow and notification preferences
   master toggle. Keeps destructive actions behind a confirmation
   modal so accidental deletions are prevented.

   Contains:
   - showDeleteConfirmation(addressId, addressDisplay) — opens modal
   - closeConfirmationModal()                          — closes modal
   - executeDeleteConfirmation()                       — submits delete
   - Notification preferences master toggle listener

   Dependencies: None
   Load Order: Load on the profile/account page
   ================================================ */

// Address deletion confirmation
let addressToDelete = null;

window.showDeleteConfirmation = function(addressId, addressName) {
    addressToDelete = addressId;
    const message = `Are you sure you want to delete "${addressName}" address?`;
    document.getElementById('confirmationMessage').textContent = message;
    document.getElementById('confirmationModal').classList.remove('d-none');
};

window.closeConfirmationModal = function() {
    document.getElementById('confirmationModal').classList.add('d-none');
    addressToDelete = null;
};

window.executeDeleteConfirmation = function() {
    if (addressToDelete) {
        const form = document.getElementById('deleteAddressForm');
        form.action = `/profile/address/delete/${addressToDelete}/`;
        form.submit();
    }
    closeConfirmationModal();
};

// Notification preferences toggle
document.addEventListener('DOMContentLoaded', function() {
    const masterToggle = document.getElementById('email_notifications_enabled');
    const optionsSection = document.getElementById('notificationOptions');

    if (masterToggle && optionsSection) {
        const updateOptionsState = function() {
            if (masterToggle.checked) {
                optionsSection.style.opacity = '1';
                optionsSection.style.pointerEvents = 'auto';
            } else {
                optionsSection.style.opacity = '0.5';
                optionsSection.style.pointerEvents = 'none';
            }
        };

        masterToggle.addEventListener('change', updateOptionsState);
        updateOptionsState();
    }
});
