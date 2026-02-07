/* ================================================
   HENDOSHI - NAVIGATION DROPDOWN
   ================================================
   
   Purpose: JavaScript functionality for navigation dropdown
   
   Contains:
   - Event handlers
   - User interactions
   - Dynamic functionality
   
   Dependencies: utils.js (typically)
   Load Order: Load as needed for specific pages
   ================================================ */

// Dropdown hover behavior for desktop
document.addEventListener('DOMContentLoaded', function() {
    // Phase 3: Add --item-index CSS variables to animated menu items
    const animatedItems = document.querySelectorAll('.menu-item-animate, .submenu-item-animate');
    animatedItems.forEach((item) => {
        // Get parent menu to calculate index within that specific menu
        const parentMenu = item.closest('.menu-submenu, .mobile-menu-content');
        if (parentMenu) {
            const siblings = parentMenu.querySelectorAll(item.classList.contains('menu-item-animate') ? '.menu-item-animate' : '.submenu-item-animate');
            const localIndex = Array.from(siblings).indexOf(item);
            item.style.setProperty('--item-index', localIndex);
        }
    });
    
    // Desktop dropdown hover behavior
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

                        // Ensure toggle loses focus so focus styles (blue outline) do not persist after hiding
                        try { toggleBtn.blur(); } catch(e) {}

                        // Also blur the activeElement if it is inside this dropdown to be extra-safe
                        try {
                            if (document.activeElement && dropdown.contains(document.activeElement)) {
                                document.activeElement.blur();
                            }
                        } catch(e) {}
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

        // Make non-dropdown links behave like dropdown toggles visually and close any open dropdowns when hovered
        const nonDropdownLinks = document.querySelectorAll('.desktop-menu .nav-item:not(.dropdown) .nav-link');
        nonDropdownLinks.forEach(link => {
            link.addEventListener('mouseenter', function() {
                // Hide any open dropdowns in the desktop menu
                const openMenus = document.querySelectorAll('.desktop-menu .dropdown-menu.show');
                openMenus.forEach(menu => {
                    const parent = menu.closest('.dropdown');
                    if (parent) {
                        const toggleBtn = parent.querySelector('.dropdown-toggle');
                        const instance = bootstrap.Dropdown.getInstance(toggleBtn);
                        if (instance) {
                            instance.hide();
                        }

                        // Remove focus from the toggle so it doesn't keep the blue focus ring
                        try { toggleBtn.blur(); } catch(e) {}

                        // Also blur the activeElement if it's inside the desktop menu to ensure no focus ring remains
                        try {
                            const desktopMenuEl = document.querySelector('.desktop-menu');
                            if (document.activeElement && desktopMenuEl && desktopMenuEl.contains(document.activeElement)) {
                                document.activeElement.blur();
                            }
                        } catch(e) {}
                    }
                });

                // Add blue-focus class for visual parity
                link.classList.add('nav-link-blue-focus');
                // Remove it from other links (just in case)
                document.querySelectorAll('.desktop-menu .nav-link.nav-link-blue-focus').forEach(l => {
                    if (l !== link) l.classList.remove('nav-link-blue-focus');
                });
            });

            link.addEventListener('mouseleave', function() {
                link.classList.remove('nav-link-blue-focus');
            });
        });

        // Clear any lingering states when leaving the desktop menu
        const desktopMenu = document.querySelector('.desktop-menu');
        if (desktopMenu) {
            desktopMenu.addEventListener('mouseleave', function() {
                // remove blue-focus from all links
                document.querySelectorAll('.desktop-menu .nav-link.nav-link-blue-focus').forEach(l => l.classList.remove('nav-link-blue-focus'));

                // hide any open dropdowns
                const openMenus = document.querySelectorAll('.desktop-menu .dropdown-menu.show');
                openMenus.forEach(menu => {
                    const parent = menu.closest('.dropdown');
                    if (parent) {
                        const toggleBtn = parent.querySelector('.dropdown-toggle');
                        const instance = bootstrap.Dropdown.getInstance(toggleBtn);
                        if (instance) {
                            instance.hide();
                        }

                        // Clear focus so the blue outline doesn't remain on the toggle
                        try { toggleBtn.blur(); } catch(e) {}

                        // And blur the activeElement if it's within the desktop menu
                        try {
                            const desktopMenuEl = document.querySelector('.desktop-menu');
                            if (document.activeElement && desktopMenuEl && desktopMenuEl.contains(document.activeElement)) {
                                document.activeElement.blur();
                            }
                        } catch(e) {}
                    }
                });
            });
        }
    }
});

