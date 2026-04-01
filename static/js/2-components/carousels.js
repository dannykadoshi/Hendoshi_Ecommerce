/* ================================================
   HENDOSHI - CAROUSELS
   ================================================

   Purpose: Powers the Collections carousel on the homepage with manual
            prev/next navigation, looping, and auto-play that pauses on hover

   Contains:
   - updateCollectionsCarousel() — translates the carousel track to show the current index
   - nextCollectionsSlide() / prevCollectionsSlide() — advance with looping support
   - Auto-play timer (4s interval) with startAutoPlay / stopAutoPlay / resetAutoPlay
   - Mouseenter/mouseleave listeners on the container and individual cards to pause auto-play

   Dependencies: None (vanilla JS)
   Load Order: Load on homepage only
   ================================================ */

// Collections Carousel
document.addEventListener('DOMContentLoaded', function() {
    const collectionsTrack = document.getElementById('collections-track');
    const collectionsPrevBtn = document.getElementById('collections-prev');
    const collectionsNextBtn = document.getElementById('collections-next');

    // Only initialize if elements exist (homepage)
    if (!collectionsTrack || !collectionsPrevBtn || !collectionsNextBtn) {
        return;
    }

    const collectionsItems = collectionsTrack.children;
    const itemWidth = 210 + 24; // item width + gap
    let currentIndex = 0;
    const totalItems = collectionsItems.length;
    // Force max 3 visible items for better UX, always scrollable
    const visibleItems = Math.min(3, totalItems);
    const maxIndex = Math.max(0, totalItems - visibleItems);

    function updateCollectionsCarousel() {
        const translateX = -currentIndex * itemWidth;
        collectionsTrack.style.transform = `translateX(${translateX}px)`;

        // Update button states - always enabled for looping
        collectionsPrevBtn.style.opacity = '1';
        collectionsPrevBtn.disabled = false;
        collectionsNextBtn.style.opacity = '1';
        collectionsNextBtn.disabled = false;
    }

    function nextCollectionsSlide() {
        currentIndex++;
        if (currentIndex > maxIndex) {
            currentIndex = 0; // Loop back to start
        }
        updateCollectionsCarousel();
    }

    function prevCollectionsSlide() {
        currentIndex--;
        if (currentIndex < 0) {
            currentIndex = maxIndex; // Loop to end
        }
        updateCollectionsCarousel();
    }

    // Event listeners for click
    collectionsNextBtn.addEventListener('click', () => {
        nextCollectionsSlide();
        resetAutoPlay(); // Reset timer on manual interaction
    });
    collectionsPrevBtn.addEventListener('click', () => {
        prevCollectionsSlide();
        resetAutoPlay(); // Reset timer on manual interaction
    });

    // Auto-play functionality
    let autoPlayInterval;
    const autoPlayDelay = 4000; // Auto-advance every 4 seconds

    function startAutoPlay() {
        clearInterval(autoPlayInterval);
        autoPlayInterval = setInterval(nextCollectionsSlide, autoPlayDelay);
    }

    function stopAutoPlay() {
        clearInterval(autoPlayInterval);
    }

    function resetAutoPlay() {
        stopAutoPlay();
        startAutoPlay();
    }

    // Pause auto-play on hover over carousel container
    const carouselContainer = collectionsTrack.closest('.collections-carousel');
    if (carouselContainer) {
        carouselContainer.addEventListener('mouseenter', stopAutoPlay);
        carouselContainer.addEventListener('mouseleave', startAutoPlay);
    }

    // Also pause auto-play on hover over individual collection cards
    const collectionCards = collectionsTrack.querySelectorAll('.collection-card');
    collectionCards.forEach(card => {
        card.addEventListener('mouseenter', stopAutoPlay);
        card.addEventListener('mouseleave', startAutoPlay);
    });

    // Clear interval when page unloads
    window.addEventListener('beforeunload', stopAutoPlay);

    // Start auto-play
    startAutoPlay();

    // Touch/swipe support for mobile
    let startX = 0;
    let isDragging = false;

    collectionsTrack.addEventListener('touchstart', (e) => {
        startX = e.touches[0].clientX;
        isDragging = true;
        stopAutoPlay(); // Pause auto-play during touch
    });

    collectionsTrack.addEventListener('touchmove', (e) => {
        if (!isDragging) return;
        const currentX = e.touches[0].clientX;
        const diff = startX - currentX;

        if (Math.abs(diff) > 50) {
            if (diff > 0) {
                nextCollectionsSlide();
            } else {
                prevCollectionsSlide();
            }
            isDragging = false;
        }
    });

    collectionsTrack.addEventListener('touchend', () => {
        isDragging = false;
        resetAutoPlay(); // Resume auto-play after touch
    });

    // Initialize carousel
    updateCollectionsCarousel();

    // Update on window resize
    window.addEventListener('resize', () => {
        // Recalculate on resize, but keep max 3 visible
        const newVisibleItems = Math.min(3, totalItems);
        const newMaxIndex = Math.max(0, totalItems - newVisibleItems);

        // Adjust current index if it's now out of bounds
        if (currentIndex > newMaxIndex) {
            currentIndex = newMaxIndex;
        }

        updateCollectionsCarousel();
    });
});

