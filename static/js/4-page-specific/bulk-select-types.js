/* ================================================
   HENDOSHI - BULK SELECT TYPES
   ================================================
   
   Purpose: JavaScript functionality for bulk select types
   
   Contains:
   - Event handlers
   - User interactions
   - Dynamic functionality
   
   Dependencies: utils.js (typically)
   Load Order: Load as needed for specific pages
   ================================================ */

// Bulk Select Types - Product Type & Audience Selection, Total Calculation
// Styled alert modal functions
function showStyledAlert(message) {
    const modal = document.getElementById('styledAlertModal');
    const messageEl = document.getElementById('styledAlertMessage');
    messageEl.textContent = message;
    modal.style.display = 'block';
}

function closeStyledAlert() {
    const modal = document.getElementById('styledAlertModal');
    modal.style.display = 'none';
}

// Close modal when clicking outside
window.addEventListener('click', function(event) {
    const modal = document.getElementById('styledAlertModal');
    if (event.target === modal) {
        closeStyledAlert();
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const productTypeCards = document.querySelectorAll('.product-type-card');
    const audienceCards = document.querySelectorAll('.audience-card');
    const audienceSection = document.getElementById('audienceSection');
    const selectionSummary = document.getElementById('selectionSummary');
    const totalCountSpan = document.getElementById('totalCount');
    const summaryDetails = document.getElementById('summaryDetails');
    const submitBtn = document.getElementById('submitBtn');
    
    // Toggle product type selection
    productTypeCards.forEach(card => {
        card.addEventListener('click', function() {
            const checkbox = this.querySelector('input[type="checkbox"]');
            checkbox.checked = !checkbox.checked;
            this.classList.toggle('selected', checkbox.checked);
            updateSelection();
        });
    });
    
    // Toggle audience selection
    audienceCards.forEach(card => {
        card.addEventListener('click', function() {
            const checkbox = this.querySelector('input[type="checkbox"]');
            checkbox.checked = !checkbox.checked;
            this.classList.toggle('selected', checkbox.checked);
            updateSelection();
        });
    });
    
    function isApparelType(card) {
        const category = (card.dataset.category || '').toLowerCase();
        if (category === 'apparel') return true;
        const name = (card.querySelector('.name')?.textContent || '').toLowerCase();
        return ['tshirt', 't-shirt', 'hoodie', 'dress', 'dresses', 'tee', 't shirt'].some(token => name.includes(token));
    }

    function updateSelection() {
        const selectedTypes = Array.from(document.querySelectorAll('.product-type-checkbox:checked'));
        const selectedAudiences = Array.from(document.querySelectorAll('.audience-checkbox:checked'));
        
        // Check if any selected type requires audience
        const requiresAudience = selectedTypes.some(checkbox => {
            const card = checkbox.closest('.product-type-card');
            return card.dataset.requiresAudience === 'true' && isApparelType(card);
        });
        
        // Show/hide audience section
        if (requiresAudience && selectedTypes.length > 0) {
            audienceSection.style.display = 'block';
        } else {
            audienceSection.style.display = 'none';
        }
        
        // Calculate total products
        let totalProducts = 0;
        const typesRequiringAudience = [];
        const typesNotRequiringAudience = [];
        
        selectedTypes.forEach(checkbox => {
            const card = checkbox.closest('.product-type-card');
            const typeName = card.querySelector('.name').textContent;
            
            const needsAudience = card.dataset.requiresAudience === 'true' && isApparelType(card);
            if (needsAudience) {
                typesRequiringAudience.push(typeName);
                totalProducts += selectedAudiences.length;
            } else {
                typesNotRequiringAudience.push(typeName);
                totalProducts += 1;
            }
        });
        
        // Update UI
        if (totalProducts > 0) {
            selectionSummary.style.display = 'block';
            totalCountSpan.textContent = totalProducts;
            
            let details = '';
            if (typesRequiringAudience.length > 0) {
                details += `<div class="mb-2"><strong>With Audience:</strong> ${typesRequiringAudience.join(', ')}</div>`;
                if (selectedAudiences.length > 0) {
                    const audienceNames = selectedAudiences.map(cb => cb.closest('.audience-card').querySelector('.name').textContent.trim());
                    details += `<div class="mb-2"><strong>Audiences:</strong> ${audienceNames.join(', ')}</div>`;
                } else {
                    details += `<div class="mb-2 text-warning"><i class="fas fa-exclamation-triangle me-2"></i>Please select at least one audience</div>`;
                }
            }
            if (typesNotRequiringAudience.length > 0) {
                details += `<div><strong>Without Audience:</strong> ${typesNotRequiringAudience.join(', ')}</div>`;
            }
            summaryDetails.innerHTML = details;
            
            // Enable submit if valid
            const isValid = selectedTypes.length > 0 && 
                (typesRequiringAudience.length === 0 || selectedAudiences.length > 0);
            submitBtn.disabled = !isValid;
        } else {
            selectionSummary.style.display = 'none';
            submitBtn.disabled = true;
        }
    }
    
    // Initialize
    updateSelection();
});
