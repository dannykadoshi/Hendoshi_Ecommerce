/**
 * Base Template Global Functions
 * Extracted inline scripts from base.html - Global functions used site-wide
 */

// ============================================
// 1. DJANGO MESSAGES TOAST DISPLAY
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    const toasts = document.querySelectorAll('[data-message="true"]');
    toasts.forEach(function(toast, index) {
        // Stagger appearance for multiple toasts
        toast.style.animationDelay = (index * 0.1) + 's';

        let timeoutId;
        let remainingTime = 2000;
        let startTime = Date.now();

        // Pause timer on hover
        toast.addEventListener('mouseenter', function() {
            clearTimeout(timeoutId);
            remainingTime -= (Date.now() - startTime);
            // Pause progress bar
            const progressBar = toast.querySelector('.toast-progress-bar');
            if (progressBar) progressBar.style.animationPlayState = 'paused';
        });

        // Resume timer on mouse leave
        toast.addEventListener('mouseleave', function() {
            startTime = Date.now();
            timeoutId = setTimeout(dismissToast, remainingTime);
            // Resume progress bar
            const progressBar = toast.querySelector('.toast-progress-bar');
            if (progressBar) progressBar.style.animationPlayState = 'running';
        });

        function dismissToast() {
            toast.classList.add('toast-hiding');
            setTimeout(function() {
                if (toast.parentNode) toast.remove();
            }, 300);
        }

        // Start auto-dismiss timer
        timeoutId = setTimeout(dismissToast, 2000 + (index * 100));
    });
});

