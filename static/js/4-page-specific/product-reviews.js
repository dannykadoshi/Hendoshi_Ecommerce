/* ================================================
   HENDOSHI - PRODUCT REVIEWS
   ================================================

   Purpose: Handles review eligibility checking, submission, image preview,
            and load-more pagination on the product detail reviews section

   Contains:
   - Write review button: AJAX eligibility check before revealing the review form
   - Review form submit: validates rating and minimum text length, submits via AJAX with CSRF
   - Image preview: FileReader-based preview for up to 3 uploaded review images (5 MB limit each)
   - Cancel button: resets and hides the form, clears image previews
   - Load more button: fetches and appends additional review cards via AJAX pagination

   Dependencies: base.js (showToast)
   Load Order: Load on product detail page only
   ================================================ */

document.addEventListener('DOMContentLoaded', function() {
    const writeReviewBtn = document.getElementById('writeReviewBtn');
    const reviewForm = document.getElementById('reviewForm');
    const cancelReviewBtn = document.getElementById('cancelReviewBtn');
    const submitReviewForm = document.getElementById('submitReviewForm');
    const loadMoreBtn = document.getElementById('loadMoreReviews');

    // Check eligibility when clicking write review
    if (writeReviewBtn) {
        writeReviewBtn.addEventListener('click', function() {
            const slug = this.dataset.productSlug;

            fetch(`/products/${slug}/review/check/`)
                .then(response => response.json())
                .then(data => {
                    if (data.can_review) {
                        reviewForm.classList.remove('d-none');
                        writeReviewBtn.style.display = 'none';
                    } else {
                        showToast(data.message, 'warning');
                    }
                })
                .catch(error => {
                    console.error('Error checking eligibility:', error);
                    showToast('Failed to check review eligibility', 'error');
                });
        });
    }

    // Cancel review
    if (cancelReviewBtn) {
        cancelReviewBtn.addEventListener('click', function() {
            reviewForm.classList.add('d-none');
            writeReviewBtn.style.display = 'inline-block';
            submitReviewForm.reset();
            // Clear image preview
            const imagePreview = document.getElementById('imagePreview');
            if (imagePreview) imagePreview.innerHTML = '';
        });
    }

    // Image preview functionality
    const reviewImagesInput = document.getElementById('reviewImages');
    if (reviewImagesInput) {
        reviewImagesInput.addEventListener('change', function() {
            const imagePreview = document.getElementById('imagePreview');
            imagePreview.innerHTML = '';

            const files = Array.from(this.files).slice(0, 3); // Max 3 images

            if (this.files.length > 3) {
                showToast('Only first 3 images will be uploaded', 'info');
            }

            files.forEach((file, index) => {
                // Validate file size (5MB)
                if (file.size > 5 * 1024 * 1024) {
                    showToast(`Image ${index + 1} exceeds 5MB limit`, 'warning');
                    return;
                }

                const reader = new FileReader();
                reader.onload = function(e) {
                    const img = document.createElement('div');
                    img.className = 'preview-image';
                    img.innerHTML = `<img src="${e.target.result}" alt="Preview ${index + 1}"><span class="remove-preview" data-index="${index}">&times;</span>`;
                    imagePreview.appendChild(img);
                };
                reader.readAsDataURL(file);
            });
        });
    }

    // Submit review
    if (submitReviewForm) {
        submitReviewForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = new FormData(this);
            const slug = writeReviewBtn.dataset.productSlug;

            // Validate rating
            if (!formData.get('rating')) {
                showToast('Please select a rating', 'warning');
                return;
            }

            // Validate review text
            const reviewText = formData.get('review_text');
            if (!reviewText || reviewText.trim().length < 20) {
                showToast('Review must be at least 20 characters', 'warning');
                return;
            }

            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch(`/products/${slug}/review/submit/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast(data.message, 'success');
                    reviewForm.classList.add('d-none');
                    writeReviewBtn.style.display = 'none';
                    submitReviewForm.reset();
                    // Clear image preview
                    const imagePreview = document.getElementById('imagePreview');
                    if (imagePreview) imagePreview.innerHTML = '';
                } else {
                    const errorMsg = data.errors ? Object.values(data.errors).join(', ') : data.message;
                    showToast(errorMsg, 'error');
                }
            })
            .catch(error => {
                console.error('Error submitting review:', error);
                showToast('Failed to submit review', 'error');
            });
        });
    }

    // Mark review helpful
    document.addEventListener('click', function(e) {
        if (e.target.closest('.helpful-btn')) {
            const btn = e.target.closest('.helpful-btn');
            const reviewId = btn.dataset.reviewId;
            const countSpan = btn.querySelector('.helpful-count');
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch(`/products/review/${reviewId}/helpful/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    countSpan.textContent = data.helpful_count;
                    btn.disabled = true;
                    showToast('Thanks for your feedback!', 'success');
                } else {
                    showToast(data.message, 'info');
                }
            })
            .catch(error => {
                console.error('Error marking helpful:', error);
                showToast('Failed to mark as helpful', 'error');
            });
        }
    });

    // Load more reviews
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', function() {
            const page = parseInt(this.dataset.page) + 1;
            const slug = this.dataset.productSlug;

            fetch(`/products/${slug}/reviews/?page=${page}`)
                .then(response => response.json())
                .then(data => {
                    const reviewsList = document.getElementById('reviewsList');

                    data.reviews.forEach(review => {
                        const reviewHtml = createReviewCard(review);
                        reviewsList.insertAdjacentHTML('beforeend', reviewHtml);
                    });

                    this.dataset.page = page;

                    if (!data.has_next) {
                        this.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Error loading reviews:', error);
                    showToast('Failed to load more reviews', 'error');
                });
        });
    }

    // Helper function to create review card HTML
    function createReviewCard(review) {
        const stars = Array(5).fill().map((_, i) => {
            return (i < review.rating ?
                '<i class="fas fa-star"></i>' :
                '<i class="far fa-star text-muted"></i>');
        }).join('');

        return `
            <div class="review-card" data-review-id="${review.id}">
                <div class="review-header">
                    <div>
                        <span class="reviewer-name">${review.username}</span>
                        ${review.verified ? '<span class="verified-badge ms-2"><i class="fas fa-check-circle"></i> Verified Purchase</span>' : ''}
                    </div>
                        <div class="review-rating">${stars}</div>
                </div>
                ${review.title ? `<h5 class="review-title">${review.title}</h5>` : ''}
                <p class="review-text">${review.text}</p>
                <div class="review-footer">
                    <small class="text-muted">${review.created_at}</small>
                    <button type="button" class="btn btn-sm btn-outline-secondary helpful-btn" data-review-id="${review.id}">
                        <i class="far fa-thumbs-up"></i> Helpful (<span class="helpful-count">${review.helpful_count}</span>)
                    </button>
                </div>
            </div>
        `;
    }
});