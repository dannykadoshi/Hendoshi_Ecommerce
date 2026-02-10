/* ================================================
   HENDOSHI - VAULT FUNCTIONALITY
   ================================================
   
   Purpose: Core JavaScript for vault photo gallery including filtering,
            voting, liking, and photo submission functionality.
   
   Contains:
   - Gallery filter dropdown logic
   - Photo voting system (upvote/downvote)
   - Photo liking/unliking functionality
   - Featured photo interactions
   - Product filter chip management
// Debug: indicate vault.js loaded
if (typeof console !== 'undefined' && console.info) {
    console.info('[vault.js] loaded');
}
   - Hall of Fame vote/like handling

   Dependencies: Requires vault-hall-of-fame.js for Hall of Fame specific events
   Load Order: Before vault-hall-of-fame.js, after core utilities
   ================================================ */

    // Contains all vault-specific functionality

// Analytics tracking for vault interactions
function trackVaultEvent(action, details = {}) {
    if (typeof gtag !== 'undefined') {
        gtag('event', 'vault_interaction', {
            page_location: window.location.pathname,
            ...details
        });
    }
}

// Gallery Filter Dropdown
// Gallery Filter Dropdown - REMOVED

// Initialize product chip interactions
// Initialize product chip interactions - REMOVED

// Gallery Like Functionality
function initializeGalleryLikes() {
    // Like photo from gallery cards - unified function
    window.likePhotoFromGallery = function(photoId) {
        likePhotoUnified(photoId, 'gallery');
    };
}

// Photo Detail Like Functionality
function initializePhotoDetailLikes() {
    window.likePhoto = function(photoId) {
        likePhotoUnified(photoId, 'detail');
    };
}

// Unified like function that works for both gallery and detail views
function likePhotoUnified(photoId, source) {
    const url = `/vault/photo/${photoId}/like/`;
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        
        // Update likes count elements in gallery/featured views (if exist)
        const galleryLikesElements = document.querySelectorAll(`[data-likes-for="${photoId}"]`);
        if (galleryLikesElements && galleryLikesElements.length) {
            galleryLikesElements.forEach(el => {
                el.innerHTML = `<i class="fas fa-heart"></i> ${data.likes}`;
            });
        }

        // Update detail view like badge (if exists) - now handles both display and active state
        const likeBadge = document.getElementById(`like-badge-${photoId}`);
        if (likeBadge) {
            likeBadge.innerHTML = `<i class="fas fa-heart"></i> <span>${data.likes}</span>`;
            if (data.liked) {
                likeBadge.classList.add('active-like');
            } else {
                likeBadge.classList.remove('active-like');
            }
        }

        // Update detail view like button styling (if exists) - keeping for backward compatibility
        const detailButton = document.getElementById(`like-button-${photoId}`);
        if (detailButton) {
            if (data.liked) {
                detailButton.classList.add('active-like');
            } else {
                detailButton.classList.remove('active-like');
            }
        }

        // Update all like buttons by data-photo-id attribute
        const likeButtons = document.querySelectorAll(`button[data-photo-id="${photoId}"]`);
        if (likeButtons && likeButtons.length) {
            likeButtons.forEach(btn => {
                if (data.liked) {
                    btn.classList.add('liked');
                } else {
                    btn.classList.remove('liked');
                }
            });
        }
        
        // Update Hall of Fame like buttons (data-action="like-photo")
        const hallLikeButtons = document.querySelectorAll(`button[data-action="like-photo"][data-photo-id="${photoId}"]`);
        if (hallLikeButtons && hallLikeButtons.length) {
            hallLikeButtons.forEach(btn => {
                // Keep the heart icon and just update the count
                btn.innerHTML = `<i class="fas fa-heart"></i> ${data.likes}`;
                
                // Update button style based on liked status
                if (data.liked) {
                    btn.classList.add('liked');
                    btn.classList.remove('btn-pink');
                    btn.classList.add('btn-success');
                } else {
                    btn.classList.remove('liked');
                    btn.classList.add('btn-pink');
                    btn.classList.remove('btn-success');
                }
            });
        }
    })
    .catch(error => console.error('Error liking photo:', error));
}

