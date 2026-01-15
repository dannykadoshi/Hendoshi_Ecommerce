// HENDOSHI Base JavaScript

// Theme Toggle Functionality
document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('themeToggle');
    const htmlElement = document.documentElement;
    
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

// Auto-dismiss messages after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        let alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            let bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
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