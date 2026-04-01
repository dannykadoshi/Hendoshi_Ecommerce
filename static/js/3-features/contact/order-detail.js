/* ================================================
   HENDOSHI - ORDER DETAIL
   ================================================
   
   Purpose: JavaScript functionality for order detail
   
   Contains:
   - Event handlers
   - User interactions
   - Dynamic functionality
   
   Dependencies: utils.js (typically)
   Load Order: Load as needed for specific pages
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
