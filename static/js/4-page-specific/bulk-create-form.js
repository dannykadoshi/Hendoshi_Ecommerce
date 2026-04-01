/* ================================================
   HENDOSHI - BULK CREATE FORM
   ================================================

   Purpose: Drives the admin bulk product creation form — auto-filling names,
            setting default prices, previewing images, and tracking form completion progress

   Contains:
   - Auto-fill product names from a base design name (on blur and button click)
   - Set default price across all unfilled price inputs via prompt dialog
   - Expand All / Collapse All accordion sections
   - Image preview on file input change using FileReader
   - Progress indicator that counts how many accordion items have all required fields filled
   - showStyledAlert() / closeStyledAlert() — custom modal alert (replaces browser alert)

   Dependencies: None (vanilla JS)
   Load Order: Load on admin bulk product creation form page only
   ================================================ */

// Bulk Create Form - Auto-fill, Progress Tracking, Image Preview, AI Generation
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
    // Auto-fill product names based on design name
    const baseDesignNameInput = document.querySelector('[name="base_design_name"]');
    const autoFillNamesBtn = document.getElementById('autoFillNamesBtn');
    
    function autoFillNames() {
        const designName = baseDesignNameInput.value.trim();
        if (!designName) {
            showStyledAlert('Please enter a Base Design Name first');
            return;
        }
        
        document.querySelectorAll('.bulk-product-name').forEach((input) => {
            const accordion = input.closest('.accordion-item');
            const titleSpan = accordion.querySelector('.product-title');
            const productInfo = titleSpan.textContent.replace(/\s+/g, ' ').trim();
            
            // Auto-fill: Design Name + Product Type + Audience
            input.value = `${designName} ${productInfo}`;
        });
    }
    
    autoFillNamesBtn.addEventListener('click', autoFillNames);
    
    // Auto-fill on design name change
    baseDesignNameInput.addEventListener('blur', autoFillNames);
    
    // Set default price
    const setDefaultPriceBtn = document.getElementById('setDefaultPriceBtn');
    setDefaultPriceBtn.addEventListener('click', function() {
        const price = prompt('Enter default price for all products (£):', '25.00');
        if (price) {
            document.querySelectorAll('.bulk-product-price').forEach(input => {
                if (!input.value) {
                    input.value = price;
                }
            });
        }
    });
    
    // Expand/Collapse all
    const expandAllBtn = document.getElementById('expandAllBtn');
    const collapseAllBtn = document.getElementById('collapseAllBtn');
    
    expandAllBtn.addEventListener('click', function() {
        document.querySelectorAll('.accordion-collapse').forEach(el => {
            if (!el.classList.contains('show')) {
                el.classList.add('show');
                el.previousElementSibling.querySelector('.accordion-button').classList.remove('collapsed');
            }
        });
    });
    
    collapseAllBtn.addEventListener('click', function() {
        document.querySelectorAll('.accordion-collapse').forEach((el) => {
            if (!el.classList.contains('show')) {
                el.classList.remove('show');
                el.previousElementSibling.querySelector('.accordion-button').classList.add('collapsed');
            }
        });
    });
    
    // Image preview
    document.querySelectorAll('.bulk-main-image').forEach(input => {
        input.addEventListener('change', function() {
            const prefix = this.name.split('-')[0];
            const preview = document.getElementById(`preview_${prefix}_main`);
            
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    });
    
    // Update progress indicator
    function updateProgress() {
        const totalProductsElem = document.querySelector('[data-total-products]');
        const totalProducts = totalProductsElem ? parseInt(totalProductsElem.dataset.totalProducts) : 0;
        let completed = 0;
        const progressList = document.getElementById('progressList');
        progressList.innerHTML = '';
        
        document.querySelectorAll('.accordion-item').forEach((item) => {
            const nameInput = item.querySelector('.bulk-product-name');
            const priceInput = item.querySelector('.bulk-product-price');
            const imageInput = item.querySelector('.bulk-main-image');
            const title = item.querySelector('.product-title').textContent.trim();
            
            const hasName = nameInput && nameInput.value.trim() && !nameInput.value.includes('{{');
            const hasPrice = priceInput && priceInput.value;
            const hasImage = imageInput && imageInput.files.length > 0;
            
            const isComplete = hasName && hasPrice && hasImage;
            if (isComplete) completed++;
            
            const badge = item.querySelector('.product-preview-badge');
            if (isComplete) {
                badge.textContent = '✓ Complete';
                badge.style.background = '#28a745';
            } else {
                badge.textContent = 'Incomplete';
                badge.style.background = '#dc3545';
            }
            
            const progressItem = document.createElement('div');
            progressItem.className = `progress-item ${isComplete ? 'complete' : 'incomplete'}`;
            progressItem.innerHTML = `
                <i class="fas fa-${isComplete ? 'check-circle' : 'times-circle'}"></i>
                <span>${title.substring(0, 20)}${title.length > 20 ? '...' : ''}</span>
            `;
            progressList.appendChild(progressItem);
        });
        
        const percent = Math.round((completed / totalProducts) * 100);
        document.getElementById('progressPercent').textContent = percent + '%';
    }
    
    // Update progress on input changes
    document.querySelectorAll('.bulk-product-name, .bulk-product-price, .bulk-main-image').forEach(input => {
        input.addEventListener('change', updateProgress);
        input.addEventListener('input', updateProgress);
    });
    
    // Initial progress update
    updateProgress();
    
    // AI Generation for base description template
    const generateSharedDescBtn = document.getElementById('generateSharedDescBtn');
    if (generateSharedDescBtn) {
        const generateDescUrl = generateSharedDescBtn.dataset.generateDescUrl;
        
        generateSharedDescBtn.addEventListener('click', function() {
            const designName = baseDesignNameInput.value;
            if (!designName) {
                showStyledAlert('Please enter a Base Design Name first');
                return;
            }
            
            const descTextarea = document.querySelector('[name="base_description"]');
            const btn = this;
            const originalText = btn.innerHTML;
            
            // Show loading state
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating...';
            
            // Use the design name for context
            const userInput = designName + ' design for various audiences';
            
            // Call AI endpoint
            fetch(generateDescUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    name: designName,
                    input: userInput
                })
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(errorData => {
                        // Check for quota errors in error message
                        const errorMsg = errorData.error || '';
                        if (errorMsg.includes('quota') || errorMsg.includes('429') || errorMsg.includes('exceeded')) {
                            throw new Error('⚠️ AI quota exceeded. Please wait a minute and try again, or check your Google API quota.');
                        }
                        throw new Error(errorMsg || 'Server error: ' + response.status);
                    }).catch(err => {
                        if (err.message) throw err;
                        throw new Error('Server error: ' + response.status);
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    showStyledAlert('Error: ' + data.error);
                    return;
                }
                
                if (data.descriptions && data.descriptions.length > 0) {
                    // Get the AI-generated description
                    let aiDescription = data.descriptions[0];
                    
                    // Create placeholder strings (avoid Django template rendering)
                    const productPlaceholder = '{{product_type}}';
                    const audiencePlaceholder = '{{audience}}';
                    
                    // Create a smart template by adding placeholders at the beginning
                    let templateDescription = 'This ' + productPlaceholder + ' is perfect for ' + audiencePlaceholder + ' who appreciate unique designs. ' + aiDescription;
                    
                    // If the description already starts with product-related language, integrate differently
                    if (aiDescription.toLowerCase().match(/^(this|these|the|a|an)/)) {
                        // Replace generic words with placeholders
                        templateDescription = aiDescription
                            .replace(/^this striking graphic design/i, 'This ' + productPlaceholder)
                            .replace(/^this design/i, 'This ' + productPlaceholder)
                            .replace(/^this product/i, 'This ' + productPlaceholder)
                            .replace(/^these products/i, 'These ' + productPlaceholder + 's')
                            .replace(/businesses and creators/gi, audiencePlaceholder)
                            .replace(/customers/gi, audiencePlaceholder)
                            .replace(/anyone/gi, audiencePlaceholder)
                            .replace(/everyone/gi, audiencePlaceholder)
                            .replace(/people/gi, audiencePlaceholder)
                            .replace(/for your/gi, 'for ' + audiencePlaceholder)
                            .replace(/any product line/gi, productPlaceholder + ' collection');
                    }
                    
                    // Fix any bracket-style placeholders to Django template syntax
                    templateDescription = templateDescription
                        .replace(/\[product type\]/gi, productPlaceholder)
                        .replace(/\[target audience\]/gi, audiencePlaceholder)
                        .replace(/\[audience\]/gi, audiencePlaceholder)
                        .replace(/\[product\]/gi, productPlaceholder)
                        .replace(/\{\{product type\}\}/gi, productPlaceholder)
                        .replace(/\{\{target audience\}\}/gi, audiencePlaceholder);
                    
                    // Set the template description
                    descTextarea.value = templateDescription;
                } else {
                    showStyledAlert('No suggestions generated. Please try again.');
                }
            })
            .catch(error => {
                showStyledAlert('Error generating description: ' + error.message);
            })
            .finally(() => {
                btn.disabled = false;
                btn.innerHTML = originalText;
            });
        });
    }
    
    // AI Generation for meta description template
    const generateSharedMetaBtn = document.getElementById('generateSharedMetaBtn');
    if (generateSharedMetaBtn) {
        const generateMetaUrl = generateSharedMetaBtn.dataset.generateMetaUrl;
        
        generateSharedMetaBtn.addEventListener('click', function() {
            const designName = baseDesignNameInput.value;
            if (!designName) {
                showStyledAlert('Please enter a Base Design Name first');
                return;
            }
            
            const metaTextarea = document.querySelector('[name="meta_description"]');
            const btn = this;
            const originalText = btn.innerHTML;
            
            // Show loading state
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating...';
            
            // Get the base description for context
            const baseDescTextarea = document.querySelector('[name="base_description"]');
            const baseDesc = baseDescTextarea ? baseDescTextarea.value.trim() : '';
            
            if (!baseDesc) {
                showStyledAlert('Please fill in the base description template first.');
                btn.disabled = false;
                btn.innerHTML = originalText;
                return;
            }
            
            // Call AI endpoint for meta description
            fetch(generateMetaUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    description: baseDesc,
                    name: designName
                })
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(errorData => {
                        // Check for quota errors in error message
                        const errorMsg = errorData.error || '';
                        if (errorMsg.includes('quota') || errorMsg.includes('429') || errorMsg.includes('exceeded')) {
                            throw new Error('⚠️ AI quota exceeded. Please wait a minute and try again, or check your Google API quota.');
                        }
                        throw new Error(errorMsg || 'Server error: ' + response.status);
                    }).catch(err => {
                        if (err.message) throw err;
                        throw new Error('Server error: ' + response.status);
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    showStyledAlert('Error: ' + data.error);
                    return;
                }
                
                if (data.suggestions && data.suggestions.length > 0) {
                    // Get the AI-generated meta description
                    let metaDescription = data.suggestions[0];
                    
                    // Create placeholder strings
                    const productPlaceholder = '{{product_type}}';
                    const audiencePlaceholder = '{{audience}}';
                    
                    // Make it a template with placeholders
                    metaDescription = metaDescription
                        .replace(/this striking graphic design/i, productPlaceholder)
                        .replace(/this design/i, productPlaceholder)
                        .replace(/this product/i, productPlaceholder)
                        .replace(/these products/i, productPlaceholder + 's')
                        .replace(/hoodie|t-shirt|tshirt|dress|mug|sticker|canvas|notebook/gi, productPlaceholder)
                        .replace(/men|women|kids|unisex|male|female/gi, audiencePlaceholder)
                        .replace(/everyone/gi, audiencePlaceholder)
                        .replace(/anyone/gi, audiencePlaceholder)
                        .replace(/\[product type\]/gi, productPlaceholder)
                        .replace(/\[target audience\]/gi, audiencePlaceholder)
                        .replace(/\[audience\]/gi, audiencePlaceholder);
                    
                    // Ensure it's under 160 characters
                    if (metaDescription.length > 160) {
                        metaDescription = metaDescription.substring(0, 157) + '...';
                    }
                    
                    // Set the template meta description
                    metaTextarea.value = metaDescription;
                } else {
                    showStyledAlert('No suggestions generated. Please try again.');
                }
            })
            .catch(error => {
                showStyledAlert('Error generating meta description: ' + error.message);
            })
            .finally(() => {
                btn.disabled = false;
                btn.innerHTML = originalText;
            });
        });
    }
    
    // Gallery Images: Add and Remove functionality
    document.addEventListener('click', function(e) {
        // Add gallery image
        if (e.target.closest('.add-gallery-image')) {
            const btn = e.target.closest('.add-gallery-image');
            const container = btn.previousElementSibling;
            const prefix = container.dataset.prefix;
            
            const newItem = document.createElement('div');
            newItem.className = 'gallery-image-item mb-2';
            newItem.innerHTML = `
                <div class="d-flex align-items-center gap-2">
                    <input type="file" name="${prefix}-gallery_images" class="form-control auth-form-input gallery-image-input" accept="image/*">
                    <button type="button" class="btn btn-sm btn-outline-danger remove-gallery-image">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;
            container.appendChild(newItem);
            
            // Show remove button on first item if there are now multiple items
            const items = container.querySelectorAll('.gallery-image-item');
            if (items.length > 1) {
                items.forEach(item => {
                    const removeBtn = item.querySelector('.remove-gallery-image');
                    if (removeBtn) removeBtn.style.display = 'block';
                });
            }
        }
        
        // Remove gallery image
        if (e.target.closest('.remove-gallery-image')) {
            const btn = e.target.closest('.remove-gallery-image');
            const item = btn.closest('.gallery-image-item');
            const container = item.closest('.gallery-images-container');
            
            item.remove();
            
            // Hide remove button on last remaining item
            const items = container.querySelectorAll('.gallery-image-item');
            if (items.length === 1) {
                const removeBtn = items[0].querySelector('.remove-gallery-image');
                if (removeBtn) removeBtn.style.display = 'none';
            }
        }
    });
    
    // Show remove buttons on file inputs that have files selected
    document.addEventListener('change', function(e) {
        if (e.target.classList.contains('gallery-image-input')) {
            const container = e.target.closest('.gallery-images-container');
            const items = container.querySelectorAll('.gallery-image-item');
            
            if (items.length > 1) {
                items.forEach(item => {
                    const removeBtn = item.querySelector('.remove-gallery-image');
                    if (removeBtn) removeBtn.style.display = 'block';
                });
            }
        }
    });
});
