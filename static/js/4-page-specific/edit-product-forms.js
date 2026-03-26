/* ================================================
   HENDOSHI - EDIT PRODUCT FORMS
   ================================================
   
   Purpose: JavaScript functionality for edit product forms
   
   Contains:
   - Event handlers
   - User interactions
   - Dynamic functionality
   
   Dependencies: utils.js (typically)
   Load Order: Load as needed for specific pages
   ================================================ */

// Edit Product - Form Input Handlers, File Previews, Image Formset, Variant Status
document.addEventListener('DOMContentLoaded', function() {
    // Get ALL form inputs including formset fields
    const formInputs = document.querySelectorAll('#editProductForm .form-control, #editProductForm select.auth-form-input, #editProductForm input.auth-form-input');

    // File input clear X logic for main image
    const mainFileInput = document.querySelector('input[type="file"][name$="main_image"]');
    const mainClearX = document.querySelector('.file-input-wrapper > .clear-file-x');
    if (mainFileInput && mainClearX) {
        mainFileInput.addEventListener('change', function() {
            mainClearX.style.display = mainFileInput.value ? 'inline' : 'none';
            // Show preview using same markup as existing main image preview
            const wrapper = mainFileInput.closest('.file-input-wrapper');
            if (wrapper) {
                const existingPreview = wrapper.parentElement.querySelector('.image-preview-current');
                if (existingPreview && existingPreview.parentElement) existingPreview.parentElement.remove();
                if (mainFileInput.files && mainFileInput.files[0]) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const div = document.createElement('div');
                        div.className = 'mb-3';
                        const img = document.createElement('img');
                        img.src = e.target.result;
                        img.alt = 'Preview';
                        img.className = 'image-preview-current';
                        div.appendChild(img);
                        // insert preview before the file input wrapper (same structure as existing main image)
                        wrapper.parentElement.insertBefore(div, wrapper);
                        // remove any stray 'Preview' text-only nodes that may exist from empty form markup
                        Array.from(wrapper.parentElement.childNodes).forEach(function(node) {
                            try {
                                const text = (node.textContent || '').trim().toLowerCase();
                                if (text === 'preview') node.remove();
                            } catch (err) {
                                // ignore
                            }
                        });
                    };
                    reader.readAsDataURL(mainFileInput.files[0]);
                }
            }
        });
        mainClearX.addEventListener('click', function(e) {
            e.preventDefault();
            mainFileInput.value = '';
            mainClearX.style.display = 'none';
            const wrapper = mainFileInput.closest('.file-input-wrapper');
            if (wrapper) {
                const prev = wrapper.parentElement.querySelector('.image-preview-current');
                if (prev && prev.parentElement) prev.parentElement.remove();
            }
        });
    }

    // File input clear X logic for additional images
    document.querySelectorAll('.image-form-row .file-input-wrapper').forEach(function(wrapper) {
        const fileInput = wrapper.querySelector('input[type="file"]');
        const clearX = wrapper.querySelector('.clear-file-x');
        if (fileInput && clearX) {
            fileInput.addEventListener('change', function() {
                clearX.style.display = fileInput.value ? 'inline' : 'none';
            });
            clearX.addEventListener('click', function(e) {
                e.preventDefault();
                fileInput.value = '';
                clearX.style.display = 'none';
            });
        }
    });

    // Function to check if input has value (works for text, select, and number inputs)
    function checkInputValue(input) {
        if (input.tagName === 'SELECT') {
            // For select elements, check if a value is selected
            return input.value !== '' && input.value !== null;
        } else if (input.type === 'number') {
            // For number inputs, check if value exists
            return input.value !== '';
        } else {
            // For text inputs
            return input.value.trim() !== '';
        }
    }

    formInputs.forEach(input => {
        // Skip file inputs and checkboxes
        if (input.type === 'file' || input.type === 'checkbox') {
            return;
        }

        input.addEventListener('input', function() {
            const errorElement = this.closest('div').querySelector('.form-error-text');
            if (errorElement) {
                errorElement.style.display = 'none';
            }
            if (checkInputValue(this)) {
                this.classList.add('has-value');
            } else {
                this.classList.remove('has-value');
            }
        });

        input.addEventListener('change', function() {
            if (checkInputValue(this)) {
                this.classList.add('has-value');
            } else {
                this.classList.remove('has-value');
            }
        });

        input.addEventListener('blur', function() {
            if (checkInputValue(this)) {
                this.classList.add('has-value');
            }
        });

        input.addEventListener('focus', function() {
            const errorElement = this.closest('div').querySelector('.form-error-text');
            if (errorElement && !this.hasAttribute('required')) {
                errorElement.style.display = 'none';
            }
        });

        // Set initial state for all inputs with values
        if (checkInputValue(input)) {
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

            // ensure clearX exists
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
                    // Show preview
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
                                // remove any stray 'Preview' text-only nodes inside this row (from empty form)
                                Array.from(wrapper.querySelectorAll('*')).forEach(function(node) {
                                    try {
                                        const text = (node.textContent || '').trim().toLowerCase();
                                        if (text === 'preview') node.remove();
                                    } catch (err) {}
                                });
                                // insert preview at the top of the form row (same markup as main image preview)
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
                // Use empty form template
                const template = document.getElementById('emptyImageFormTemplate');
                newForm = document.createElement('div');
                newForm.className = 'image-form-row mb-4 p-4 dynamically-added';
                newForm.innerHTML = template.innerHTML.replace(/__prefix__/g, formCount);
            }

            // Add close button
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

            // Append new form and update total
            imageFormsetContainer.appendChild(newForm);
            totalForms.value = formCount + 1;

            // Attach listeners for preview and clear
            attachImageInputListeners(newForm);

            // Re-init inputs for value styling
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

    // Size/Color toggle status badges
    function updateVariantStatusBadge(checkbox) {
        const label = checkbox.closest('label');
        if (!label) return;
        const badge = label.querySelector('.variant-status-badge');
        if (!badge) return;

        if (checkbox.checked) {
            badge.textContent = 'In Use';
            badge.classList.remove('not-in-use');
            badge.classList.add('in-use');
        } else {
            badge.textContent = 'Not in Use';
            badge.classList.remove('in-use');
            badge.classList.add('not-in-use');
        }
    }

    document.querySelectorAll('#sizesToggles input[type="checkbox"], #colorToggles input[type="checkbox"]').forEach(checkbox => {
        updateVariantStatusBadge(checkbox);
        checkbox.addEventListener('change', function() {
            updateVariantStatusBadge(this);
        });
    });

});