// Voting Functionality
function initializeVoting() {
    window.votePhoto = function(photoId, voteType) {
        const url = `/vault/photo/${photoId}/vote/${voteType}/`;
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }

            // Update detail view buttons (with specific IDs)
            const detailUpvoteButton = document.getElementById(`upvote-button-${photoId}`);
            if (detailUpvoteButton) {
                // Update button text with new count
                detailUpvoteButton.innerHTML = `<i class="fas fa-thumbs-up"></i> ${data.upvotes}`;

                if (data.user_vote === 'up') {
                    detailUpvoteButton.classList.add('btn-success');
                    detailUpvoteButton.classList.remove('btn-outline-success');
                } else {
                    detailUpvoteButton.classList.add('btn-outline-success');
                    detailUpvoteButton.classList.remove('btn-success');
                }
            }

            const detailDownvoteButton = document.getElementById(`downvote-button-${photoId}`);
            if (detailDownvoteButton) {
                // Update button text with new count
                detailDownvoteButton.innerHTML = `<i class="fas fa-thumbs-down"></i> ${data.downvotes}`;

                if (data.user_vote === 'down') {
                    detailDownvoteButton.classList.add('btn-danger');
                    detailDownvoteButton.classList.remove('btn-outline-danger');
                } else {
                    detailDownvoteButton.classList.add('btn-outline-danger');
                    detailDownvoteButton.classList.remove('btn-danger');
                }
            }

            // Update Hall of Fame gallery buttons (data-action="vote")
            const allUpvoteButtons = document.querySelectorAll(`button[data-action="vote"][data-photo-id="${photoId}"][data-vote-type="up"]`);
            allUpvoteButtons.forEach(button => {
                if (data.user_vote === 'up') {
                    button.classList.add('btn-success');
                    button.classList.remove('btn-outline-success');
                } else {
                    button.classList.add('btn-outline-success');
                    button.classList.remove('btn-success');
                }
            });

            const allDownvoteButtons = document.querySelectorAll(`button[data-action="vote"][data-photo-id="${photoId}"][data-vote-type="down"]`);
            allDownvoteButtons.forEach(button => {
                if (data.user_vote === 'down') {
                    button.classList.add('btn-danger');
                    button.classList.remove('btn-outline-danger');
                } else {
                    button.classList.add('btn-outline-danger');
                    button.classList.remove('btn-danger');
                }
            });

            // Update stats row counts dynamically
            const statsUpvotes = document.querySelectorAll(`.stat-item .fa-thumbs-up + span`);
            statsUpvotes.forEach(span => {
                if (span.closest('.hall-of-fame-card')?.querySelector(`[data-photo-id="${photoId}"]`)) {
                    span.textContent = data.upvotes;
                }
            });
            
            const statsDownvotes = document.querySelectorAll(`.stat-item .fa-thumbs-down + span`);
            statsDownvotes.forEach(span => {
                if (span.closest('.hall-of-fame-card')?.querySelector(`[data-photo-id="${photoId}"]`)) {
                    span.textContent = data.downvotes;
                }
            });
            
            const statsScore = document.querySelectorAll(`.stat-item .fa-chart-line + span`);
            statsScore.forEach(span => {
                if (span.closest('.hall-of-fame-card')?.querySelector(`[data-photo-id="${photoId}"]`)) {
                    span.textContent = data.vote_score;
                }
            });

            // Update vote score display if it exists
            const voteScoreElement = document.getElementById(`vote-score-${photoId}`);
            if (voteScoreElement) {
                voteScoreElement.textContent = `Score: ${data.vote_score}`;
            }
        })
        .catch(error => console.error('Error voting on photo:', error));
    };
}

// Social Share Functionality for Vault Photo Detail
function initializePhotoDetailShare() {
    var shareButtons = document.querySelectorAll('.vault-sidebar-share-buttons .share-btn');

    shareButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var platform = this.dataset.platform;
            var photoCaption = this.dataset.photoCaption || '';
            var photoUrl = this.dataset.photoUrl || window.location.href;
            var photoImage = this.dataset.photoImage || '';

            switch(platform) {
                case 'native':
                    shareNative(photoUrl, photoCaption);
                    break;
                case 'facebook':
                    shareToFacebook(photoUrl, photoCaption);
                    break;
                case 'twitter':
                    shareToTwitter(photoUrl, photoCaption);
                    break;
                case 'pinterest':
                    shareToPinterest(photoUrl, photoCaption, photoImage);
                    break;
                case 'instagram':
                    shareToInstagram(photoUrl, photoCaption);
                    break;
                case 'copy-link':
                    copyToClipboard(photoUrl, this);
                    break;
            }
        });
    });

    function shareNative(url, caption) {
        if (navigator.share) {
            navigator.share({
                title: 'HENDOSHI Vault Photo',
                text: caption,
                url: url
            }).catch(function(err) {
                
            });
        } else {
            copyToClipboard(url, document.querySelector('.copy-link-btn'));
        }
    }

    function shareToFacebook(url, caption) {
        var shareUrl = 'https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(url) + '&quote=' + encodeURIComponent(caption);
        window.open(shareUrl, 'facebook-share', 'width=600,height=400');
    }

    function shareToTwitter(url, caption) {
        var text = caption + ' ' + url;
        var shareUrl = 'https://twitter.com/intent/tweet?text=' + encodeURIComponent(text);
        window.open(shareUrl, 'twitter-share', 'width=600,height=400');
    }

    function shareToPinterest(url, caption, image) {
        var shareUrl = 'https://pinterest.com/pin/create/button/?url=' + encodeURIComponent(url) + '&description=' + encodeURIComponent(caption);
        if (image) {
            shareUrl += '&media=' + encodeURIComponent(image);
        }
        window.open(shareUrl, 'pinterest-share', 'width=600,height=400');
    }

    function shareToInstagram(url, caption) {
        copyToClipboard(url, document.querySelector('.copy-link-btn'));
        alert('Link copied! Open Instagram and paste in your story or bio.');
    }

    function copyToClipboard(url, button) {
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(url).then(function() {
                showCopySuccess(button);
            }).catch(function(err) {
                fallbackCopy(url, button);
            });
        } else {
            fallbackCopy(url, button);
        }
    }

    function fallbackCopy(text, button) {
        var textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();

        try {
            var successful = document.execCommand('copy');
            if (successful) {
                showCopySuccess(button);
            }
        } catch (err) {
            console.error('Copy failed:', err);
        }

        document.body.removeChild(textArea);
    }

    function showCopySuccess(button) {
        if (!button) return;
        var originalIcon = button.innerHTML;
        button.classList.add('copied');
        button.innerHTML = '<i class="fas fa-check"></i>';

        setTimeout(function() {
            button.classList.remove('copied');
            button.innerHTML = originalIcon;
        }, 2000);
    }
}

