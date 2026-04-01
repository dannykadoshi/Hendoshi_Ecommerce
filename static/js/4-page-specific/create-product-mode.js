/* ================================================
   HENDOSHI - CREATE PRODUCT MODE
   ================================================

   Purpose: Handles the Single vs Bulk mode toggle on the product creation
            entry page, redirecting to the bulk creation tool when selected

   Contains:
   - Click handler on #bulkModeBtn to redirect to the bulk create URL (from data attribute)
   - Hover handlers that update the #modeDescription hint text dynamically

   Dependencies: None (vanilla JS)
   Load Order: Load on admin product creation mode selection page only
   ================================================ */

// Creation Mode Toggle - Single vs Bulk
document.addEventListener('DOMContentLoaded', function() {
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
        
        // Hover effects for descriptions
        bulkModeBtn.addEventListener('mouseenter', function() {
            if (modeDescription) {
                modeDescription.innerHTML = '<small>Create multiple products at once by selecting types and audiences</small>';
            }
        });
        
        bulkModeBtn.addEventListener('mouseleave', function() {
            if (modeDescription) {
                modeDescription.innerHTML = '<small>Need to create multiple products? Use our bulk creation tool</small>';
            }
        });
    }
});