// Related Products Carousel Functionality
document.addEventListener('DOMContentLoaded', function() {
    const relatedProductsTrack = document.getElementById('related-products-track');
    const relatedProductsPrev = document.getElementById('related-products-prev');
    const relatedProductsNext = document.getElementById('related-products-next');

    if (!relatedProductsTrack || !relatedProductsPrev || !relatedProductsNext) {
        return; // Exit if elements don't exist
    }

    const relatedProductItems = relatedProductsTrack.children;
    const totalRelatedItems = relatedProductItems.length;
    let relatedCurrentIndex = 0;
    let relatedVisibleItems = 3; // Default for desktop
    let relatedMaxIndex = Math.max(0, totalRelatedItems - relatedVisibleItems);

    function updateRelatedProductsCarousel() {
        const itemWidth = relatedProductItems[0] ? relatedProductItems[0].offsetWidth + 24 : 234; // item width + gap
        const translateX = -relatedCurrentIndex * itemWidth;
        relatedProductsTrack.style.transform = `translateX(${translateX}px)`;
    }

    function nextRelatedProductsSlide() {
        if (relatedCurrentIndex < relatedMaxIndex) {
            relatedCurrentIndex++;
            updateRelatedProductsCarousel();
        } else {
            // Loop back to start
            relatedCurrentIndex = 0;
            updateRelatedProductsCarousel();
        }
        // Auto-play disabled
    }

    function prevRelatedProductsSlide() {
        if (relatedCurrentIndex > 0) {
            relatedCurrentIndex--;
            updateRelatedProductsCarousel();
        } else {
            // Loop to end
            relatedCurrentIndex = relatedMaxIndex;
            updateRelatedProductsCarousel();
        }
        // Auto-play disabled
    }

    // Event listeners for navigation buttons
    relatedProductsNext.addEventListener('click', nextRelatedProductsSlide);
    relatedProductsPrev.addEventListener('click', prevRelatedProductsSlide);

    // Auto-play functionality for related products
    let relatedAutoPlayInterval;
    const relatedAutoPlayDelay = 5000; // Auto-advance every 5 seconds

    function startRelatedAutoPlay() {
        clearInterval(relatedAutoPlayInterval);
        relatedAutoPlayInterval = setInterval(nextRelatedProductsSlide, relatedAutoPlayDelay);
    }

    function stopRelatedAutoPlay() {
        clearInterval(relatedAutoPlayInterval);
    }

    function resetRelatedAutoPlay() {
        stopRelatedAutoPlay();
        startRelatedAutoPlay();
    }

    // Pause auto-play on hover over carousel container (disabled)
    // const relatedCarouselContainer = relatedProductsTrack.closest('.related-products-carousel');
    // if (relatedCarouselContainer) {
    //     relatedCarouselContainer.addEventListener('mouseenter', stopRelatedAutoPlay);
    //     relatedCarouselContainer.addEventListener('mouseleave', startRelatedAutoPlay);
    // }

    // Clear interval when page unloads
    window.addEventListener('beforeunload', stopRelatedAutoPlay);

    // Touch/swipe support for mobile
    let relatedStartX = 0;
    let relatedIsDragging = false;

    relatedProductsTrack.addEventListener('touchstart', (e) => {
        relatedStartX = e.touches[0].clientX;
        relatedIsDragging = true;
        stopRelatedAutoPlay();
    });

    relatedProductsTrack.addEventListener('touchmove', (e) => {
        if (!relatedIsDragging) return;
        const relatedCurrentX = e.touches[0].clientX;
        const relatedDiff = relatedStartX - relatedCurrentX;

        if (Math.abs(relatedDiff) > 30) {
            if (relatedDiff > 0) {
                nextRelatedProductsSlide();
            } else {
                prevRelatedProductsSlide();
            }
            relatedIsDragging = false;
        }
    });

    relatedProductsTrack.addEventListener('touchend', () => {
        relatedIsDragging = false;
        resetRelatedAutoPlay();
    });

    // Update visible items based on screen size
    function updateRelatedVisibleItems() {
        const screenWidth = window.innerWidth;
        if (screenWidth <= 480) {
            relatedVisibleItems = 1;
        } else if (screenWidth <= 768) {
            relatedVisibleItems = 2;
        } else {
            relatedVisibleItems = 3;
        }
        relatedMaxIndex = Math.max(0, totalRelatedItems - relatedVisibleItems);

        if (relatedCurrentIndex > relatedMaxIndex) {
            relatedCurrentIndex = relatedMaxIndex;
        }

        updateRelatedProductsCarousel();
    }

    // Initialize carousel
    updateRelatedVisibleItems();
    updateRelatedProductsCarousel();

    // Update on window resize
    window.addEventListener('resize', updateRelatedVisibleItems);

    // Auto-play disabled - manual navigation only
});

