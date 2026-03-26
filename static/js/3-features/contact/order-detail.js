/**
 * Order Detail - Copy tracking number utility
 */

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
