/* ================================================
   HENDOSHI - PRODUCTS OLD PAGE
   ================================================

   Purpose: Legacy sort selector handler for the old product listing page;
            redirects to the selected sort URL on change (superseded by products-filters.js)

   Contains:
   - change event listener on #sort-selector that sets window.location.href to the selected value

   Dependencies: None (vanilla JS)
   Load Order: Legacy — only loaded if the old product listing template is still in use
   ================================================ */

document.getElementById('sort-selector').addEventListener('change', function() {
    window.location.href = this.value;
});
