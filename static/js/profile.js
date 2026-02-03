/**
 * Profile Page Scripts
 * Handles address management and notification preferences
 */

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
        function updateOptionsState() {
            if (masterToggle.checked) {
                optionsSection.style.opacity = '1';
                optionsSection.style.pointerEvents = 'auto';
            } else {
                optionsSection.style.opacity = '0.5';
                optionsSection.style.pointerEvents = 'none';
            }
        }

        masterToggle.addEventListener('change', updateOptionsState);
        updateOptionsState();
    }
});