// Submit Photo Multi-Select
function initializeSubmitMultiSelect() {
    const multiSelect = document.getElementById('product_tags');
    const tagInput = document.getElementById('tag_input');
    const selectedTags = document.getElementById('selected_tags');
    const dropdown = document.getElementById('product_dropdown');
    const hiddenInput = document.getElementById('product_ids');
    
    // Only initialize if required elements exist (submit photo page)
    if (!multiSelect || !tagInput || !selectedTags || !dropdown || !hiddenInput) return;
    
    const items = dropdown.querySelectorAll('.vault-dropdown-item');

    let selectedProducts = [];
    let selectedIndex = -1;

    function showDropdown() {
        dropdown.style.display = 'block';
        filterItems();
    }

    function hideDropdown() {
        dropdown.style.display = 'none';
        selectedIndex = -1;
        items.forEach(item => item.classList.remove('selected'));
    }

    function filterItems() {
        const query = tagInput.value.toLowerCase();
        let hasVisibleItems = false;

        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            const isSelected = selectedProducts.includes(item.dataset.value);
            if (text.includes(query) && !isSelected) {
                item.style.display = 'block';
                hasVisibleItems = true;
            } else {
                item.style.display = 'none';
            }
        });

        dropdown.style.display = hasVisibleItems && tagInput === document.activeElement ? 'block' : 'none';
    }

    function addTag(productId, productName) {
        if (selectedProducts.includes(productId)) return;

        selectedProducts.push(productId);
        updateTags();
        updateHiddenInput();
        tagInput.value = '';
        filterItems();
    }

    function removeTag(productId) {
        selectedProducts = selectedProducts.filter(id => id !== productId);
        updateTags();
        updateHiddenInput();
    }

    function updateTags() {
        selectedTags.innerHTML = '';
        selectedProducts.forEach(productId => {
            const item = Array.from(items).find(item => item.dataset.value === productId);
            if (item) {
                const tag = document.createElement('span');
                tag.className = 'vault-tag';
                tag.innerHTML = `
                    ${item.dataset.name}
                    <span class="vault-tag-remove" onclick="removeTag('${productId}')">&times;</span>
                `;
                selectedTags.appendChild(tag);
            }
        });
    }

    function updateHiddenInput() {
        hiddenInput.value = selectedProducts.filter(id => id && id.trim()).join(',');
    }

    function selectItem(item) {
        addTag(item.dataset.value, item.dataset.name);
        hideDropdown();
    }

    // Input event listeners
    tagInput.addEventListener('focus', showDropdown);
    tagInput.addEventListener('input', filterItems);

    tagInput.addEventListener('keydown', function(e) {
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            const visibleItems = Array.from(items).filter(item => item.style.display !== 'none');
            selectedIndex = Math.min(selectedIndex + 1, visibleItems.length - 1);
            updateSelection(visibleItems);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            selectedIndex = Math.max(selectedIndex - 1, 0);
            const visibleItems = Array.from(items).filter(item => item.style.display !== 'none');
            updateSelection(visibleItems);
        } else if (e.key === 'Enter') {
            e.preventDefault();
            const visibleItems = Array.from(items).filter(item => item.style.display !== 'none');
            if (selectedIndex >= 0 && visibleItems[selectedIndex]) {
                selectItem(visibleItems[selectedIndex]);
            }
        } else if (e.key === 'Escape') {
            hideDropdown();
        } else if (e.key === 'Backspace' && tagInput.value === '') {
            // Remove last tag on backspace
            if (selectedProducts.length > 0) {
                removeTag(selectedProducts[selectedProducts.length - 1]);
            }
        }
    });

    function updateSelection(visibleItems) {
        items.forEach((item, index) => {
            if (visibleItems.indexOf(item) === selectedIndex) {
                item.classList.add('selected');
                item.scrollIntoView({ block: 'nearest' });
            } else {
                item.classList.remove('selected');
            }
        });
    }

    // Item click handlers
    items.forEach(item => {
        item.addEventListener('click', function() {
            selectItem(this);
        });
        item.addEventListener('mouseenter', function() {
            const visibleItems = Array.from(items).filter(item => item.style.display !== 'none');
            selectedIndex = visibleItems.indexOf(this);
            updateSelection(visibleItems);
        });
    });

    // Hide dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!multiSelect.contains(e.target)) {
            hideDropdown();
        }
    });

    // Make removeTag global for onclick
    window.removeTag = removeTag;
}

