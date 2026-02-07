/* ================================================
   HENDOSHI - CREATE PRODUCT MODE
   ================================================
   
   Purpose: JavaScript functionality for create product mode
   
   Contains:
   - Event handlers
   - User interactions
   - Dynamic functionality
   
   Dependencies: utils.js (typically)
   Load Order: Load as needed for specific pages
   ================================================ */

// Creation Mode Toggle - Single vs Bulk
document.addEventListener('DOMContentLoaded', function() {
    const singleModeBtn = document.getElementById('singleModeBtn');
    const bulkModeBtn = document.getElementById('bulkModeBtn');
    const modeDescription = document.getElementById('modeDescription');
    
    if (bulkModeBtn) {
        bulkModeBtn.addEventListener('click', function() {
            // Get the bulk create URL from data attribute
            const bulkUrl = bulkModeBtn.dataset.bulkUrl;
            if (bulkUrl) {
                window.location.href = bulkUrl;
            }
        });
    }
    
    // Hover effects for descriptions
    if (singleModeBtn) {
        singleModeBtn.addEventListener('mouseenter', function() {
            if (modeDescription) {
                modeDescription.innerHTML = '<small>Create one product at a time with full customization</small>';
            }
        });
    }
    
    if (bulkModeBtn) {
        bulkModeBtn.addEventListener('mouseenter', function() {
            if (modeDescription) {
                modeDescription.innerHTML = '<small>Create multiple products at once by selecting types and audiences</small>';
            }
        });
    }
});