// Recently Viewed Products Carousel Functionality
document.addEventListener('DOMContentLoaded', function() {
    const recentlyViewedTrack = document.getElementById('recently-viewed-products-track');
    const recentlyViewedPrev = document.getElementById('recently-viewed-products-prev');
    const recentlyViewedNext = document.getElementById('recently-viewed-products-next');

    if (!recentlyViewedTrack || !recentlyViewedPrev || !recentlyViewedNext) {
        return; // Exit if elements don't exist
    }

    const recentlyViewedItems = recentlyViewedTrack.children;
    const totalRecentlyViewedItems = recentlyViewedItems.length;
    let recentlyViewedCurrentIndex = 0;
    let recentlyViewedVisibleItems = 3; // Default for desktop
    let recentlyViewedMaxIndex = Math.max(0, totalRecentlyViewedItems - recentlyViewedVisibleItems);

    function updateRecentlyViewedCarousel() {
        const itemWidth = recentlyViewedItems[0] ? recentlyViewedItems[0].offsetWidth + 24 : 234; // item width + gap
        const translateX = -recentlyViewedCurrentIndex * itemWidth;
        recentlyViewedTrack.style.transform = `translateX(${translateX}px)`;
    }

    function nextRecentlyViewedSlide() {
        if (recentlyViewedCurrentIndex < recentlyViewedMaxIndex) {
            recentlyViewedCurrentIndex++;
            updateRecentlyViewedCarousel();
        } else {
            // Loop back to start
            recentlyViewedCurrentIndex = 0;
            updateRecentlyViewedCarousel();
        }
        // Auto-play disabled
    }

    function prevRecentlyViewedSlide() {
        if (recentlyViewedCurrentIndex > 0) {
            recentlyViewedCurrentIndex--;
            updateRecentlyViewedCarousel();
        } else {
            // Loop to end
            recentlyViewedCurrentIndex = recentlyViewedMaxIndex;
            updateRecentlyViewedCarousel();
        }
        // Auto-play disabled
    }

    // Event listeners for navigation buttons
    recentlyViewedNext.addEventListener('click', nextRecentlyViewedSlide);
    recentlyViewedPrev.addEventListener('click', prevRecentlyViewedSlide);

    // Auto-play functionality for recently viewed products
    let recentlyViewedAutoPlayInterval;
    const recentlyViewedAutoPlayDelay = 5000; // Auto-advance every 5 seconds

    function startRecentlyViewedAutoPlay() {
        clearInterval(recentlyViewedAutoPlayInterval);
        recentlyViewedAutoPlayInterval = setInterval(nextRecentlyViewedSlide, recentlyViewedAutoPlayDelay);
    }

    function stopRecentlyViewedAutoPlay() {
        clearInterval(recentlyViewedAutoPlayInterval);
    }

    function resetRecentlyViewedAutoPlay() {
        stopRecentlyViewedAutoPlay();
        startRecentlyViewedAutoPlay();
    }

    // Pause auto-play on hover over carousel container (disabled)
    // const recentlyViewedCarouselContainer = recentlyViewedTrack.closest('.recently-viewed-products-carousel');
    // if (recentlyViewedCarouselContainer) {
    //     recentlyViewedCarouselContainer.addEventListener('mouseenter', stopRecentlyViewedAutoPlay);
    //     recentlyViewedCarouselContainer.addEventListener('mouseleave', startRecentlyViewedAutoPlay);
    // }

    // Clear interval when page unloads
    window.addEventListener('beforeunload', stopRecentlyViewedAutoPlay);

    // Touch/swipe support for mobile
    let recentlyViewedStartX = 0;
    let recentlyViewedIsDragging = false;

    recentlyViewedTrack.addEventListener('touchstart', (e) => {
        recentlyViewedStartX = e.touches[0].clientX;
        recentlyViewedIsDragging = true;
        stopRecentlyViewedAutoPlay();
    });

    recentlyViewedTrack.addEventListener('touchmove', (e) => {
        if (!recentlyViewedIsDragging) return;
        const recentlyViewedCurrentX = e.touches[0].clientX;
        const recentlyViewedDiff = recentlyViewedStartX - recentlyViewedCurrentX;

        if (Math.abs(recentlyViewedDiff) > 30) {
            if (recentlyViewedDiff > 0) {
                nextRecentlyViewedSlide();
            } else {
                prevRecentlyViewedSlide();
            }
            recentlyViewedIsDragging = false;
        }
    });

    recentlyViewedTrack.addEventListener('touchend', () => {
        recentlyViewedIsDragging = false;
        resetRecentlyViewedAutoPlay();
    });

    // Update visible items based on screen size
    function updateRecentlyViewedVisibleItems() {
        const screenWidth = window.innerWidth;
        if (screenWidth <= 480) {
            recentlyViewedVisibleItems = 1;
        } else if (screenWidth <= 768) {
            recentlyViewedVisibleItems = 2;
        } else {
            recentlyViewedVisibleItems = 3;
        }
        recentlyViewedMaxIndex = Math.max(0, totalRecentlyViewedItems - recentlyViewedVisibleItems);

        if (recentlyViewedCurrentIndex > recentlyViewedMaxIndex) {
            recentlyViewedCurrentIndex = recentlyViewedMaxIndex;
        }

        updateRecentlyViewedCarousel();
    }

    // Initialize carousel
    updateRecentlyViewedVisibleItems();
    updateRecentlyViewedCarousel();

    // Update on window resize
    window.addEventListener('resize', updateRecentlyViewedVisibleItems);

    // Auto-play disabled - manual navigation only
});