// ============================================
// 2. ADMIN PANEL & MOBILE MENU FUNCTIONALITY
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    // Unified function to close all submenus (admin + vault + content moderation)
    function closeAllSubmenus() {
        document.querySelectorAll('.admin-panel-submenu, .vault-submenu, .content-moderation-submenu').forEach(menu => {
            menu.classList.remove('show');
            if (menu.parentElement) menu.parentElement.classList.remove('show');
        });
    }

    // Admin Panel Dropdown - Click only (submenu opens to the left)
    function closeAllAdminSubmenus() {
        document.querySelectorAll('.admin-panel-submenu').forEach(menu => {
            menu.classList.remove('show');
            if (menu.parentElement) menu.parentElement.classList.remove('show');
        });
    }

    // Handle Admin Panel click to toggle submenu (open to left)
    document.querySelectorAll('.admin-panel-toggle').forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const wrapper = this.closest('.admin-panel-dropdown-wrapper');
            const submenu = wrapper.querySelector('.admin-panel-submenu');
            // Toggle .show class for submenu
            const isOpen = submenu.classList.contains('show');
            closeAllAdminSubmenus();
            if (!isOpen) {
                submenu.classList.add('show');
                wrapper.classList.add('show');
            }
        });
    });

    // Handle Vault submenu toggle (Hall of Fame)
    document.querySelectorAll('.vault-submenu-toggle').forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const wrapper = this.closest('.vault-submenu-dropdown-wrapper');
            const submenu = wrapper.querySelector('.vault-submenu');
            // Toggle .show class for submenu
            const isOpen = submenu.classList.contains('show');
            closeAllSubmenus();
            if (!isOpen) {
                submenu.classList.add('show');
                wrapper.classList.add('show');
            }
        });
    });

    // Handle Content Moderation submenu toggle (click only)
    document.querySelectorAll('.content-moderation-toggle').forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const submenu = this.parentElement.querySelector('.content-moderation-submenu');
            // Toggle .show class for submenu
            const isOpen = submenu.classList.contains('show');
            // Close all other submenus first
            document.querySelectorAll('.content-moderation-submenu').forEach(menu => {
                menu.classList.remove('show');
            });
            if (!isOpen) {
                submenu.classList.add('show');
            }
        });
    });

    // Close vault and admin submenus when mouse leaves the wrapper
    document.querySelectorAll('.vault-submenu-dropdown-wrapper, .admin-panel-dropdown-wrapper').forEach(wrapper => {
        wrapper.addEventListener('mouseleave', function() {
            const submenu = this.querySelector('.admin-panel-submenu, .vault-submenu, .content-moderation-submenu');
            if (submenu && submenu.classList.contains('show')) {
                closeAllSubmenus();
            }
        });
    });

    // Prevent submenu from closing when clicking inside it
    document.querySelectorAll('.admin-panel-submenu, .vault-submenu, .content-moderation-submenu').forEach(submenu => {
        submenu.addEventListener('click', function(e) {
            if (e.target.tagName === 'A' || e.target.closest('a')) {
                return;
            }
            e.stopPropagation();
        });
    });

    // Close submenu when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.admin-panel-dropdown-wrapper') && !e.target.closest('.vault-submenu-dropdown-wrapper')) {
            closeAllSubmenus();
        }
    });

    // Close submenu when parent dropdown closes
    document.querySelectorAll('.desktop-icons .dropdown, .mobile-icons .dropdown, .desktop-menu .nav-item.dropdown').forEach(parentDropdown => {
        parentDropdown.addEventListener('hidden.bs.dropdown', function() {
            closeAllSubmenus();
        });
    });

    // Mobile Menu Functionality
    const navBurger = document.getElementById('navBurger');
    const mobileMenu = document.getElementById('mobileMenu');
    const mobileMenuOverlay = document.getElementById('mobileMenuOverlay');
    const mobileMenuClose = document.getElementById('mobileMenuClose');
    const currencySwitcher = document.getElementById('currencySwitcher');
    const mobileThemeToggle = document.getElementById('mobileThemeToggle');
    const mobileSearchToggle = document.getElementById('mobileSearchToggle');
    const mobileSearchBox = document.getElementById('mobileSearchBox');
    const menuArrows = document.querySelectorAll('.menu-item-arrow');
    const menuTriggers = document.querySelectorAll('.menu-item-trigger');
    const submenuBackButtons = document.querySelectorAll('.submenu-back');

    // Toggle mobile menu
    function toggleMobileMenu() {
        navBurger.classList.toggle('active');
        mobileMenu.classList.toggle('active');
        mobileMenuOverlay.classList.toggle('active');
        document.body.classList.toggle('menu-open');
    }

    // Close mobile menu (for close button)
    function closeMobileMenu() {
        navBurger.classList.remove('active');
        mobileMenu.classList.remove('active');
        mobileMenuOverlay.classList.remove('active');
        document.body.classList.remove('menu-open');
    }

    navBurger.addEventListener('click', toggleMobileMenu);
    mobileMenuOverlay.addEventListener('click', toggleMobileMenu);
    if (mobileMenuClose) {
        mobileMenuClose.addEventListener('click', closeMobileMenu);
    }

    // Mobile search toggle (in burger menu)
    if (mobileSearchToggle && mobileSearchBox) {
        mobileSearchToggle.addEventListener('click', function(e) {
            e.preventDefault();
            mobileSearchBox.classList.toggle('show');
            const input = mobileSearchBox.querySelector('.search-input');
            if (mobileSearchBox.classList.contains('show') && input) {
                setTimeout(() => input.focus(), 100);
            }
        });
    }

    // Menu triggers (Collections, Product Type text)
    menuTriggers.forEach(trigger => {
        trigger.addEventListener('click', function(e) {
            e.preventDefault();
            const submenuId = this.dataset.submenu;
            const submenu = document.getElementById('submenu' + submenuId.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(''));
            
            const mainMenu = document.getElementById('menuMain');
            mainMenu.style.transform = 'translateX(-100%)';
            
            if (submenu) {
                submenu.classList.remove('hidden');
                setTimeout(() => {
                    submenu.style.transform = 'translateX(0)';
                }, 10);
            }
        });
    });

    // Menu item arrows (submenu navigation)
    menuArrows.forEach(arrow => {
        arrow.addEventListener('click', function(e) {
            e.preventDefault();
            const submenuId = this.dataset.submenu;
            const submenu = document.getElementById('submenu' + submenuId.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(''));
            
            const mainMenu = document.getElementById('menuMain');
            mainMenu.style.transform = 'translateX(-100%)';
            
            if (submenu) {
                submenu.classList.remove('hidden');
                setTimeout(() => {
                    submenu.style.transform = 'translateX(0)';
                }, 10);
            }
        });
    });

    // Submenu back buttons
    submenuBackButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const backTo = this.dataset.back;
            const currentSubmenu = this.closest('.menu-submenu');

            if (backTo === 'main') {
                // Going back to main menu
                const mainMenu = document.getElementById('menuMain');
                mainMenu.style.transform = 'translateX(0)';

                currentSubmenu.style.transform = 'translateX(100%)';
                setTimeout(() => {
                    currentSubmenu.classList.add('hidden');
                }, 300);
            } else if (backTo === 'account') {
                // Going back to account submenu
                const accountSubmenu = document.getElementById('accountSubmenu');

                currentSubmenu.style.transform = 'translateX(100%)';
                setTimeout(() => {
                    currentSubmenu.classList.add('hidden');
                    accountSubmenu.style.transform = 'translateX(0)';
                }, 300);
            } else if (backTo === 'vault') {
                // Going back to vault submenu
                const vaultSubmenu = document.getElementById('submenuVault');

                currentSubmenu.style.transform = 'translateX(100%)';
                setTimeout(() => {
                    currentSubmenu.classList.add('hidden');
                    vaultSubmenu.style.transform = 'translateX(0)';
                }, 300);
            }
        });
    });

    // Handle submenu triggers (like Admin Panel)
    const submenuTriggers = document.querySelectorAll('.submenu-trigger');
    submenuTriggers.forEach(trigger => {
        trigger.addEventListener('click', function(e) {
            e.preventDefault();
            const submenuId = this.dataset.submenu;
            const targetSubmenu = document.getElementById('submenu' + submenuId.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(''));
            const currentSubmenu = this.closest('.menu-submenu');

            if (targetSubmenu) {
                // Hide current submenu
                currentSubmenu.style.transform = 'translateX(-100%)';

                // Show target submenu
                targetSubmenu.classList.remove('hidden');
                setTimeout(() => {
                    targetSubmenu.style.transform = 'translateX(0)';
                }, 10);
            }
        });
    });

    // Currency switcher
    currencySwitcher.addEventListener('click', function(e) {
        e.preventDefault();
        const mainMenu = document.getElementById('menuMain');
        const currencySubmenu = document.getElementById('currencySubmenu');
        
        mainMenu.style.transform = 'translateX(-100%)';
        currencySubmenu.classList.remove('hidden');
        
        setTimeout(() => {
            currencySubmenu.style.transform = 'translateX(0)';
        }, 10);
    });

    // Account menu toggle
    const accountMenuToggle = document.getElementById('accountMenuToggle');
    if (accountMenuToggle) {
        accountMenuToggle.addEventListener('click', function(e) {
            e.preventDefault();
            const mainMenu = document.getElementById('menuMain');
            const accountSubmenu = document.getElementById('accountSubmenu');
            
            mainMenu.style.transform = 'translateX(-100%)';
            accountSubmenu.classList.remove('hidden');
            
            setTimeout(() => {
                accountSubmenu.style.transform = 'translateX(0)';
            }, 10);
        });
    }

    // Currency selection
    const currencyItems = document.querySelectorAll('#currencySubmenu .submenu-item');
    currencyItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const currency = this.dataset.currency;
            document.getElementById('currentCurrency').textContent = currency;
            
            // Close submenu
            const mainMenu = document.getElementById('menuMain');
            const currencySubmenu = document.getElementById('currencySubmenu');
            mainMenu.style.transform = 'translateX(0)';
            currencySubmenu.style.transform = 'translateX(100%)';
            
            setTimeout(() => {
                currencySubmenu.classList.add('hidden');
                currencySubmenu.style.transform = 'translateX(100%)';
            }, 300);
        });
    });

    // Mobile theme toggle
    if (mobileThemeToggle) {
        mobileThemeToggle.addEventListener('click', function(e) {
            e.preventDefault();
            const html = document.documentElement;
            const isDarkMode = html.classList.contains('light-mode');
            
            if (isDarkMode) {
                html.classList.remove('light-mode');
                localStorage.setItem('theme', 'dark');
                this.innerHTML = '<i class="fas fa-sun"></i> <span>Light Mode</span>';
            } else {
                html.classList.add('light-mode');
                localStorage.setItem('theme', 'light');
                this.innerHTML = '<i class="fas fa-moon"></i> <span>Dark Mode</span>';
            }
        });
        
        // Update button text on load
        const html = document.documentElement;
        if (html.classList.contains('light-mode')) {
            mobileThemeToggle.innerHTML = '<i class="fas fa-moon"></i> <span>Dark Mode</span>';
        } else {
            mobileThemeToggle.innerHTML = '<i class="fas fa-sun"></i> <span>Light Mode</span>';
        }
    }

    // Desktop theme toggle
    const desktopThemeToggle = document.getElementById('desktopThemeToggle');
    if (desktopThemeToggle) {
        desktopThemeToggle.addEventListener('click', function(e) {
            e.preventDefault();
            const html = document.documentElement;

            if (html.classList.contains('light-mode')) {
                html.classList.remove('light-mode');
                localStorage.setItem('theme', 'dark');
                this.innerHTML = '<i class="fas fa-sun"></i>';
            } else {
                html.classList.add('light-mode');
                localStorage.setItem('theme', 'light');
                this.innerHTML = '<i class="fas fa-moon"></i>';
            }
        });

        // Update icon on load
        const html = document.documentElement;
        if (html.classList.contains('light-mode')) {
            desktopThemeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        } else {
            desktopThemeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        }
    }

    // Desktop floating search toggle
    const desktopSearchToggle = document.getElementById('desktopSearchToggle');
    const floatingSearchBox = document.getElementById('floatingSearchBox');
    const floatingSearchInput = document.getElementById('floatingSearchInput');

    if (desktopSearchToggle && floatingSearchBox) {
        desktopSearchToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            floatingSearchBox.classList.toggle('active');
            desktopSearchToggle.classList.toggle('active');

            // Focus on input when opened
            if (floatingSearchBox.classList.contains('active') && floatingSearchInput) {
                setTimeout(() => floatingSearchInput.focus(), 100);
            }
        });

        // Close search box when clicking outside
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.desktop-search-container')) {
                floatingSearchBox.classList.remove('active');
                desktopSearchToggle.classList.remove('active');
            }
        });

        // Close on Escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && floatingSearchBox.classList.contains('active')) {
                floatingSearchBox.classList.remove('active');
                desktopSearchToggle.classList.remove('active');
            }
        });
    }
});

