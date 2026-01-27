// HENDOSHI Vault JavaScript
// Contains all vault-specific functionality

// Gallery Filter Dropdown
function initializeGalleryFilter() {
    const input = document.getElementById('product_filter');
    const hiddenInput = document.getElementById('product_value');
    const dropdown = document.getElementById('product-dropdown');
    const items = dropdown.querySelectorAll('.vault-dropdown-item');
    let selectedIndex = -1;

    // Initialize with current filter if any
    const productFilter = '{{ product_filter }}';
    if (productFilter) {
        const currentItem = Array.from(items).find(item => item.dataset.value === productFilter);
        if (currentItem) {
            input.value = currentItem.textContent;
            hiddenInput.value = productFilter;
        }
    }

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
        const query = input.value.toLowerCase();
        let hasVisibleItems = false;

        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            if (text.includes(query)) {
                item.style.display = 'block';
                hasVisibleItems = true;
            } else {
                item.style.display = 'none';
            }
        });

        dropdown.style.display = hasVisibleItems && input === document.activeElement ? 'block' : 'none';
    }

    function selectItem(item) {
        input.value = item.textContent;
        hiddenInput.value = item.dataset.value;
        hideDropdown();
    }

    // Input event listeners
    input.addEventListener('focus', showDropdown);
    input.addEventListener('input', filterItems);

    input.addEventListener('keydown', function(e) {
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            selectedIndex = Math.min(selectedIndex + 1, items.length - 1);
            updateSelection();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            selectedIndex = Math.max(selectedIndex - 1, 0);
            updateSelection();
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (selectedIndex >= 0 && items[selectedIndex].style.display !== 'none') {
                selectItem(items[selectedIndex]);
            }
        } else if (e.key === 'Escape') {
            hideDropdown();
        }
    });

    function updateSelection() {
        items.forEach((item, index) => {
            if (index === selectedIndex && item.style.display !== 'none') {
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
            selectedIndex = Array.from(items).indexOf(this);
            updateSelection();
        });
    });

    // Hide dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!input.contains(e.target) && !dropdown.contains(e.target)) {
            hideDropdown();
        }
    });
}

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
        // Update likes count in gallery view (if exists)
        const galleryLikesElement = document.getElementById(`likes-${photoId}`);
        if (galleryLikesElement) {
            galleryLikesElement.innerHTML = `<i class="fas fa-heart"></i> ${data.likes}`;
        }

        // Update detail view like button (if exists)
        const detailButton = document.getElementById(`like-button-${photoId}`);
        if (detailButton) {
            detailButton.innerHTML = `<i class="fas fa-heart"></i> Like (${data.likes})`;
            if (data.liked) {
                detailButton.classList.add('btn-pink');
                detailButton.classList.remove('btn-outline-pink');
            } else {
                detailButton.classList.add('btn-outline-pink');
                detailButton.classList.remove('btn-pink');
            }
        }

        // Update gallery like button styling (if exists)
        const galleryButton = document.querySelector(`button[onclick*="${photoId}"]`);
        if (galleryButton && galleryButton.classList.contains('vault-like-btn')) {
            if (data.liked) {
                galleryButton.classList.add('btn-pink');
                galleryButton.classList.remove('btn-outline-pink');
            } else {
                galleryButton.classList.add('btn-outline-pink');
                galleryButton.classList.remove('btn-pink');
            }
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

            // Update gallery buttons (found by onclick attribute) - only update classes, not innerHTML since they don't show counts
            const allButtons = document.querySelectorAll(`button[onclick*="${photoId}"]`);
            allButtons.forEach(button => {
                const onclickAttr = button.getAttribute('onclick');
                if (onclickAttr.includes(`votePhoto(${photoId}, 'up')`)) {
                    // This is an upvote button
                    if (data.user_vote === 'up') {
                        button.classList.add('btn-success');
                        button.classList.remove('btn-outline-success');
                    } else {
                        button.classList.add('btn-outline-success');
                        button.classList.remove('btn-success');
                    }
                } else if (onclickAttr.includes(`votePhoto(${photoId}, 'down')`)) {
                    // This is a downvote button
                    if (data.user_vote === 'down') {
                        button.classList.add('btn-danger');
                        button.classList.remove('btn-outline-danger');
                    } else {
                        button.classList.add('btn-outline-danger');
                        button.classList.remove('btn-danger');
                    }
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

// Share Photo Functionality
function initializePhotoDetailShare() {
    window.sharePhoto = function() {
        const modal = new bootstrap.Modal(document.getElementById('shareModal'));
        modal.show();

        // Select the share URL
        const shareUrlInput = document.getElementById('shareUrl');
        shareUrlInput.select();
        shareUrlInput.setSelectionRange(0, 99999);
    };
    // Copy share link functionality
    window.copyShareLink = function() {
        const shareUrlInput = document.getElementById('shareUrl');
        const url = shareUrlInput.value;

        // Try modern clipboard API first
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(url).then(function() {
                showCopyFeedback('Link copied to clipboard!');
            }).catch(function(err) {
                console.error('Failed to copy: ', err);
                fallbackCopyTextToClipboard(url);
            });
        } else {
            // Fallback for older browsers
            fallbackCopyTextToClipboard(url);
        }
    };;

    function fallbackCopyTextToClipboard(text) {
        const textArea = document.createElement("textarea");
        textArea.value = text;
        textArea.style.position = "fixed";
        textArea.style.left = "-999999px";
        textArea.style.top = "-999999px";
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();

        try {
            const successful = document.execCommand('copy');
            if (successful) {
                showCopyFeedback('Link copied to clipboard!');
            } else {
                showCopyFeedback('Failed to copy link', true);
            }
        } catch (err) {
            showCopyFeedback('Failed to copy link', true);
        }

        document.body.removeChild(textArea);
    }

    function showCopyFeedback(message, isError = false) {
        // Remove any existing feedback
        const existingFeedback = document.querySelector('.copy-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }

        // Create feedback element
        const feedback = document.createElement('div');
        feedback.className = `copy-feedback alert alert-${isError ? 'danger' : 'success'} alert-dismissible fade show`;
        feedback.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; min-width: 250px;';
        feedback.innerHTML = `
            <i class="fas fa-${isError ? 'exclamation-triangle' : 'check-circle'}"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(feedback);

        // Auto remove after 3 seconds
        setTimeout(() => {
            if (feedback.parentNode) {
                feedback.remove();
            }
        }, 3000);
    }}

// Submit Photo Multi-Select
function initializeSubmitMultiSelect() {
    const multiSelect = document.getElementById('product_tags');
    const tagInput = document.getElementById('tag_input');
    const selectedTags = document.getElementById('selected_tags');
    const dropdown = document.getElementById('product_dropdown');
    const hiddenInput = document.getElementById('product_ids');
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

// Initialize vault functionality based on current page
document.addEventListener('DOMContentLoaded', function() {
    // Gallery page
    if (document.getElementById('product_filter')) {
        initializeGalleryFilter();
        initializeGalleryLikes();
    }

    // Photo detail page
    if (document.getElementById('shareModal')) {
        initializePhotoDetailLikes();
        initializePhotoDetailShare();
        initializePhotoDetailKeyboardNav();
    }

    // Submit photo page
    if (document.getElementById('product_tags')) {
        initializeSubmitMultiSelect();
        initializeSubmitFormValidation();
    }

    // Moderation page
    if (document.getElementById('select-all')) {
        initializeModerationBulkSelection();
    }

    // Featured photos carousel
    if (document.getElementById('featured-track')) {
        initializeFeaturedCarousel();
    }
});

// Featured Photos Carousel
function initializeFeaturedCarousel() {
    const track = document.getElementById('featured-track');
    const prevBtn = document.getElementById('featured-prev');
    const nextBtn = document.getElementById('featured-next');
    const items = track.children;
    let currentIndex = 0;
    const totalItems = items.length;
    let itemWidth = 0;
    let visibleItems = 1;
    let maxIndex = 0;

    function calculateDimensions() {
        if (!items.length) return;

        // Measure the real item width and gap
        const firstItem = items[0];
        const itemRect = firstItem.getBoundingClientRect();
        const computed = getComputedStyle(track);
        const gap = parseFloat(computed.gap) || 16; // fallback
        const paddingLeft = parseFloat(computed.paddingLeft) || 0;
        const paddingRight = parseFloat(computed.paddingRight) || 0;

        itemWidth = Math.round(itemRect.width + gap);

        const availableWidth = track.parentElement.offsetWidth - paddingLeft - paddingRight;
        visibleItems = Math.max(1, Math.floor(availableWidth / itemWidth) || 1);
        maxIndex = Math.max(0, totalItems - visibleItems);

        // Clamp currentIndex to new max
        if (currentIndex > maxIndex) currentIndex = maxIndex;
    }

    function updateCarousel() {
        const translateX = -currentIndex * itemWidth;
        track.style.transform = `translateX(${translateX}px)`;

        // Update button states
        prevBtn.style.opacity = currentIndex === 0 ? '0.5' : '1';
        prevBtn.disabled = currentIndex === 0;
        nextBtn.style.opacity = currentIndex >= maxIndex ? '0.5' : '1';
        nextBtn.disabled = currentIndex >= maxIndex;
    }

    function nextSlide() {
        if (currentIndex < maxIndex) {
            currentIndex++;
            updateCarousel();
        }
    }

    function prevSlide() {
        if (currentIndex > 0) {
            currentIndex--;
            updateCarousel();
        }
    }

    // Event listeners
    nextBtn.addEventListener('click', nextSlide);
    prevBtn.addEventListener('click', prevSlide);

    // Touch/swipe support for mobile
    let startX = 0;
    let isDragging = false;

    track.addEventListener('touchstart', (e) => {
        startX = e.touches[0].clientX;
        isDragging = true;
    });

    track.addEventListener('touchmove', (e) => {
        if (!isDragging) return;
        const currentX = e.touches[0].clientX;
        const diff = startX - currentX;

        if (Math.abs(diff) > 50) {
            if (diff > 0 && currentIndex < maxIndex) {
                nextSlide();
            } else if (diff < 0 && currentIndex > 0) {
                prevSlide();
            }
            isDragging = false;
        }
    });

    track.addEventListener('touchend', () => {
        isDragging = false;
    });

    // Recalculate on window resize to handle responsive item sizes
    window.addEventListener('resize', () => {
        calculateDimensions();
        updateCarousel();
    });

    // Auto-play functionality (optional)
    let autoplayInterval = null;
    function startAutoplay() {
        if (autoplayInterval) clearInterval(autoplayInterval);
        autoplayInterval = setInterval(() => {
            if (currentIndex >= maxIndex) {
                currentIndex = 0;
            } else {
                currentIndex++;
            }
            updateCarousel();
        }, 5000); // Change slide every 5 seconds
    }

    // Pause autoplay on hover
    track.parentElement.addEventListener('mouseenter', () => {
        if (autoplayInterval) clearInterval(autoplayInterval);
    });

    track.parentElement.addEventListener('mouseleave', () => {
        startAutoplay();
    });

    // Initialize dimensions and carousel
    calculateDimensions();
    updateCarousel();
    startAutoplay();

    // Handle window resize
    window.addEventListener('resize', () => {
        const newVisibleItems = Math.floor(track.parentElement.offsetWidth / itemWidth) || 1;
        const newMaxIndex = Math.max(0, totalItems - newVisibleItems);

        if (currentIndex > newMaxIndex) {
            currentIndex = newMaxIndex;
        }

        updateCarousel();
    });
}

// Initialize all vault functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeGalleryFilter();
    initializeGalleryLikes();
    initializePhotoDetailLikes();
    initializeVoting();
    initializePhotoDetailShare();
    initializeCarousel();
});