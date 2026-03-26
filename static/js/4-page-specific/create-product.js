/* ================================================
   HENDOSHI - CREATE PRODUCT
   ================================================
   
   Purpose: JavaScript functionality for create product
   
   Contains:
   - Event handlers
   - User interactions
   - Dynamic functionality
   
   Dependencies: utils.js (typically)
   Load Order: Load as needed for specific pages
   ================================================ */

// Create Product Page - Form Input Handlers, Image Formset, Variant Preview
document.addEventListener('DOMContentLoaded', function() {
    // Function to check if input has value
    function checkInputValue(input) {
        if (!input) return false;
        if (input.tagName === 'SELECT') {
            return input.value !== '' && input.value !== null;
        } else if (input.type === 'number') {
            return input.value !== '';
        } else {
            return input.value.trim() !== '';
        }
    }

    // Form inputs - add has-value class for floating labels
    const formInputs = document.querySelectorAll('#createProductForm .form-control');
    
    formInputs.forEach(input => {
        input.addEventListener('input', function() {
            const errorElement = this.closest('div').querySelector('.form-error-text');
            if (errorElement) {
                errorElement.style.display = 'none';
            }
            if (this.value.trim() !== '') {
                this.classList.add('has-value');
            } else {
                this.classList.remove('has-value');
            }
        });

        input.addEventListener('blur', function() {
            if (this.value.trim() !== '') {
                this.classList.add('has-value');
            }
        });

        input.addEventListener('focus', function() {
            const errorElement = this.closest('div').querySelector('.form-error-text');
            if (errorElement && !this.hasAttribute('required')) {
                errorElement.style.display = 'none';
            }
        });

        if (input.value.trim() !== '') {
            input.classList.add('has-value');
        }
    });

    // Add Image Button Functionality
    const addImageBtn = document.getElementById('addImageBtn');
    const imageFormsetContainer = document.getElementById('imageFormsetContainer');

    if (addImageBtn && imageFormsetContainer) {
        const attachImageInputListeners = function(wrapper) {
            if (!wrapper) return;
            const fileInput = wrapper.querySelector('input[type="file"]');
            const clearX = wrapper.querySelector('.clear-file-x');

            if (clearX) {
                clearX.style.display = fileInput && fileInput.value ? 'inline' : 'none';
                clearX.addEventListener('click', function(e) {
                    e.preventDefault();
                    if (fileInput) fileInput.value = '';
                    clearX.style.display = 'none';
                    const prev = wrapper.querySelector('.image-preview-current');
                    if (prev && prev.parentElement) prev.parentElement.remove();
                });
            }

            if (fileInput) {
                fileInput.addEventListener('change', function() {
                    if (clearX) clearX.style.display = fileInput.value ? 'inline' : 'none';
                    const existingPreview = wrapper.querySelector('.image-preview-current');
                    if (existingPreview && existingPreview.parentElement) existingPreview.parentElement.remove();
                    if (fileInput.files && fileInput.files[0]) {
                        const reader = new FileReader();
                        reader.onload = function(e) {
                            const div = document.createElement('div');
                            div.className = 'mb-3';
                            const img = document.createElement('img');
                            img.src = e.target.result;
                            img.alt = 'Preview';
                            img.className = 'image-preview-current';
                            div.appendChild(img);
                            Array.from(wrapper.querySelectorAll('*')).forEach(function(node) {
                                try {
                                    const text = (node.textContent || '').trim().toLowerCase();
                                    if (text === 'preview') node.remove();
                                } catch (err) {}
                            });
                            wrapper.insertBefore(div, wrapper.firstChild);
                        };
                        reader.readAsDataURL(fileInput.files[0]);
                    }
                });
            }
        };

        addImageBtn.addEventListener('click', function() {
            const totalForms = document.querySelector('input[name="images-TOTAL_FORMS"]');
            const formCount = parseInt(totalForms.value || '0');
            const lastForm = imageFormsetContainer.querySelector('.image-form-row:last-of-type');
            let newForm;

            if (lastForm) {
                newForm = lastForm.cloneNode(true);
                newForm.style.position = 'relative';
                newForm.classList.add('dynamically-added');
                const formRegex = new RegExp('images-\\d+-', 'g');
                newForm.innerHTML = newForm.innerHTML.replace(formRegex, `images-${formCount}-`);
                newForm.querySelectorAll('input[type="text"], input[type="number"], input[type="file"]').forEach(input => {
                    input.value = '';
                    input.classList.remove('has-value');
                });
                const imagePreview = newForm.querySelector('.image-preview-current');
                if (imagePreview && imagePreview.parentElement) {
                    imagePreview.parentElement.remove();
                }
                const deleteCheckbox = newForm.querySelector('input[type="checkbox"]');
                if (deleteCheckbox) deleteCheckbox.checked = false;
            } else {
                const template = document.getElementById('emptyImageFormTemplate');
                newForm = document.createElement('div');
                newForm.className = 'image-form-row mb-4 p-4 dynamically-added';
                newForm.innerHTML = template.innerHTML.replace(/__prefix__/g, formCount);
            }

            const totalFormsField = document.querySelector('input[name="images-TOTAL_FORMS"]');
            const closeBtn = document.createElement('button');
            closeBtn.type = 'button';
            closeBtn.className = 'btn-close-formset';
            closeBtn.innerHTML = '×';
            closeBtn.title = 'Remove this form';
            closeBtn.addEventListener('click', function() {
                newForm.remove();
                totalFormsField.value = parseInt(totalFormsField.value) - 1;
            });
            newForm.insertBefore(closeBtn, newForm.firstChild);

            imageFormsetContainer.appendChild(newForm);
            totalForms.value = formCount + 1;

            attachImageInputListeners(newForm);

            const newInputs = newForm.querySelectorAll('.form-control, select.auth-form-input, input.auth-form-input');
            newInputs.forEach(input => {
                if (input.type === 'file' || input.type === 'checkbox') return;
                input.addEventListener('input', function() {
                    if (checkInputValue(this)) this.classList.add('has-value'); else this.classList.remove('has-value');
                });
                input.addEventListener('change', function() {
                    if (checkInputValue(this)) this.classList.add('has-value'); else this.classList.remove('has-value');
                });
            });
        });
    }

    // Variant Selection Toggle Preview Functionality
    function updateVariantPreview() {
        const sizeCheckboxes = document.querySelectorAll('#sizesToggles input[type="checkbox"]:checked');
        const colorCheckboxes = document.querySelectorAll('#colorToggles input[type="checkbox"]:checked');
        const previewList = document.getElementById('variantPreviewList');
        if (!previewList) return; // preview removed — no-op

        // Get label text from parent label element (Django's CheckboxSelectMultiple structure)
        const selectedSizes = Array.from(sizeCheckboxes).map(cb => {
            const label = cb.closest('label');
            // Get text content excluding the checkbox itself
            const text = label ? label.textContent.trim() : cb.value;
            return { value: cb.value, label: text };
        });
        const selectedColors = Array.from(colorCheckboxes).map(cb => {
            const label = cb.closest('label');
            const text = label ? label.textContent.trim() : cb.value;
            return { value: cb.value, label: text };
        });

        let variants = [];

        // Generate combinations
        if (selectedSizes.length && selectedColors.length) {
            selectedSizes.forEach(size => {
                selectedColors.forEach(color => {
                    variants.push(`${size.label} / ${color.label}`);
                });
            });
        } else if (selectedSizes.length) {
            variants = selectedSizes.map(s => s.label);
        } else if (selectedColors.length) {
            variants = selectedColors.map(c => c.label);
        }

        // Update preview
        if (variants.length) {
            previewList.innerHTML = variants.map(v =>
                `<span class="variant-preview-item">${v}</span>`
            ).join('') +
            `<div class="variant-count w-100"><i class="fas fa-layer-group me-2"></i>${variants.length} variant(s) will be created</div>`;
        } else {
            previewList.innerHTML = '<p class="text-muted">Select sizes and/or colors above to see variant combinations</p>';
        }
    }

    // Add event listeners to all toggle checkboxes
    document.querySelectorAll('.variant-toggles input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', updateVariantPreview);
    });

    // Initial update
    updateVariantPreview();
});