// Submit Photo Upload Zone (Drag & Drop + Preview)
function initializeSubmitUploadZone() {
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('id_image');
    const uploadContent = document.querySelector('.vault-upload-content');
    const uploadPreview = document.getElementById('uploadPreview');
    const previewImage = document.getElementById('previewImage');
    const removePreview = document.getElementById('removePreview');

    if (!uploadZone || !fileInput) return;

    // Drag and drop functionality
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadZone.addEventListener(eventName, () => uploadZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadZone.addEventListener(eventName, () => uploadZone.classList.remove('dragover'), false);
    });

    uploadZone.addEventListener('drop', function(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            fileInput.files = files;
            previewFile(files[0]);
        }
    }, false);

    // Click to upload
    uploadZone.addEventListener('click', function(e) {
        // Don't trigger if clicking remove button
        if (e.target.id === 'removePreview' || e.target.closest('#removePreview')) {
            return;
        }
        
        // Don't trigger if preview is visible
        if (!uploadPreview.classList.contains('d-none')) {
            return;
        }
        
        fileInput.click();
    });

    // File input change
    fileInput.addEventListener('change', function() {
        if (this.files[0]) {
            previewFile(this.files[0]);
        }
    });

    // Preview functionality
    function previewFile(file) {
        if (!previewImage || !uploadPreview) {
            console.error('Preview elements not found!');
            return;
        }
        
        const reader = new FileReader();
        reader.onload = function(e) {
            previewImage.src = e.target.result;
            
            // Hide upload content, show preview
            if (uploadContent) uploadContent.classList.add('d-none');
            uploadPreview.classList.remove('d-none');
            
            // Force Safari to repaint/reflow
            uploadPreview.style.display = 'none';
            uploadPreview.offsetHeight; // Trigger reflow
            uploadPreview.style.display = '';
        };
        reader.onerror = function(e) {
            console.error('FileReader error:', e);
        };
        reader.readAsDataURL(file);
    }

    // Remove preview
    if (removePreview) {
        removePreview.addEventListener('click', function(e) {
            e.stopPropagation();
            fileInput.value = '';
            if (uploadContent) uploadContent.classList.remove('d-none');
            if (uploadPreview) uploadPreview.classList.add('d-none');
        });
    }
}

// Handle photo submission button click
window.handlePhotoSubmission = function() {
    const fileInput = document.getElementById('id_image');
    const consentCheckbox = document.getElementById('consent');
    const form = document.getElementById('submit-form');
    const submitBtn = document.getElementById('submit-btn');

    if (!fileInput.files[0]) {
        alert('Please select an image to upload.');
        return;
    }

    // Check file size (15MB)
    if (fileInput.files[0].size > 15 * 1024 * 1024) {
        alert('File size must be less than 15MB.');
        return;
    }

    // Check file type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg'];
    if (!allowedTypes.includes(fileInput.files[0].type)) {
        alert('Only JPG and PNG files are allowed.');
        return;
    }

    if (!consentCheckbox.checked) {
        alert('Please agree to the terms before submitting.');
        return;
    }

    // If all validations pass, submit the form
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Launching Your Photo...';
    form.submit();
};

// Submit Photo Form Validation
function initializeSubmitFormValidation() {
    const captionTextarea = document.getElementById('id_caption');
    const charCount = document.getElementById('char-count');
    const submitBtn = document.getElementById('submit-btn');
    const form = document.getElementById('submit-form');

    if (!captionTextarea || !charCount || !submitBtn || !form) return;

    // Character count
    captionTextarea.addEventListener('input', function() {
        const count = this.value.length;
        charCount.textContent = count;
        if (count > 720) {
            charCount.style.color = '#dc3545';
        } else {
            charCount.style.color = 'var(--gray)';
        }
    });

    // Form validation
    form.addEventListener('submit', function(e) {
        const fileInput = document.getElementById('id_image');
        const consentCheckbox = document.getElementById('consent');

        if (!fileInput.files[0]) {
            e.preventDefault();
            alert('Please select an image to upload.');
            return;
        }

        // Check file size (5MB)
        if (fileInput.files[0].size > 5 * 1024 * 1024) {
            e.preventDefault();
            alert('File size must be less than 5MB.');
            return;
        }

        // Check file type
        const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg'];
        if (!allowedTypes.includes(fileInput.files[0].type)) {
            e.preventDefault();
            alert('Only JPG and PNG files are allowed.');
            return;
        }

        if (!consentCheckbox.checked) {
            e.preventDefault();
            alert('Please agree to the terms before submitting.');
            return;
        }

        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';
    });
}