// ============================================
// 3. GLOBAL TOAST NOTIFICATION FUNCTION
// ============================================
function showToast(message, type = 'success') {
    // Get or create toast container
    let toastContainer = document.querySelector('.toast-container-custom');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container-custom';
        document.body.appendChild(toastContainer);
    }

    // Define icon and title based on type
    const config = {
        success: { icon: 'fa-check-circle', title: 'Success' },
        error: { icon: 'fa-times-circle', title: 'Error' },
        danger: { icon: 'fa-times-circle', title: 'Error' },
        warning: { icon: 'fa-exclamation-triangle', title: 'Warning' },
        info: { icon: 'fa-info-circle', title: 'Info' }
    };
    const { icon, title } = config[type] || config.info;

    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    toast.style.position = 'relative';

    toast.innerHTML = `
        <div class="toast-content">
            <div class="toast-header">
                <strong><i class="fas ${icon}"></i> ${title}</strong>
            </div>
            <div class="toast-body">${message}</div>
        </div>
        <button class="toast-close" aria-label="Close">
            <i class="fas fa-times"></i>
        </button>
        <div class="toast-progress">
            <div class="toast-progress-bar"></div>
        </div>
    `;

    toastContainer.appendChild(toast);

    // Store timeout ID for pause/resume functionality
    let timeoutId;
    let remainingTime = 2000;
    let startTime = Date.now();

    // Close button functionality
    const closeBtn = toast.querySelector('.toast-close');
    closeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        dismissToast();
    });

    // Pause on hover
    toast.addEventListener('mouseenter', () => {
        clearTimeout(timeoutId);
        remainingTime -= (Date.now() - startTime);
    });

    // Resume on mouse leave
    toast.addEventListener('mouseleave', () => {
        startTime = Date.now();
        timeoutId = setTimeout(dismissToast, remainingTime);
    });

    // Dismiss function
    function dismissToast() {
        toast.classList.add('toast-hiding');
        setTimeout(() => toast.remove(), 300);
    }

    // Auto-remove after 2 seconds
    timeoutId = setTimeout(dismissToast, 2000);
}

