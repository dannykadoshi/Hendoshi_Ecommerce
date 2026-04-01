/* ================================================
   HENDOSHI - ORDER DETAIL
   ================================================

   Purpose: Provides copy-to-clipboard functionality for tracking numbers
            on the order detail page

   Contains:
   - window.copyTracking() — copies a tracking number to the clipboard via navigator.clipboard
   - Shows a showToast() success or error notification on copy result

   Dependencies: base.js (showToast)
   Load Order: Load on order detail page only
   ================================================ */

window.copyTracking = function(trackingNumber) {
    navigator.clipboard.writeText(trackingNumber).then(function() {
        if (typeof showToast === 'function') {
            showToast('Tracking number copied!', 'success');
        } else if (typeof window.alert !== 'undefined') {
            window.alert('Tracking number copied!');
        }
    }).catch(function() {
        if (typeof showToast === 'function') {
            showToast('Failed to copy tracking number', 'error');
        } else if (typeof window.alert !== 'undefined') {
            window.alert('Failed to copy tracking number');
        }
    });
};
