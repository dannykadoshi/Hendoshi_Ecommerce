/* ================================================
   HENDOSHI - VAULT HALL OF FAME
   ================================================
   
   Purpose: JavaScript functionality for vault hall of fame
   
   Contains:
   - Event handlers
   - User interactions
   - Dynamic functionality
   
   Dependencies: utils.js (typically)
   Load Order: Load as needed for specific pages
   ================================================ */

// Hall of Fame specific functionality

// Toggle caption expansion
function toggleCaption(photoId) {
    const caption = document.getElementById('caption-' + photoId);
    const btn = document.getElementById('read-more-' + photoId);
    
    if (!caption || !btn) return;
    
    if (caption.classList.contains('expanded')) {
        caption.classList.remove('expanded');
        btn.innerHTML = '<i class="fas fa-chevron-down"></i> Read More';
    } else {
        caption.classList.add('expanded');
        btn.innerHTML = '<i class="fas fa-chevron-up"></i> Show Less';
    }
}

// Event delegation for Hall of Fame interactions
document.addEventListener('DOMContentLoaded', function() {
    console.log('Hall of Fame JS loaded');
    
    // Toggle caption with data attributes
    document.addEventListener('click', function(e) {
        const toggleBtn = e.target.closest('[data-action="toggle-caption"]');
        if (toggleBtn) {
            const photoId = toggleBtn.dataset.photoId;
            console.log('Toggle caption clicked:', photoId);
            toggleCaption(photoId);
        }
    });
    
    // Vote buttons with data attributes
    document.addEventListener('click', function(e) {
        const voteBtn = e.target.closest('[data-action="vote"]');
        if (voteBtn) {
            e.preventDefault();
            const photoId = voteBtn.dataset.photoId;
            const voteType = voteBtn.dataset.voteType;
            console.log('Vote clicked:', photoId, voteType);
            console.log('votePhoto function exists:', typeof votePhoto);
            if (typeof votePhoto === 'function') {
                votePhoto(photoId, voteType);
            } else {
                console.error('votePhoto function not found!');
            }
        }
    });
    
    // Like button with data attributes
    document.addEventListener('click', function(e) {
        const likeBtn = e.target.closest('[data-action="like-photo"]');
        if (likeBtn) {
            e.preventDefault();
            const photoId = likeBtn.dataset.photoId;
            console.log('Like clicked:', photoId);
            console.log('likePhotoUnified function exists:', typeof likePhotoUnified);
            if (typeof likePhotoUnified === 'function') {
                likePhotoUnified(photoId, 'hall_of_fame');
            } else {
                console.error('likePhotoUnified function not found!');
            }
        }
    });
});
