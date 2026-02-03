/**
 * Order Detail - Copy tracking number utility
 */

window.copyTracking = function(trackingNumber) {
    navigator.clipboard.writeText(trackingNumber).then(function() {
        if (typeof showToast === 'function') {
            showToast('Tracking number copied!', 'success');
        } else {
            alert('Tracking number copied!');
        }
    }).catch(function(err) {
        console.error('Failed to copy: ', err);
        if (typeof showToast === 'function') {
            showToast('Failed to copy tracking number', 'error');
        } else {
            alert('Failed to copy tracking number');
        }
    });
};
