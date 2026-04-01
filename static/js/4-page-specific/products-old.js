/* ================================================
   HENDOSHI - PRODUCTS OLD PAGE
   ================================================
   
   Purpose: JavaScript functionality for products old page
   
   Contains:
   - Event handlers
   - User interactions
   - Dynamic functionality
   
   Dependencies: utils.js (typically)
   Load Order: Load as needed for specific pages
   ================================================ */

document.getElementById('sort-selector').addEventListener('change', function() {
    window.location.href = this.value;
});