// ============================================
// 4. BACK TO TOP BUTTON
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    const backToTopBtn = document.getElementById('backToTopBtn');
    
    if (backToTopBtn) {
        // Show/hide button based on scroll position
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopBtn.classList.add('show');
            } else {
                backToTopBtn.classList.remove('show');
            }
        });
        
        // Scroll to top when clicked
        backToTopBtn.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
});

// ============================================
// 6. DISCOUNT BANNER FUNCTIONALITY
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    try {
        const discountBanner = document.getElementById('discountBanner');
        const navbar = document.querySelector('.navbar');
        const copyTooltip = document.getElementById('copyTooltip');
        const confettiCanvas = document.getElementById('confettiCanvas');

        if (!discountBanner) return;

        // Data attributes
        const isHighValue = discountBanner.dataset.highValue === 'true';

        // All offers data (safely parsed from JSON script tag)
        let allOffers = [];
        try {
            const offersDataEl = document.getElementById('discount-offers-data');
            if (offersDataEl) {
                allOffers = JSON.parse(offersDataEl.textContent || '[]');
            }
        } catch (jsonErr) {
            console.warn('Failed to parse discount offers JSON:', jsonErr);
        }

        // URL override for testing (kept for potential future use)
        // const forceShow = urlParams.get('show_discount_banner') === '1' || urlParams.get('show_discount_banner') === 'true';

        // ============================================
        // CLICK-TO-COPY FUNCTIONALITY (with robust fallback and feedback)
        // ============================================
        const initCopyToClipboard = function() {
            discountBanner.addEventListener('click', async function(e) {
                const codeElement = e.target.closest('.discount-code-text');
                if (!codeElement) return;

                e.preventDefault();
                e.stopPropagation();

                const code = codeElement.dataset.code || codeElement.textContent.trim();

                const showCopiedFeedback = function() {
                    // Show tooltip
                    if (copyTooltip) {
                        copyTooltip.classList.add('show');
                        setTimeout(() => {
                            copyTooltip.classList.remove('show');
                        }, 2000);
                    }

                    // Visual feedback on the code
                    codeElement.style.transform = 'scale(1.1)';
                    setTimeout(() => {
                        codeElement.style.transform = '';
                    }, 200);

                    // Global toast notification for clarity
                    try {
                        if (typeof showToast === 'function') {
                            showToast('Copied code: ' + code, 'success');
                        }
                    } catch (e) {
                        // No-op
                    }
                };

                // Try navigator.clipboard first (preferred)
                try {
                    if (navigator.clipboard && typeof navigator.clipboard.writeText === 'function') {
                        await navigator.clipboard.writeText(code);
                        showCopiedFeedback();
                        return;
                    }
                } catch (err) {
                    console.warn('navigator.clipboard.writeText failed:', err);
                }

                // Fallback to document.execCommand for older browsers / insecure contexts
                try {
                    const textarea = document.createElement('textarea');
                    textarea.value = code;
                    textarea.style.position = 'fixed'; // avoid scrolling to bottom
                    textarea.style.left = '-9999px';
                    textarea.setAttribute('aria-hidden', 'true');
                    document.body.appendChild(textarea);
                    textarea.focus();
                    textarea.select();

                    const successful = document.execCommand && document.execCommand('copy');
                    document.body.removeChild(textarea);

                    if (successful) {
                        showCopiedFeedback();
                        return;
                    } else {
                        console.warn('Fallback copy (execCommand) failed');
                    }
                } catch (err) {
                    console.warn('Fallback copy failed:', err);
                }

                // If copying failed, notify user
                try {
                    if (typeof showToast === 'function') {
                        showToast('Could not copy code to clipboard', 'warning');
                    } else {
                        alert('Could not copy code to clipboard. Code: ' + code);
                    }
                } catch (_) {}
            });
        };

        // ============================================
        // CONFETTI EFFECT FOR HIGH-VALUE DISCOUNTS
        // Implemented as a controller exposed at window.confettiController
        // so it can be started/stopped when offers change.
        // ============================================
        const initConfetti = function() {
            if (!confettiCanvas) return;

            const ctx = confettiCanvas.getContext('2d');
            let confettiPieces = [];
            const colors = ['#FF1493', '#FFD700', '#FF6B35', '#00CED1', '#9400D3', '#FF69B4'];
            let animationId = null;
            let running = false;

            class Confetti {
                constructor() {
                    this.reset();
                }

                reset() {
                    this.x = Math.random() * confettiCanvas.width;
                    this.y = -10;
                    this.size = Math.random() * 6 + 3;
                    this.speedY = Math.random() * 2 + 1;
                    this.speedX = (Math.random() - 0.5) * 2;
                    this.rotation = Math.random() * 360;
                    this.rotationSpeed = (Math.random() - 0.5) * 10;
                    this.color = colors[Math.floor(Math.random() * colors.length)];
                    this.opacity = 1;
                }

                update() {
                    this.y += this.speedY;
                    this.x += this.speedX;
                    this.rotation += this.rotationSpeed;
                    this.opacity -= 0.008;

                    if (this.y > confettiCanvas.height || this.opacity <= 0) {
                        this.reset();
                    }
                }

                draw() {
                    ctx.save();
                    ctx.translate(this.x, this.y);
                    ctx.rotate(this.rotation * Math.PI / 180);
                    ctx.globalAlpha = this.opacity;
                    ctx.fillStyle = this.color;
                    ctx.fillRect(-this.size / 2, -this.size / 2, this.size, this.size / 2);
                    ctx.restore();
                }
            }

            function resizeCanvas() {
                confettiCanvas.width = confettiCanvas.offsetWidth;
                confettiCanvas.height = confettiCanvas.offsetHeight;
            }

            function animate() {
                if (!running) return;
                ctx.clearRect(0, 0, confettiCanvas.width, confettiCanvas.height);
                confettiPieces.forEach(piece => {
                    piece.update();
                    piece.draw();
                });
                animationId = requestAnimationFrame(animate);
            }

            function startConfetti() {
                if (running) return;
                running = true;
                resizeCanvas();

                // If no pieces, create subtle particle rain
                if (confettiPieces.length === 0) {
                    for (let i = 0; i < 30; i++) {
                        const piece = new Confetti();
                        piece.y = Math.random() * confettiCanvas.height;
                        confettiPieces.push(piece);
                    }
                }

                animate();
            }

            function burstConfetti(count = 20) {
                // Generate all pieces first, then schedule them
                const pieces = [];
                for (let i = 0; i < count; i++) {
                    pieces.push({
                        delayTime: i * 30,
                        index: i
                    });
                }

                // Now schedule them with closures
                pieces.forEach((item) => {
                    setTimeout(() => {
                        const piece = new Confetti();
                        piece.x = confettiCanvas.width / 2;
                        piece.speedX = (Math.random() - 0.5) * 8;
                        piece.speedY = Math.random() * 3 + 2;
                        confettiPieces.push(piece);
                    }, item.delayTime);
                });
            }

            function stopConfetti() {
                running = false;
                if (animationId) {
                    cancelAnimationFrame(animationId);
                    animationId = null;
                }
                // Clear particles after a short delay so last frame fades out
                setTimeout(() => {
                    try { ctx.clearRect(0, 0, confettiCanvas.width, confettiCanvas.height); } catch (e) {}
                    confettiPieces = [];
                }, 200);
            }

            // Expose controller globally so cycling code can trigger it
            window.confettiController = {
                start: startConfetti,
                stop: stopConfetti,
                burst: burstConfetti,
                isRunning: () => running
            };

            // Initialize canvas size and optional auto-start if initial offer flagged
            resizeCanvas();
            if (isHighValue && window.confettiController) {
                window.confettiController.start();
                window.confettiController.burst();
            }

            // Handle resize
            window.addEventListener('resize', resizeCanvas);
        };

        // ============================================
        // AUTO-SCROLL BEHAVIOR (Hide on scroll down, show on scroll up)
        // ============================================
        const initScrollBehavior = function() {
            let lastScrollY = window.scrollY || 0;
            let ticking = false;
            let isHidden = false;

            function updateBannerVisibility() {
                const currentScrollY = window.scrollY || 0;
                const scrollThreshold = 100; // Start hiding after 100px scroll

                if (currentScrollY > scrollThreshold) {
                    // Scrolled past threshold - hide banner
                    if (!isHidden) {
                        discountBanner.classList.add('banner-hidden');
                        if (navbar) navbar.classList.add('banner-dismissed');
                        isHidden = true;
                    }
                } else {
                    // Near top - show banner
                    if (isHidden) {
                        discountBanner.classList.remove('banner-hidden');
                        if (navbar) navbar.classList.remove('banner-dismissed');
                        isHidden = false;
                    }
                }

                lastScrollY = currentScrollY;
                ticking = false;
            }

            // Run once on init to set the correct initial visibility (handles page loads where user starts scrolled)
            try { updateBannerVisibility(); } catch (e) {}

            window.addEventListener('scroll', function() {
                if (!ticking) {
                    requestAnimationFrame(updateBannerVisibility);
                    ticking = true;
                }
            }, { passive: true });

            // Ensure banner updates when user returns to the tab or window (visibility/focus changes)
            window.addEventListener('visibilitychange', function() { try { updateBannerVisibility(); } catch (e) {} });
            window.addEventListener('focus', function() { try { updateBannerVisibility(); } catch (e) {} });
        };

        // ============================================
        // REDUCED MOTION SUPPORT
        // ============================================
        const initReducedMotion = function() {
            if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
                discountBanner.classList.add('reduced-motion');
            }
        };

        // ============================================
        // INITIALIZE ALL FEATURES
        // ============================================
        initReducedMotion();
        initCopyToClipboard();
        initConfetti();
        initScrollBehavior();
    } catch (err) {
        console.error('Discount banner error:', err);
    }
});

