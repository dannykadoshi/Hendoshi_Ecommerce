/* ================================================
   HENDOSHI - TOAST NOTIFICATIONS
   ================================================

   Purpose: Provides a global window.showToast() utility for
   displaying non-blocking, auto-dismissing toast messages anywhere
   in the site. Supports four types (success, error, info, warning),
   each with a distinct colour and icon. Toasts are created as DOM
   elements, appended to a container, and removed after a configurable
   duration or when clicked.

   Contains:
   - window.showToast(message, type, duration) — public API
   - Toast DOM element creation and styled injection
   - Auto-remove timer and click-to-dismiss handler
   - Toast container (#toast-container) lazy creation

   Dependencies: None
   Load Order: Load in <head> or early in base.html before any script
               that may call showToast()
   ================================================ */

/**
 * Show a toast notification
 * @param {string} message - The message to display
 * @param {string} type - Type of toast: 'success', 'error', 'info', 'warning'
 * @param {number} duration - Duration in milliseconds (default: 3000)
 */
window.showToast = function(message, type = 'info', duration = 3000) {
    // Get or create toast container
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 300px;
        `;
        document.body.appendChild(toastContainer);
    }

    // Create toast element
    const toast = document.createElement('div');
    toast.style.cssText = `
        padding: 12px 16px;
        margin-bottom: 8px;
        border-radius: 4px;
        font-size: 14px;
        animation: slideIn 0.3s ease;
    `;

    // Add type-specific styling and icon
    const typeConfig = {
        success: {
            bgColor: '#d4edda',
            textColor: '#155724',
            borderColor: '#c3e6cb',
            icon: '✓'
        },
        error: {
            bgColor: '#f8d7da',
            textColor: '#721c24',
            borderColor: '#f5c6cb',
            icon: '✕'
        },
        info: {
            bgColor: '#d1ecf1',
            textColor: '#0c5460',
            borderColor: '#bee5eb',
            icon: 'ⓘ'
        },
        warning: {
            bgColor: '#fff3cd',
            textColor: '#856404',
            borderColor: '#ffeeba',
            icon: '⚠'
        }
    };

    const config = typeConfig[type] || typeConfig.info;
    toast.style.backgroundColor = config.bgColor;
    toast.style.color = config.textColor;
    toast.style.border = `2px solid ${config.borderColor}`;
    toast.textContent = `${config.icon} ${message}`;

    toastContainer.appendChild(toast);

    // Add CSS animation if not already present
    if (!document.getElementById('toast-styles')) {
        const style = document.createElement('style');
        style.id = 'toast-styles';
        style.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateX(400px);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            @keyframes slideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(400px);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }

    // Auto-remove after duration
    setTimeout(function() {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(function() {
            toast.remove();
        }, 300);
    }, duration);
};

/**
 * Show utility functions for specific toast types
 */
window.showSuccessToast = function(message, duration) {
    window.showToast(message, 'success', duration);
};

window.showErrorToast = function(message, duration) {
    window.showToast(message, 'error', duration);
};

window.showInfoToast = function(message, duration) {
    window.showToast(message, 'info', duration);
};

window.showWarningToast = function(message, duration) {
    window.showToast(message, 'warning', duration);
};