// Utility function for CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Photo Detail Keyboard Navigation
function initializePhotoDetailKeyboardNav() {
    document.addEventListener('keydown', function(e) {
        // Only handle keyboard navigation if we're not in an input field
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
            return;
        }

        // Find previous and next buttons in the photo navigation section
        const photoNav = document.querySelector('.vault-photo-navigation');
        let prevButton = null;
        let nextButton = null;

        if (photoNav) {
            const navButtons = photoNav.querySelectorAll('a.btn');
            navButtons.forEach(button => {
                if (button.querySelector('.fa-chevron-left')) {
                    prevButton = button;
                } else if (button.querySelector('.fa-chevron-right')) {
                    nextButton = button;
                }
            });
        }

        if (e.key === 'ArrowLeft' && prevButton) {
            e.preventDefault();
            prevButton.click();
        } else if (e.key === 'ArrowRight' && nextButton) {
            e.preventDefault();
            nextButton.click();
        }
    });
}

// Moderation Bulk Selection
function initializeModerationBulkSelection() {
    const selectAllCheckbox = document.getElementById('select-all');
    const photoCheckboxes = document.querySelectorAll('.photo-checkbox');
    const selectedPhotosInput = document.getElementById('selected-photos');
    const bulkForm = document.querySelector('form[action*="moderate"]');

    // Only initialize if required elements exist
    if (!selectAllCheckbox || !selectedPhotosInput) return;

    function updateSelectedPhotos() {
        const selectedIds = Array.from(photoCheckboxes)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);
        selectedPhotosInput.value = selectedIds.join(',');
    }

    function updateSelectAllState() {
        const checkedBoxes = document.querySelectorAll('.photo-checkbox:checked');
        const totalBoxes = photoCheckboxes.length;
        selectAllCheckbox.checked = checkedBoxes.length === totalBoxes;
        selectAllCheckbox.indeterminate = checkedBoxes.length > 0 && checkedBoxes.length < totalBoxes;
    }

    // Handle select all checkbox
    selectAllCheckbox.addEventListener('change', function() {
        photoCheckboxes.forEach(checkbox => {
            checkbox.checked = this.checked;
        });
        updateSelectedPhotos();
    });

    // Handle individual checkboxes
    photoCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateSelectAllState();
            updateSelectedPhotos();
        });
    });

    // Update hidden input before form submission
    if (bulkForm) {
        bulkForm.addEventListener('submit', function() {
            updateSelectedPhotos();
        });
    }
}

// Moderation Caption Toggle
function initializeModerationCaptionToggle() {
    const toggleButtons = document.querySelectorAll('.caption-toggle');

    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const container = this.parentElement;
            const caption = container.querySelector('.moderation-caption');
            const isExpanded = this.getAttribute('aria-expanded') === 'true';

            if (isExpanded) {
                // Collapse
                caption.classList.remove('expanded');
                this.setAttribute('aria-expanded', 'false');
                this.setAttribute('aria-label', 'Expand caption');
            } else {
                // Expand
                caption.classList.add('expanded');
                this.setAttribute('aria-expanded', 'true');
                this.setAttribute('aria-label', 'Collapse caption');
            }
        });
    });
}

// Moderation Page Auto-Submit Filter
function initializeModerationAutoSubmit() {
    const statusFilter = document.getElementById('status-filter');
    const filterForm = document.getElementById('status-filter-form');
    const searchInput = document.getElementById('search-input');
    
    
    if (!statusFilter || !filterForm) {
        
        return;
    }
    
    // Auto-submit when status changes
    statusFilter.addEventListener('change', function() {
        
        filterForm.submit();
    });
    
    // Auto-submit when search changes (debounced)
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(() => {
                
                filterForm.submit();
            }, 500);
        });
    }
}