// ============================================
// 7. CART DRAWER FUNCTIONS (Global)
// ============================================
function updateCartCount(count) {
    const badge = document.getElementById('cartCountBadge');
    if (badge) {
        badge.textContent = count;
        if (count > 0) {
            badge.classList.remove('badge-hidden');
        } else {
            badge.classList.add('badge-hidden');
        }
    }
}

function showCartDrawer(data) {
    // Check if cart drawer elements exist
    const itemImage = document.getElementById('cartDrawerItemImage');
    const itemName = document.getElementById('cartDrawerItemName');
    const itemVariant = document.getElementById('cartDrawerItemVariant');
    const itemQty = document.getElementById('cartDrawerItemQty');
    const itemPrice = document.getElementById('cartDrawerItemPrice');
    const subtotal = document.getElementById('cartDrawerSubtotal');
    const itemCount = document.getElementById('cartDrawerItemCount');
    const total = document.getElementById('cartDrawerTotal');
    const discountRow = document.getElementById('cartDrawerDiscountRow');
    const discountInput = document.getElementById('cartDrawerDiscountInput');
    const discountCode = document.getElementById('cartDrawerDiscountCode');
    const discountAmount = document.getElementById('cartDrawerDiscountAmount');
    const related = document.getElementById('cartDrawerRelated');
    const overlay = document.getElementById('cartDrawerOverlay');
    const drawer = document.getElementById('cartDrawer');

    // Update drawer with item details
    if (itemImage) {
        itemImage.src = data.item.image_url;
        itemImage.alt = data.item.name;
    }
    if (itemName) itemName.textContent = data.item.name;

    // Build variant text (handle missing size/color)
    if (itemVariant) {
        const variantParts = [];
        if (data.item.size) variantParts.push(data.item.size);
        if (data.item.color) variantParts.push(data.item.color);
        if (variantParts.length > 0) {
            itemVariant.textContent = variantParts.join(' / ');
            itemVariant.style.display = 'block';
        } else {
            itemVariant.style.display = 'none';
        }
    }

    if (itemQty) itemQty.textContent = `Qty: ${data.item.quantity}`;
    if (itemPrice) itemPrice.textContent = `€${data.item.total.toFixed(2)}`;

    // Update summary
    if (subtotal) subtotal.textContent = `€${data.cart_subtotal.toFixed(2)}`;
    if (itemCount) itemCount.textContent = data.cart_count;
    if (total) total.textContent = `€${data.cart_total.toFixed(2)}`;

    // Handle discount
    if (discountRow && discountInput && discountCode && discountAmount) {
        if (data.discount_code) {
            discountCode.textContent = data.discount_code;
            discountAmount.textContent = data.discount_amount.toFixed(2);
            discountRow.style.display = 'flex';
            discountInput.style.display = 'none';
        } else {
            discountRow.style.display = 'none';
            discountInput.style.display = 'block';
        }
    }

    // Calculate and show free shipping progress
    updateShippingProgress(data.cart_subtotal);

    // Populate related products carousel
    if (related) {
        if (data.related_products && data.related_products.length > 0) {
            populateRelatedProducts(data.related_products);
            related.style.display = 'block';
        } else {
            related.style.display = 'none';
        }
    }

    // Show the drawer
    if (overlay) overlay.classList.add('active');
    if (drawer) drawer.classList.add('active');
    document.body.classList.add('cart-drawer-open');
}

