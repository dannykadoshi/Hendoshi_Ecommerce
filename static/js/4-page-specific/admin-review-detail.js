/* ================================================
   HENDOSHI - ADMIN REVIEW DETAIL
   ================================================

   Purpose: Drives the admin review moderation UI — approve/reject status updates,
            admin reply submission/removal, and image deletion via AJAX

   Contains:
   - updateStatus() / proceedWithStatusUpdate() — AJAX POST to approve or reject a review
   - Admin reply form submission and clearReply() — save or remove admin reply via fetch
   - deleteImage() — AJAX DELETE for individual review images
   - showReviewConfirmModal() / closeReviewConfirmModal() — Bootstrap modal confirmation dialog

   Dependencies: Bootstrap 5 (Modal), base.js (showToast)
   Load Order: Load on admin review detail page only
   ================================================ */

// Admin Review Detail - Review Status Update, Admin Reply, Image Deletion
const reviewDetailCard = document.querySelector('.review-detail-card');
const reviewId = reviewDetailCard ? reviewDetailCard.dataset.reviewId : null;

// Make functions globally available
window.updateStatus = updateStatus;
window.clearReply = clearReply;
window.deleteImage = deleteImage;
window.closeReviewConfirmModal = closeReviewConfirmModal;

// Global variables for modal callbacks
let currentConfirmCallback = null;

function showReviewConfirmModal(message, onConfirm) {
    const modal = document.getElementById('reviewConfirmModal');
    const messageEl = document.getElementById('reviewConfirmMessage');
    const confirmBtn = document.getElementById('confirmActionBtn');

    if (!modal || !messageEl || !confirmBtn) {
        console.error('Review confirm modal elements not found');
        // Fallback to browser confirm
        if (confirm(message)) {
            onConfirm();
        }
        return;
    }

    messageEl.textContent = message;
    currentConfirmCallback = onConfirm;

    // Set up confirm button
    confirmBtn.onclick = function() {
        const bsModal = bootstrap.Modal.getInstance(modal);
        if (bsModal) {
            bsModal.hide();
        }
        if (currentConfirmCallback) {
            currentConfirmCallback();
        }
    };

    // Show Bootstrap modal
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
}

function closeReviewConfirmModal() {
    const modal = document.getElementById('reviewConfirmModal');
    if (modal) {
        const bsModal = bootstrap.Modal.getInstance(modal);
        if (bsModal) {
            bsModal.hide();
        }
    }
    currentConfirmCallback = null;
}

function updateStatus(reviewId, status) {
    showReviewConfirmModal(
        `Are you sure you want to ${status} this review?`,
        function() {
            proceedWithStatusUpdate(reviewId, status);
        }
    );
}

function proceedWithStatusUpdate(reviewId, status) {
    if (!reviewDetailCard) {
        console.error('Review detail card not found');
        showToast('Error: Review detail card not found', 'error');
        return;
    }

    const updateStatusUrl = reviewDetailCard.dataset.updateStatusUrl;
    const adminListReviewsUrl = reviewDetailCard.dataset.adminListReviewsUrl;

    if (!updateStatusUrl) {
        console.error('Update status URL not found');
        showToast('Error: Update status URL not configured', 'error');
        return;
    }

    fetch(updateStatusUrl.replace('0', reviewId), {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: `status=${status}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update the status badge
            const badge = document.querySelector('.status-badge');
            badge.className = `status-badge ${status}`;
            badge.textContent = status.charAt(0).toUpperCase() + status.slice(1);

            // Show success message
            showToast(`Review ${status} successfully!`, 'success');

            // Redirect back to list after a short delay
            setTimeout(() => {
                window.location.href = adminListReviewsUrl;
            }, 1500);
        } else {
            showToast('Failed to update review status', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Failed to update review status', 'error');
    });
}

// Admin Reply Form
const adminReplyForm = document.getElementById('adminReplyForm');
if (adminReplyForm) {
    const adminReplyUrl = adminReplyForm.dataset.adminReplyUrl;
    if (!adminReplyUrl) {
        console.error('Admin reply URL not found on form');
    }
    
    adminReplyForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const replyText = document.getElementById('replyText').value.trim();

        fetch(adminReplyUrl.replace('0', reviewId), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: `reply=${encodeURIComponent(replyText)}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('Reply saved successfully!', 'success');
                // Reload page to show updated reply
                setTimeout(() => location.reload(), 1000);
            } else {
                showToast('Failed to save reply', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Failed to save reply', 'error');
        });
    });
}

function clearReply() {
    showReviewConfirmModal(
        'Are you sure you want to remove this reply?',
        function() {
            proceedWithReplyRemoval();
        }
    );
}

function proceedWithReplyRemoval() {
    const adminReplyUrl = adminReplyForm.dataset.adminReplyUrl;

    fetch(adminReplyUrl.replace('0', reviewId), {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: 'reply='
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Reply removed successfully!', 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showToast('Failed to remove reply', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Failed to remove reply', 'error');
    });
}

function deleteImage(imageId) {
    showReviewConfirmModal(
        'Are you sure you want to delete this image?',
        function() {
            proceedWithImageDeletion(imageId);
        }
    );
}

function proceedWithImageDeletion(imageId) {
    const deleteImageUrl = reviewDetailCard.dataset.deleteImageUrl;

    fetch(deleteImageUrl.replace('0', imageId), {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Remove the image element
            const imageContainer = document.getElementById(`review-image-${imageId}`);
            if (imageContainer) {
                imageContainer.remove();
            }
            showToast('Image deleted successfully!', 'success');
        } else {
            showToast('Failed to delete image', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Failed to delete image', 'error');
    });
}

function showToast(message, type) {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type === 'success' ? 'success' : 'danger'} position-fixed`;
    toast.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        background-color: ${type === 'success' ? 'rgba(25, 135, 84, 0.95)' : 'rgba(220, 53, 69, 0.95)'};
        color: white;
        border: 1px solid ${type === 'success' ? '#198754' : '#dc3545'};
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
    `;
    toast.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-triangle'} me-2"></i>
            <span>${message}</span>
            <button type="button" class="btn-close btn-close-white ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}