// Initialize vault functionality based on current page
document.addEventListener('DOMContentLoaded', function() {
    // Initialize voting and likes globally
    initializeVoting();
    initializeGalleryLikes();
    initializePhotoDetailLikes();

    // Gallery page - filter functionality removed
    // if (document.getElementById('product_filter')) {
    //     initializeGalleryFilter();
    //     initializeProductChips();
    // }

    // Photo detail page
    if (document.querySelector('.vault-detail-layout')) {
        initializePhotoDetailShare();
        initializePhotoDetailKeyboardNav();
    }

    // Submit photo page
    if (document.getElementById('product_tags')) {
        initializeSubmitMultiSelect();
        initializeSubmitFormValidation();
    }

    // Submit photo upload zone
    if (document.getElementById('uploadZone')) {
        initializeSubmitUploadZone();
    }

    // Moderation page
    if (document.getElementById('status-filter')) {
        initializeModerationAutoSubmit();
    }
    if (document.querySelector('.moderation-card') || document.getElementById('select-all')) {
        initializeModerationBulkSelection();
        initializeModerationCaptionToggle();
    }

    // Featured photos carousel
    if (document.getElementById('featured-track')) {
        // Add a longer delay to ensure CSS is fully loaded
        setTimeout(() => {
            initializeFeaturedCarousel();
        }, 500);
    }
});