// Expose showCartDrawer to window scope
window.showCartDrawer = showCartDrawer;

// Generate star rating HTML
function generateStarRating(rating) {
    let html = '';
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;

    for (let i = 1; i <= 5; i++) {
        if (i <= fullStars) {
            html += '<i class="fas fa-star"></i>';
        } else if (i === fullStars + 1 && hasHalfStar) {
            html += '<i class="fas fa-star-half-alt"></i>';
        } else {
            html += '<i class="fas fa-star empty"></i>';
        }
    }
    return html;
}

// Populate related products carousel
function populateRelatedProducts(products) {
    const carousel = document.getElementById('cartDrawerCarousel');
    if (!carousel) return;
    
    carousel.innerHTML = '';

    products.forEach(product => {
        const card = document.createElement('div');
        card.className = 'cart-drawer-product-card';
        card.innerHTML = `
            <a href="${product.url}" class="cart-drawer-product-image">
                <img src="${product.image_url}" alt="${product.name}" loading="lazy">
                <button type="button" class="cart-drawer-quick-add"
                        data-product-id="${product.id}"
                        data-default-size="${product.default_size}"
                        data-default-color="${product.default_color}"
                        title="Quick add to cart"
                        onclick="event.preventDefault(); event.stopPropagation(); quickAddToCart(this);">
                    <i class="fas fa-shopping-cart"></i>
                </button>
            </a>
            <a href="${product.url}" class="cart-drawer-product-info">
                <h6 class="cart-drawer-product-name">${product.name}</h6>
                <div class="cart-drawer-product-rating">
                    <span class="cart-drawer-product-stars">${generateStarRating(product.rating)}</span>
                    <span class="cart-drawer-product-reviews">(${product.review_count})</span>
                </div>
                <span class="cart-drawer-product-price">€${product.price.toFixed(2)}</span>
            </a>
        `;
        carousel.appendChild(card);
    });

    // Initialize carousel buttons state
    updateCarouselButtons();
}

