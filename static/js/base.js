// HENDOSHI Base JavaScript

// Theme Toggle Functionality
document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('themeToggle');
    const htmlElement = document.documentElement;
    
    // Exit if theme toggle button doesn't exist on this page
    if (!themeToggle) {
        return;
    }
    
    // Check for saved theme preference or default to system preference
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const initialTheme = savedTheme || (prefersDark ? 'dark' : 'light');
    
    // Set initial theme
    setTheme(initialTheme);
    
    // Theme toggle button click handler
    themeToggle.addEventListener('click', function(e) {
        e.preventDefault();
        const currentTheme = htmlElement.classList.contains('light-mode') ? 'light' : 'dark';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
    });
    
    function setTheme(theme) {
        if (theme === 'light') {
            htmlElement.classList.add('light-mode');
            themeToggle.classList.add('light-mode-active');
            themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
            themeToggle.removeAttribute('title');
            localStorage.setItem('theme', 'light');
        } else {
            htmlElement.classList.remove('light-mode');
            themeToggle.classList.remove('light-mode-active');
            themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
            themeToggle.removeAttribute('title');
            localStorage.setItem('theme', 'dark');
        }
    }
});

// Dropdown hover behavior for desktop
document.addEventListener('DOMContentLoaded', function() {
    if (window.innerWidth >= 992) {
        const dropdowns = document.querySelectorAll('.navbar-right .dropdown, .desktop-menu .dropdown');
        
        dropdowns.forEach(dropdown => {
            let hideTimeout;
            
            const showDropdown = function() {
                clearTimeout(hideTimeout);
                const toggleBtn = dropdown.querySelector('.dropdown-toggle');
                const menu = dropdown.querySelector('.dropdown-menu');
                if (toggleBtn && menu && !menu.classList.contains('show')) {
                    const bsDropdown = bootstrap.Dropdown.getOrCreateInstance(toggleBtn);
                    bsDropdown.show();
                }
            };
            
            const hideDropdown = function() {
                hideTimeout = setTimeout(function() {
                    const toggleBtn = dropdown.querySelector('.dropdown-toggle');
                    if (toggleBtn) {
                        const bsDropdown = bootstrap.Dropdown.getInstance(toggleBtn);
                        if (bsDropdown) {
                            bsDropdown.hide();
                        }
                    }
                }, 100);
            };
            
            dropdown.addEventListener('mouseenter', showDropdown);
            dropdown.addEventListener('mouseleave', hideDropdown);
            
            // Keep dropdown open when hovering over the menu itself
            const menu = dropdown.querySelector('.dropdown-menu');
            if (menu) {
                menu.addEventListener('mouseenter', showDropdown);
                menu.addEventListener('mouseleave', hideDropdown);
            }
        });
    }
});

// Auto-dismiss messages after 4 seconds (exclude guide alerts)
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        let alerts = document.querySelectorAll('.alert:not(.guide-alert)');
        alerts.forEach(function(alert) {
            let bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 4000);
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

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
        s.setAttribute('aria-hidden', s.classList.contains('active') ? 'false' : 'true');
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
        slides[currentSlide].setAttribute('aria-hidden', 'true');
        currentSlide = index % slides.length;
        if (currentSlide < 0) currentSlide = slides.length - 1;
        slides[currentSlide].classList.add('active');
        slides[currentSlide].setAttribute('aria-hidden', 'false');
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

// Newsletter Form Validation
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('newsletterForm');
    if (!form) return;
    
    const emailInput = document.getElementById('newsletter-email');
    const errorDiv = form.querySelector('.newsletter-error');
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Clear previous error
        errorDiv.classList.remove('show');
        emailInput.classList.remove('invalid');
        
        // Validate email
        const email = emailInput.value.trim();
        
        if (!email) {
            showError('Please enter your email address');
            return;
        }
        
        if (!isValidEmail(email)) {
            showError('Please enter a valid email address (e.g., you@example.com)');
            return;
        }
        
        // Consent checkbox (GDPR)
        const consentCheckbox = document.getElementById('newsletter-consent');
        const consent = consentCheckbox ? consentCheckbox.checked : false;
        if (!consent) {
            showError('Please agree to the Privacy Policy to subscribe.');
            return;
        }

        // If validation passes, submit via AJAX to backend
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : '';

        fetch('/notifications/newsletter/subscribe/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `email=${encodeURIComponent(email)}&consent=${consent ? '1' : '0'}`
        })
        .then(response => response.json().then(data => ({status: response.status, body: data})))
        .then(({status, body}) => {
            if (status === 200) {
                // Server tells user to check email for confirmation
                showSuccessMessage(body.message || 'Confirmation email sent. Please check your inbox.');
                emailInput.value = '';
                if (consentCheckbox) consentCheckbox.checked = false;
            } else if (status === 409) {
                showError(body.message || 'Email already subscribed.');
            } else {
                showError(body.message || 'Subscription failed. Please try again later.');
            }
        })
        .catch(() => {
            showError('Network error. Please try again later.');
        });
    });
    
    function showError(message) {
        errorDiv.textContent = message;
        errorDiv.classList.add('show');
        emailInput.classList.add('invalid');
        
        // Auto-hide error after 4 seconds
        setTimeout(function() {
            errorDiv.classList.remove('show');
            emailInput.classList.remove('invalid');
        }, 4000);
    }
    
    function showSuccess() {
        showSuccessMessage('Thanks for subscribing!');
    }

    function showSuccessMessage(message) {
        errorDiv.textContent = '✓ ' + (message || 'Thanks for subscribing!');
        errorDiv.style.borderLeftColor = '#00ff00';
        errorDiv.style.color = '#00ff00';
        errorDiv.classList.add('show');

        setTimeout(function() {
            errorDiv.classList.remove('show');
            errorDiv.style.borderLeftColor = '';
            errorDiv.style.color = '';
        }, 4500);
    }
    
    function isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
});

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
    const itemWidth = 280 + 24; // item width + gap
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