// Featured Photos Carousel - Transform-based like Collections Carousel
function initializeFeaturedCarousel() {
    
    const track = document.getElementById('featured-track');
    const prevBtn = document.getElementById('featured-prev');
    const nextBtn = document.getElementById('featured-next');

    // Only initialize if required elements exist
    if (!track || !prevBtn || !nextBtn) {
        return;
    }

    const featuredItems = track.children;
    const totalItems = featuredItems.length;

    let currentIndex = 0;
    let isVerticalLayout = false;
    let touchStartX = 0;
    let touchStartY = 0;
    let touchEndX = 0;
    let touchEndY = 0;

    // Determine if we're in vertical (desktop sidebar) or horizontal (mobile) layout
    function checkLayout() {
        const trackComputedStyle = window.getComputedStyle(track);
        const flexDirection = trackComputedStyle.flexDirection;
        isVerticalLayout = flexDirection === 'column';
    }

    // Calculate item size dynamically based on layout
    function getItemSize() {
        if (featuredItems.length === 0) return isVerticalLayout ? 400 : 374;
        
        if (isVerticalLayout) {
            // Vertical layout: use height + gap
            return featuredItems[0].offsetHeight + 24; // height + gap (1.5rem = 24px)
        } else {
            // Horizontal layout: use width + gap
            return featuredItems[0].offsetWidth + 24; // width + gap (1.5rem = 24px)
        }
    }

    function updateFeaturedCarousel() {
        checkLayout();
        
        const itemSize = getItemSize();
        let visibleItems;
        
        if (isVerticalLayout) {
            // Vertical layout (desktop): show 2 items
            visibleItems = Math.min(2, totalItems);
        } else {
            // Horizontal layout (mobile): calculate based on container width
            const container = track.closest('.vault-featured-carousel-container');
            if (container) {
                const containerWidth = container.offsetWidth - 100; // Subtract padding (50px each side)
                visibleItems = Math.max(1, Math.floor(containerWidth / itemSize));
            } else {
                visibleItems = Math.min(2, totalItems); // Fallback
            }
        }
        
        const maxIndex = Math.max(0, totalItems - visibleItems);
        
        // Clamp current index if needed
        if (currentIndex > maxIndex) {
            currentIndex = maxIndex;
        }
        
        if (isVerticalLayout) {
            // Vertical scrolling (desktop sidebar)
            const translateY = -currentIndex * itemSize;
            track.style.transform = `translateY(${translateY}px)`;
        } else {
            // Horizontal scrolling (mobile)
            const translateX = -currentIndex * itemSize;
            track.style.transform = `translateX(${translateX}px)`;
        }

        // Update button states - always enabled for looping
        prevBtn.style.opacity = '1';
        prevBtn.disabled = false;
        nextBtn.style.opacity = '1';
        nextBtn.disabled = false;
    }

    function nextFeaturedSlide() {
        checkLayout();
        const itemSize = getItemSize();
        let visibleItems;
        
        if (isVerticalLayout) {
            visibleItems = Math.min(2, totalItems);
        } else {
            const container = track.closest('.vault-featured-carousel-container');
            if (container) {
                const containerWidth = container.offsetWidth - 100;
                visibleItems = Math.max(1, Math.floor(containerWidth / itemSize));
            } else {
                visibleItems = Math.min(2, totalItems);
            }
        }
        
        const maxIndex = Math.max(0, totalItems - visibleItems);
        
        currentIndex++;
        if (currentIndex > maxIndex) {
            currentIndex = 0; // Loop back to start
        }
        updateFeaturedCarousel();
    }

    function prevFeaturedSlide() {
        checkLayout();
        const itemSize = getItemSize();
        let visibleItems;
        
        if (isVerticalLayout) {
            visibleItems = Math.min(2, totalItems);
        } else {
            const container = track.closest('.vault-featured-carousel-container');
            if (container) {
                const containerWidth = container.offsetWidth - 100;
                visibleItems = Math.max(1, Math.floor(containerWidth / itemSize));
            } else {
                visibleItems = Math.min(2, totalItems);
            }
        }
        
        const maxIndex = Math.max(0, totalItems - visibleItems);
        
        currentIndex--;
        if (currentIndex < 0) {
            currentIndex = maxIndex; // Loop to end
        }
        updateFeaturedCarousel();
    }

    // Touch event handlers for mobile swipe
    function handleTouchStart(e) {
        touchStartX = e.changedTouches[0].screenX;
        touchStartY = e.changedTouches[0].screenY;
    }

    function handleTouchEnd(e) {
        touchEndX = e.changedTouches[0].screenX;
        touchEndY = e.changedTouches[0].screenY;
        handleSwipeGesture();
    }

    function handleSwipeGesture() {
        checkLayout();
        const diffX = touchStartX - touchEndX;
        const diffY = touchStartY - touchEndY;
        const minSwipeDistance = 30; // Reduced from 50 to 30 for better sensitivity

        if (isVerticalLayout) {
            // Vertical layout - respond to vertical swipes
            if (Math.abs(diffY) > minSwipeDistance && Math.abs(diffY) > Math.abs(diffX)) {
                if (diffY > 0) {
                    // Swipe up - next
                    nextFeaturedSlide();
                } else {
                    // Swipe down - previous
                    prevFeaturedSlide();
                }
            }
        } else {
            // Horizontal layout - respond to horizontal swipes
            if (Math.abs(diffX) > minSwipeDistance && Math.abs(diffX) > Math.abs(diffY)) {
                if (diffX > 0) {
                    // Swipe left - next
                    nextFeaturedSlide();
                } else {
                    // Swipe right - previous
                    prevFeaturedSlide();
                }
            }
        }
    }

    // Add touch event listeners to featured section (parent container)
    const featuredSection = track.closest('.vault-featured-section');
    
    if (featuredSection) {
        featuredSection.addEventListener('touchstart', handleTouchStart, { passive: true });
        featuredSection.addEventListener('touchend', handleTouchEnd, { passive: true });
    } else {
        
        const carouselContainer = track.closest('.vault-featured-carousel');
        if (carouselContainer) {
            carouselContainer.addEventListener('touchstart', handleTouchStart, { passive: true });
            carouselContainer.addEventListener('touchend', handleTouchEnd, { passive: true });
        } else {
            
            track.addEventListener('touchstart', handleTouchStart, { passive: true });
            track.addEventListener('touchend', handleTouchEnd, { passive: true });
        }
    }

    // Event listeners for click
    
    
    if (prevBtn && nextBtn) {
        
        
        const handlePrevClick = (e) => {
            pauseAutoPlay();
            e.preventDefault();
            e.stopPropagation();
            prevFeaturedSlide();
            resumeAutoPlay();
        };
        
        const handleNextClick = (e) => {
            pauseAutoPlay();
            e.preventDefault();
            e.stopPropagation();
            nextFeaturedSlide();
            resumeAutoPlay();
        };
        
        prevBtn.addEventListener('click', handlePrevClick);
        nextBtn.addEventListener('click', handleNextClick);
        
        
        
        // Test immediate click
        
    } else {
        console.error('Buttons not found for event listeners');
    }

    // Auto-play functionality for mobile
    let autoPlayInterval = null;
    const autoPlayDelay = 4000; // 4 seconds
    let isUserInteracting = false;

    function startAutoPlay() {
        if (autoPlayInterval) {
            clearInterval(autoPlayInterval);
        }
        
        autoPlayInterval = setInterval(() => {
            if (!isUserInteracting && !isVerticalLayout) {
                nextFeaturedSlide();
            }
        }, autoPlayDelay);
    }

    function stopAutoPlay() {
        if (autoPlayInterval) {
            clearInterval(autoPlayInterval);
            autoPlayInterval = null;
        }
    }

    function pauseAutoPlay() {
        isUserInteracting = true;
        stopAutoPlay();
    }

    function resumeAutoPlay() {
        isUserInteracting = false;
        // Resume auto-play after 8 seconds of inactivity
        setTimeout(() => {
            if (!isUserInteracting && !isVerticalLayout) {
                startAutoPlay();
            }
        }, 8000);
    }

    // Start auto-play initially (will only work on mobile due to layout check)
    startAutoPlay();

    // Pause auto-play on touch interactions
    function handleTouchStart(e) {
        pauseAutoPlay();
        touchStartX = e.changedTouches[0].screenX;
        touchStartY = e.changedTouches[0].screenY;
    }

    function handleTouchEnd(e) {
        touchEndX = e.changedTouches[0].screenX;
        touchEndY = e.changedTouches[0].screenY;
        handleSwipeGesture();
        resumeAutoPlay();
    }

    // Handle window resize
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            currentIndex = 0; // Reset to start on resize
            updateFeaturedCarousel();
            // Restart auto-play after resize
            stopAutoPlay();
            startAutoPlay();
        }, 250);
    });
}