// Quick add to cart from carousel
window.quickAddToCart = function(button) {
    const productId = button.dataset.productId;
    const size = button.dataset.defaultSize;
    const color = button.dataset.defaultColor;

    // If no size/color, redirect to product page
    if (!size || !color) {
        const card = button.closest('.cart-drawer-product-card');
        const link = card.querySelector('a').href;
        window.location.href = link;
        return;
    }

    // Show loading state
    const originalHtml = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    button.disabled = true;

    // Get CSRF token (try form field, meta tag, then cookie)
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                      document.querySelector('meta[name="csrf-token"]')?.content ||
                      getCookie('csrftoken');

    fetch(`/cart/add/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `csrfmiddlewaretoken=${encodeURIComponent(csrfToken)}&size=${encodeURIComponent(size)}&color=${encodeURIComponent(color)}&quantity=1`
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

            // Show success state briefly
            button.innerHTML = '<i class="fas fa-check"></i>';
            button.classList.add('adding');

            // Update cart drawer totals
            document.getElementById('cartDrawerSubtotal').textContent = `€${data.cart_subtotal.toFixed(2)}`;
            document.getElementById('cartDrawerItemCount').textContent = data.cart_count;
            document.getElementById('cartDrawerTotal').textContent = `€${data.cart_total.toFixed(2)}`;
            updateShippingProgress(data.cart_subtotal);

            setTimeout(() => {
                button.innerHTML = originalHtml;
                button.classList.remove('adding');
                button.disabled = false;
            }, 1500);
        } else {
            button.innerHTML = originalHtml;
            button.disabled = false;
            if (typeof showToast === 'function') {
                showToast(data.message || 'Could not add to cart', 'error');
            }
        }
    })
    .catch(error => {
        console.error('Quick add error:', error);
        button.innerHTML = originalHtml;
        button.disabled = false;
    });
};

// Carousel navigation
function updateCarouselButtons() {
    const carousel = document.getElementById('cartDrawerCarousel');
    const prevBtn = document.getElementById('carouselPrev');
    const nextBtn = document.getElementById('carouselNext');

    if (!carousel || !prevBtn || !nextBtn) return;

    prevBtn.disabled = carousel.scrollLeft <= 0;
    nextBtn.disabled = carousel.scrollLeft >= carousel.scrollWidth - carousel.clientWidth - 5;
}

function scrollCarousel(direction) {
    const carousel = document.getElementById('cartDrawerCarousel');
    const cardWidth = 148; // card width + gap
    const scrollAmount = cardWidth * 2;

    carousel.scrollBy({
        left: direction === 'next' ? scrollAmount : -scrollAmount,
        behavior: 'smooth'
    });

    setTimeout(updateCarouselButtons, 350);
}

// Get CSRF cookie helper
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

function updateShippingProgress(subtotal) {
    const freeShippingThreshold = 50.00;
    const remaining = Math.max(0, freeShippingThreshold - subtotal);
    const percentage = Math.min(100, (subtotal / freeShippingThreshold) * 100);
    
    const shippingBar = document.getElementById('cartDrawerShippingBar');
    const shippingText = document.getElementById('cartDrawerShippingText');
    const shippingRemaining = document.getElementById('cartDrawerShippingRemaining');
    
    if (shippingBar) shippingBar.style.width = `${percentage}%`;
    if (shippingRemaining) shippingRemaining.textContent = `€${remaining.toFixed(2)}`;

    if (shippingText) {
        if (remaining === 0) {
            shippingText.innerHTML = '<i class="fas fa-check-circle text-success me-1"></i> Congrats! 🎉 You\'ve unlocked FREE SHIPPING';
        } else {
            shippingText.innerHTML = '<i class="fas fa-truck me-1"></i> Add <span id="cartDrawerShippingRemaining">€' + remaining.toFixed(2) + '</span> more for FREE shipping!';
        }
    }
}

function hideCartDrawer() {
    document.getElementById('cartDrawerOverlay').classList.remove('active');
    document.getElementById('cartDrawer').classList.remove('active');
    document.body.classList.remove('cart-drawer-open');
}

// ============================================
// 8. CART DRAWER & DISCOUNT CODE EVENT LISTENERS
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    // Cart drawer close functionality
    const cartDrawerClose = document.getElementById('cartDrawerClose');
    const cartDrawerContinue = document.getElementById('cartDrawerContinue');
    const cartDrawerOverlay = document.getElementById('cartDrawerOverlay');

    if (cartDrawerClose) {
        cartDrawerClose.addEventListener('click', hideCartDrawer);
    }

    if (cartDrawerContinue) {
        cartDrawerContinue.addEventListener('click', hideCartDrawer);
    }

    if (cartDrawerOverlay) {
        cartDrawerOverlay.addEventListener('click', hideCartDrawer);
    }

    // Carousel navigation
    const carouselPrev = document.getElementById('carouselPrev');
    const carouselNext = document.getElementById('carouselNext');
    const carousel = document.getElementById('cartDrawerCarousel');

    if (carouselPrev) {
        carouselPrev.addEventListener('click', () => scrollCarousel('prev'));
    }

    if (carouselNext) {
        carouselNext.addEventListener('click', () => scrollCarousel('next'));
    }

    if (carousel) {
        carousel.addEventListener('scroll', updateCarouselButtons);
    }

    // Close drawer on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && document.getElementById('cartDrawer').classList.contains('active')) {
            hideCartDrawer();
        }
    });

    // Discount code functionality
    const discountForm = document.getElementById('cartDrawerDiscountForm');
    const discountInput = document.getElementById('cartDrawerDiscountCodeInput');

    if (discountForm) {
        discountForm.addEventListener('submit', function(e) {
            e.preventDefault();
            applyDiscountCode();
        });
    }

    if (discountInput) {
        discountInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                applyDiscountCode();
            }
        });
    }
});

// Apply discount code function
function applyDiscountCode() {
    const discountInput = document.getElementById('cartDrawerDiscountCodeInput');
    const discountApplyBtn = document.getElementById('cartDrawerDiscountApply');
    
    const code = discountInput.value.trim().toUpperCase();
    
    if (!code) {
        showDiscountMessage('Please enter a discount code', 'error');
        return;
    }

    // Disable button and show loading
    discountApplyBtn.disabled = true;
    discountApplyBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    
    const csrfToken = getCookie('csrftoken');
    
    fetch('/checkout/apply-discount/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `csrfmiddlewaretoken=${encodeURIComponent(csrfToken)}&discount_code=${encodeURIComponent(code)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update cart totals
            document.getElementById('cartDrawerSubtotal').textContent = `€${data.cart_subtotal.toFixed(2)}`;
            document.getElementById('cartDrawerTotal').textContent = `€${data.cart_total.toFixed(2)}`;
            
            // Show discount row
            if (data.discount_code) {
                document.getElementById('cartDrawerDiscountCode').textContent = data.discount_code;
                document.getElementById('cartDrawerDiscountAmount').textContent = data.discount_amount.toFixed(2);
                document.getElementById('cartDrawerDiscountRow').style.display = 'flex';
                
                // Hide discount input after successful application
                document.getElementById('cartDrawerDiscountInput').style.display = 'none';
            }
            
            // Update shipping progress
            updateShippingProgress(data.cart_subtotal);
            
            // Clear input and show success
            discountInput.value = '';
            showDiscountMessage('Discount code applied successfully!', 'success');
            
            // Update cart count in header if needed
            if (typeof updateCartCount === 'function') {
                updateCartCount(data.cart_count);
            }
        } else {
            showDiscountMessage(data.message || 'Invalid discount code', 'error');
        }
    })
    .catch(error => {
        console.error('Discount application error:', error);
        showDiscountMessage('An error occurred. Please try again.', 'error');
    })
    .finally(() => {
        // Re-enable button
        discountApplyBtn.disabled = false;
        discountApplyBtn.innerHTML = '<i class="fas fa-tag"></i> Apply';
    });
}

