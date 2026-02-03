/**
 * Product Detail Main Functionality
 * Handles variant selection, cart operations, image gallery, and battle vest for main product
 */

document.addEventListener('DOMContentLoaded', function() {
    // Size and Color Button Selection
    const sizeButtons = document.querySelectorAll('.size-btn');
    const sizeInput = document.getElementById('size-input');
    const colorButtons = document.querySelectorAll('.color-btn');
    const colorInput = document.getElementById('color-input');

    const stickySizeSelect = document.getElementById('stickySizeSelect');
    const stickyColorSelect = document.getElementById('stickyColorSelect');

    function syncStickyFromInputs() {
        if (stickySizeSelect && sizeInput) {
            stickySizeSelect.value = sizeInput.value || '';
        }
        if (stickyColorSelect && colorInput) {
            stickyColorSelect.value = colorInput.value || '';
        }
    }

    sizeButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove selected class from all size buttons
            sizeButtons.forEach(btn => btn.classList.remove('selected'));
            // Add selected class to clicked button
            this.classList.add('selected');
            // Update hidden input
            sizeInput.value = this.dataset.value;
            syncStickyFromInputs();
        });
    });

    colorButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove selected class from all color buttons
            colorButtons.forEach(btn => btn.classList.remove('selected'));
            // Add selected class to clicked button
            this.classList.add('selected');
            // Update hidden input
            colorInput.value = this.dataset.value;
            syncStickyFromInputs();
        });
    });

    if (stickySizeSelect) {
        stickySizeSelect.addEventListener('change', function() {
            const match = Array.from(sizeButtons).find(btn => btn.dataset.value === this.value);
            if (match) {
                match.click();
            } else if (sizeInput) {
                sizeInput.value = '';
            }
        });
    }

    if (stickyColorSelect) {
        stickyColorSelect.addEventListener('change', function() {
            const match = Array.from(colorButtons).find(btn => btn.dataset.value === this.value);
            if (match) {
                match.click();
            } else if (colorInput) {
                colorInput.value = '';
            }
        });
    }

    syncStickyFromInputs();

    // Quantity increment/decrement
    function incrementQuantity() {
        const input = document.getElementById('quantity');
        input.value = parseInt(input.value) + 1;
        syncStickyFromInputs();
    }

    function decrementQuantity() {
        const input = document.getElementById('quantity');
        const min = parseInt(input.min);
        if (parseInt(input.value) > min) {
            input.value = parseInt(input.value) - 1;
        }
        syncStickyFromInputs();
    }

    // Add event listener for manual quantity input changes
    const quantityInput = document.getElementById('quantity');
    if (quantityInput) {
        quantityInput.addEventListener('input', function() {
            // Validate input is a positive integer
            const value = parseInt(this.value);
            if (isNaN(value) || value < 1) {
                this.value = 1;
            } else {
                this.value = value;
            }
            syncStickyFromInputs();
        });

        quantityInput.addEventListener('blur', function() {
            // Ensure minimum value on blur
            const value = parseInt(this.value);
            const min = parseInt(this.min) || 1;
            if (value < min) {
                this.value = min;
            }
            syncStickyFromInputs();
        });
    }

    // Make functions globally available
    window.incrementQuantity = incrementQuantity;
    window.decrementQuantity = decrementQuantity;

    // Add event listeners for quantity buttons
    const qtyMinusBtn = document.querySelector('.qty-minus');
    const qtyPlusBtn = document.querySelector('.qty-plus');
    const loginToAddBtn = document.querySelector('.login-to-add-btn');

    if (qtyMinusBtn) {
        qtyMinusBtn.addEventListener('click', decrementQuantity);
    }

    if (qtyPlusBtn) {
        qtyPlusBtn.addEventListener('click', incrementQuantity);
    }

    if (loginToAddBtn) {
        loginToAddBtn.addEventListener('click', function() {
            window.location.href = '/accounts/login/?next=' + encodeURIComponent(window.location.pathname);
        });
    }

    // Custom form validation with toast messages
    const form = document.getElementById('addToCartForm');

    form.addEventListener('submit', function(e) {
        e.preventDefault(); // Prevent default form submission

        // Check if size is selected
        const sizeInput = document.getElementById('size-input');
        if (sizeInput && sizeInput.value === '') {
            showValidationToast('Please select a size before adding to cart.');
            return false;
        }

        // Check if color is selected
        const colorInput = document.getElementById('color-input');
        if (colorInput && colorInput.value === '') {
            showValidationToast('Please select a color before adding to cart.');
            return false;
        }

        // Submit via AJAX
        submitAddToCartForm();
        return false;
    });

    // AJAX form submission
    function submitAddToCartForm() {
        const form = document.getElementById('addToCartForm');

        // Get values from hidden inputs
        const sizeInput = document.getElementById('size-input');
        const colorInput = document.getElementById('color-input');
        const quantityInput = document.getElementById('quantity');

        const size = sizeInput ? sizeInput.value : '';
        const color = colorInput ? colorInput.value : '';
        const quantity = quantityInput.value;
        const productId = form.dataset.productId || form.querySelector('input[name="product_id"]')?.value;

        // Show loading state
        const submitBtn = form.querySelector('.add-to-cart-btn');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';
        submitBtn.disabled = true;

        // Get CSRF token from the form
        const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch(`/cart/add/${productId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `csrfmiddlewaretoken=${encodeURIComponent(csrfToken)}&size=${encodeURIComponent(size)}&color=${encodeURIComponent(color)}&quantity=${encodeURIComponent(quantity)}`
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Update cart count
                updateCartCount(data.cart_count);

                // Show cart drawer with item details
                showCartDrawer(data);

                // Success toast removed to avoid overlap with cart drawer
            } else {
                // Show error
                if (typeof showToast === 'function') {
                    showToast(data.message, 'error');
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            if (typeof showToast === 'function') {
                showToast('Failed to add item to cart. Please try again.', 'error');
            }
        })
        .finally(() => {
            // Reset button
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        });
    }

    // Sticky add-to-cart bar behavior
    const stickyBar = document.getElementById('stickyAddToCart');
    const stickyAddBtn = document.getElementById('stickyAddBtn');
    const trigger = document.getElementById('mainImageContainer');
    if (!stickyBar || !trigger) return;

    let lastScrollY = window.scrollY;
    let isPastTrigger = false;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            isPastTrigger = !entry.isIntersecting;
        });
    }, { rootMargin: '-80px 0px 0px 0px', threshold: 0.1 });

    observer.observe(trigger);

    function hideSticky() {
        stickyBar.classList.remove('is-visible');
        stickyBar.setAttribute('aria-hidden', 'true');
    }

    function showSticky() {
        stickyBar.classList.add('is-visible');
        stickyBar.setAttribute('aria-hidden', 'false');
    }

    window.addEventListener('scroll', () => {
        const currentY = window.scrollY;
        const scrollingDown = currentY > lastScrollY;
        lastScrollY = currentY;

        if (!isPastTrigger || currentY < 200 || !scrollingDown) {
            hideSticky();
            return;
        }

        showSticky();
    }, { passive: true });

    if (stickyAddBtn) {
        stickyAddBtn.addEventListener('click', function() {
            submitAddToCartForm();
        });
    }

    // Use global showToast for validation messages
    function showValidationToast(message) {
        if (typeof showToast === 'function') {
            showToast(message, 'warning');
        }
    }

    // Add pink border to dropdowns when selection is made
    const dropdowns = document.querySelectorAll('.product-dropdown');
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('change', function() {
            if (this.value !== '') {
                this.classList.add('has-selection');
            } else {
                this.classList.remove('has-selection');
            }
        });

        // Check initial state
        if (dropdown.value !== '') {
            dropdown.classList.add('has-selection');
        }
    });
});

// Battle Vest functionality for main product
document.addEventListener('DOMContentLoaded', function() {
    const battleVestBtn = document.getElementById('battleVestBtn');

    // Only initialize if battle vest button exists (user is authenticated)
    if (!battleVestBtn) return;

    const productSlug = battleVestBtn.dataset.productSlug;
    const heartIcon = battleVestBtn.querySelector('.heart-icon');
    const btnText = battleVestBtn.querySelector('.vest-btn-text'); // May be null now

    // Check if product is already in vest on page load
    checkInVest();

    // Add click handler
    battleVestBtn.addEventListener('click', function() {
        const isInVest = heartIcon.classList.contains('fas');

        if (isInVest) {
            // Remove from vest
            removeFromVest();
        } else {
            // Add to vest
            addToVest();
        }
    });

    function checkInVest() {
        fetch(`/products/${productSlug}/check-in-vest/`)
            .then(response => response.json())
            .then(data => {
                if (data.in_vest) {
                    // Product is in vest - show filled heart
                    heartIcon.classList.remove('far');
                    heartIcon.classList.add('fas');
                    if (btnText) btnText.textContent = 'IN YOUR BATTLE VEST';
                    battleVestBtn.classList.add('in-vest');
                }
                updateVestCount(data.item_count);
            })
            .catch(error => console.error('Error checking vest:', error));
    }

    function addToVest() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch(`/products/${productSlug}/add-to-vest/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update button to filled heart
                heartIcon.classList.remove('far');
                heartIcon.classList.add('fas');
                if (btnText) btnText.textContent = 'IN YOUR BATTLE VEST';
                battleVestBtn.classList.add('in-vest');

                // Show success toast
                showToast(data.message, 'success');

                // Update count
                updateVestCount(data.item_count);
            } else {
                showToast(data.message, 'info');
            }
        })
        .catch(error => {
            console.error('Error adding to vest:', error);
            showToast('Failed to add to Battle Vest', 'error');
        });
    }

    function removeFromVest() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch(`/products/${productSlug}/remove-from-vest/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update button to outline heart
                heartIcon.classList.remove('fas');
                heartIcon.classList.add('far');
                if (btnText) btnText.textContent = 'ADD TO BATTLE VEST';
                battleVestBtn.classList.remove('in-vest');

                // Show info toast
                showToast(data.message, 'info');

                // Update count
                updateVestCount(data.item_count);
            } else {
                showToast(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error removing from vest:', error);
            showToast('Failed to remove from Battle Vest', 'error');
        });
    }

    function updateVestCount(count) {
        // Update both mobile and desktop count badges
        const mobileBadge = document.getElementById('battleVestCount');
        const desktopBadge = document.getElementById('battleVestCountDesktop');

        if (mobileBadge) {
            mobileBadge.textContent = count;
            mobileBadge.style.display = count > 0 ? 'inline-block' : 'none';
        }

        if (desktopBadge) {
            desktopBadge.textContent = count;
            desktopBadge.style.display = count > 0 ? 'inline-block' : 'none';
        }
    }

    // showToast is defined globally in base.html
});

// Product Image Gallery functionality
document.addEventListener('DOMContentLoaded', function() {
    const mainImageContainer = document.getElementById('mainImageContainer');
    const mainImage = document.getElementById('mainProductImage');
    const thumbnails = document.querySelectorAll('.image-thumbnails .thumbnail');

    // Mobile tap-to-flip functionality for main image
    if (mainImageContainer) {
        mainImageContainer.addEventListener('click', function() {
            // Only on mobile
            if (window.innerWidth < 992) {
                mainImageContainer.classList.toggle('image-flipped');
            }
        });
    }

    // Thumbnail click functionality
    if (thumbnails.length > 0 && mainImage) {
        thumbnails.forEach(thumbnail => {
            thumbnail.addEventListener('click', function() {
                const newImageUrl = this.getAttribute('data-image-url');

                // Update main image
                mainImage.src = newImageUrl;

                // Update active thumbnail
                thumbnails.forEach(t => t.classList.remove('active'));
                this.classList.add('active');

                // Reset flip state on mobile
                if (mainImageContainer) {
                    mainImageContainer.classList.remove('image-flipped');
                }
            });
        });
    }

    // Social Share Functionality
    const shareButtons = document.querySelectorAll('.share-btn');

    shareButtons.forEach(button => {
        button.addEventListener('click', function() {
            const platform = this.dataset.platform;
            const productName = this.dataset.productName || '';
            const productUrl = this.dataset.productUrl || '';
            const productImage = this.dataset.productImage || '';

            // Get product slug from battle vest button
            const battleVestBtn = document.getElementById('battleVestBtn');
            const productSlug = battleVestBtn ? battleVestBtn.dataset.productSlug : '';

            // Track share event (analytics)
            if (typeof gtag !== 'undefined') {
                gtag('event', 'share', {
                    method: platform,
                    content_type: 'product',
                    item_id: productSlug
                });
            }

            // Handle different platforms
            switch(platform) {
                case 'facebook':
                    shareToFacebook(productUrl, productName);
                    break;
                case 'twitter':
                    shareToTwitter(productUrl, productName);
                    break;
                case 'pinterest':
                    shareToPinterest(productUrl, productName, productImage);
                    break;
                case 'instagram':
                    shareToInstagram(productUrl, productName);
                    break;
                case 'copy-link':
                    copyToClipboard(productUrl);
                    break;
            }
        });
    });

    // Facebook share function
    function shareToFacebook(url, title) {
        const shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}&quote=${encodeURIComponent('Check out this ' + title + ' from HENDOSHI - Wear Your Weird!')}`;
        window.open(shareUrl, 'facebook-share', 'width=600,height=400');
    }

    // Twitter share function
    function shareToTwitter(url, title) {
        const text = `Check out this ${title} from HENDOSHI - Wear Your Weird! ${url}`;
        const shareUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`;
        window.open(shareUrl, 'twitter-share', 'width=600,height=400');
    }

    // Pinterest share function
    function shareToPinterest(url, title, imageUrl) {
        if (!imageUrl) {
            // Fallback to copy link if no image
            copyToClipboard(url);
            showToast('Link copied! Share this image on Pinterest manually.', 'info');
            return;
        }
        const description = `Check out this ${title} from HENDOSHI - Wear Your Weird!`;
        const shareUrl = `https://pinterest.com/pin/create/button/?url=${encodeURIComponent(url)}&media=${encodeURIComponent(imageUrl)}&description=${encodeURIComponent(description)}`;
        window.open(shareUrl, 'pinterest-share', 'width=600,height=400');
    }

    // Instagram share function (opens Instagram app/website)
    function shareToInstagram(url, title) {
        // Instagram doesn't have a direct share URL like Facebook/Twitter
        // We'll copy the link and show instructions
        copyToClipboard(url);
        showToast('Link copied! Share this on Instagram by pasting the link in your story or bio.', 'info');

        // Try to open Instagram app/website
        const instagramUrl = 'https://www.instagram.com/';
        window.open(instagramUrl, 'instagram-share');
    }

    // Copy to clipboard function
    function copyToClipboard(text) {
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(text).then(() => {
                showToast('Link copied to clipboard!', 'success');
            }).catch(() => {
                fallbackCopyToClipboard(text);
            });
        } else {
            fallbackCopyToClipboard(text);
        }
    }

    // Fallback copy function for older browsers
    function fallbackCopyToClipboard(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();

        try {
            document.execCommand('copy');
            showToast('Link copied to clipboard!', 'success');
        } catch (err) {
            showToast('Failed to copy link. Please copy manually.', 'error');
        }

        document.body.removeChild(textArea);
    }

    // Mobile Web Share API support
    if (navigator.share) {
        // Add a native share button for mobile devices
        const mobileShareBtn = document.createElement('button');
        mobileShareBtn.className = 'share-btn mobile-share-btn';
        mobileShareBtn.innerHTML = '<i class="fas fa-share-alt"></i>';
        mobileShareBtn.style.borderColor = 'var(--electric-yellow)';
        mobileShareBtn.style.color = 'var(--electric-yellow)';

        mobileShareBtn.addEventListener('click', async () => {
            // Get product info from data attributes
            const firstShareBtn = document.querySelector('.share-btn[data-product-name]');
            const productName = firstShareBtn ? firstShareBtn.dataset.productName : '';
            const productUrl = firstShareBtn ? firstShareBtn.dataset.productUrl : window.location.href;

            // Get product slug from battle vest button
            const battleVestBtn = document.getElementById('battleVestBtn');
            const productSlug = battleVestBtn ? battleVestBtn.dataset.productSlug : '';

            try {
                await navigator.share({
                    title: productName + ' - HENDOSHI',
                    text: 'Check out this ' + productName + ' from HENDOSHI - Wear Your Weird!',
                    url: productUrl
                });

                // Track share event
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'share', {
                        method: 'native',
                        content_type: 'product',
                        item_id: productSlug
                    });
                }

                showToast('Shared successfully!', 'success');
            } catch (err) {
                // User cancelled or error occurred
                console.log('Share cancelled or failed');
            }
        });

        // Insert the mobile share button at the beginning
        const shareButtonsContainer = document.querySelector('.social-share-buttons');
        if (shareButtonsContainer) {
            shareButtonsContainer.insertBefore(mobileShareBtn, shareButtonsContainer.firstChild);
        }
    }
});