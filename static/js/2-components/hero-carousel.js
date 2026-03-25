/* ================================================
   HENDOSHI - HERO CAROUSEL
   ================================================
   
   Purpose: JavaScript functionality for hero carousel
   
   Contains:
   - Event handlers
   - User interactions
   - Dynamic functionality
   
   Dependencies: utils.js (typically)
   Load Order: Load as needed for specific pages
   ================================================ */

// Hero background carousel with navigation dots
document.addEventListener('DOMContentLoaded', function() {
    const slides = document.querySelectorAll('.carousel-slide');
    const dots = document.querySelectorAll('.hero-carousel-dot');
    const ctaButton = document.querySelector('.hero-cta-btn');

    if (slides.length === 0) return;
    let currentSlide = 0;

    // Find any pre-marked active slide
    slides.forEach((s, i) => {
        if (s.classList.contains('active')) currentSlide = i;
        const isActive = s.classList.contains('active');
        if (isActive) {
            s.removeAttribute('inert');
        } else {
            s.setAttribute('inert', '');
        }
    });

    // Update navigation dots
    function updateDots(index) {
        dots.forEach((dot, i) => {
            if (i === index) {
                dot.classList.add('active');
            } else {
                dot.classList.remove('active');
            }
        });
    }

    function showSlide(index) {
        if (index === currentSlide) return;
        slides[currentSlide].classList.remove('active');
        slides[currentSlide].setAttribute('inert', '');
        currentSlide = index % slides.length;
        if (currentSlide < 0) currentSlide = slides.length - 1;
        slides[currentSlide].classList.add('active');
        slides[currentSlide].removeAttribute('inert');
        updateDots(currentSlide);
    }

    function nextSlide() {
        showSlide((currentSlide + 1) % slides.length);
    }

    // Auto-play with pause on hover/touch
    const HERO_INTERVAL = 5000;
    let heroTimer = null;

    function startHeroAutoplay() {
        stopHeroAutoplay();
        heroTimer = setInterval(nextSlide, HERO_INTERVAL);
    }

    function stopHeroAutoplay() {
        if (heroTimer) {
            clearInterval(heroTimer);
            heroTimer = null;
        }
    }

    function resetHeroAutoplay() {
        stopHeroAutoplay();
        startHeroAutoplay();
    }

    // Navigation dot click handlers
    dots.forEach((dot, index) => {
        dot.addEventListener('click', function() {
            showSlide(index);
            resetHeroAutoplay();
        });
    });

    // Pause on hover for desktop and on touch for mobile
    const heroEl = document.querySelector('.hero') || document.querySelector('.hero-carousel');
    if (heroEl) {
        heroEl.addEventListener('mouseenter', stopHeroAutoplay);
        heroEl.addEventListener('mouseleave', startHeroAutoplay);
        heroEl.addEventListener('touchstart', stopHeroAutoplay, {passive: true});
        heroEl.addEventListener('touchend', resetHeroAutoplay, {passive: true});
    }

    // Make sure we stop autoplay when page is hidden (tab inactive)
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) stopHeroAutoplay(); else startHeroAutoplay();
    });

    // Add loaded class to CTA button after animations complete
    if (ctaButton) {
        setTimeout(function() {
            ctaButton.classList.add('loaded');
        }, 2000);
    }

    // Initialize dots state
    updateDots(currentSlide);

    // Start autoplay
    startHeroAutoplay();
});