// Show discount message
function showDiscountMessage(message, type) {
    const discountMessage = document.getElementById('cartDrawerDiscountMessage');
    discountMessage.textContent = message;
    discountMessage.className = `cart-drawer-discount-message ${type}`;
    discountMessage.style.display = 'block';
    
    // Hide after 3 seconds
    setTimeout(() => {
        discountMessage.style.display = 'none';
    }, 3000);
}

// ============================================
// GLOBAL CART COUNT UPDATE FUNCTION
// ============================================
/**
 * Update cart badge count across all pages
 * Used by product detail page and other pages that add items to cart
 * @param {number} count - New cart item count
 */
window.updateCartCount = function(count) {
    // Update all cart badges on the page (mobile and desktop)
    const badges = document.querySelectorAll('.cart-count-badge');
    badges.forEach(badge => {
        badge.textContent = count;
        if (count > 0) {
            badge.classList.remove('badge-hidden');
        } else {
            badge.classList.add('badge-hidden');
        }
    });
};

// ============================================
// DATA ATTRIBUTE STYLE HANDLERS
// (Replaces inline styles for Code Institute compliance)
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    // 1. Apply background images from data attributes (home page collections)
    document.querySelectorAll('[data-bg-image]').forEach(el => {
        const bgImage = el.dataset.bgImage;
        if (bgImage) {
            el.style.backgroundImage = `url('${bgImage}')`;
            el.style.backgroundSize = 'cover';
            el.style.backgroundPosition = 'center';
        }
    });

    // 2. Apply gradients from data attributes (seasonal theme strips)
    document.querySelectorAll('[data-gradient]').forEach(el => {
        const gradient = el.dataset.gradient;
        if (gradient) {
            el.style.background = gradient;
        }
    });

    // 3. Apply progress bar widths from data attributes (product review stats)
    document.querySelectorAll('.progress-bar[data-width]').forEach(bar => {
        const width = bar.dataset.width;
        if (width) {
            bar.style.width = width + '%';
        }
    });
});