// Moderation Confirmation Modal Functions
let currentFormToSubmit = null;

function showVaultConfirmModal(title, message, iconClass, confirmText, confirmClass, form, isRejectAction = false) {
    // Update modal content
    document.getElementById('modal-title-text').textContent = title;
    document.getElementById('modal-message').textContent = message;
    document.getElementById('modal-main-icon').className = `fas ${iconClass} vault-modal-main-icon`;
    document.getElementById('modal-confirm-text').textContent = confirmText;
    
    // Update confirm button styling
    const confirmBtn = document.getElementById('modal-confirm-btn');
    confirmBtn.className = `btn vault-modal-btn-confirm ${confirmClass}`;
    
    // Handle rejection reason textarea
    const rejectionContainer = document.getElementById('rejection-reason-container');
    const rejectionTextarea = document.getElementById('rejection-reason');
    
    if (isRejectAction) {
        rejectionContainer.classList.remove('d-none');
        rejectionTextarea.value = ''; // Clear previous value
        updateRejectionCharCount();
        
        // Focus on textarea after modal is shown
        setTimeout(() => {
            rejectionTextarea.focus();
        }, 500);
    } else {
        rejectionContainer.classList.add('d-none');
        rejectionTextarea.value = '';
    }
    
    // Store the form to submit
    currentFormToSubmit = form;
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('vaultConfirmModal'));
    modal.show();
}

// Character count for rejection reason
function updateRejectionCharCount() {
    const textarea = document.getElementById('rejection-reason');
    const counter = document.getElementById('rejection-char-count');
    if (!textarea || !counter) return;
    
    const count = textarea.value.length;
    counter.textContent = count;
    
    // Change color based on character count
    if (count > 450) {
        counter.style.color = '#dc3545';
    } else if (count > 400) {
        counter.style.color = '#ffc107';
    } else {
        counter.style.color = '#6c757d';
    }
}

// Handle modal confirm button click
document.addEventListener('DOMContentLoaded', function() {
    const confirmBtn = document.getElementById('modal-confirm-btn');
    if (confirmBtn) {
        confirmBtn.addEventListener('click', function() {
            if (currentFormToSubmit) {
                // If rejection action, add rejection reason to form
                const rejectionTextarea = document.getElementById('rejection-reason');
                const rejectionContainer = document.getElementById('rejection-reason-container');
                if (rejectionTextarea && !rejectionContainer.classList.contains('d-none')) {
                    const reasonInput = currentFormToSubmit.querySelector('input[name="rejection_reason"]');
                    if (reasonInput) {
                        reasonInput.value = rejectionTextarea.value;
                    }
                }
                // Submit the form
                currentFormToSubmit.submit();
            }
        });
    }

    // Character count update for rejection reason
    const rejectionTextarea = document.getElementById('rejection-reason');
    if (rejectionTextarea) {
        rejectionTextarea.addEventListener('input', updateRejectionCharCount);
    }
});

// Vault-specific confirmation function - exposed globally for onclick handlers
window.confirmVaultAction = function(action, photoId, title, message, iconClass, confirmText, confirmClass, isRejectAction = false) {
    // Find the form for this action - try to find the input first
    const photoInput = document.querySelector(`form input[name="photo_id"][value="${photoId}"]`);
    
    if (!photoInput) {
        console.error('Could not find photo input for photoId:', photoId);
        return false;
    }
    
    const form = photoInput.closest('form');
    
    if (!form) {
        console.error('Could not find form for photoId:', photoId);
        return false;
    }
    
    const actionInput = form.querySelector('input[name="action"]');
    if (actionInput) {
        actionInput.value = action;
    } else {
        console.error('Could not find action input in form');
    }
    
    showVaultConfirmModal(title, message, iconClass, confirmText, confirmClass, form, isRejectAction);
        return false; // Prevent default form submission
    };

// Event delegation for vault moderate buttons with data attributes
document.addEventListener('click', function(e) {
    const vaultBtn = e.target.closest('[data-vault-action]');
    if (vaultBtn) {
        e.preventDefault();
        const action = vaultBtn.dataset.vaultAction;
        const photoId = vaultBtn.dataset.photoId;
        const title = vaultBtn.dataset.title;
        const message = vaultBtn.dataset.message;
        const iconClass = vaultBtn.dataset.icon;
        const confirmText = vaultBtn.dataset.confirmText;
        const confirmClass = vaultBtn.dataset.confirmClass;
        const isRejectAction = vaultBtn.dataset.isReject === 'true';
        
        window.confirmVaultAction(action, photoId, title, message, iconClass, confirmText, confirmClass, isRejectAction);
    }
});

    /*
     * Duplicate DOMContentLoaded block removed.
     * Initialization is handled earlier in this file (single entrypoint retained).
     */