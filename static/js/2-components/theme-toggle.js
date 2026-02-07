/* ================================================
   HENDOSHI - THEME TOGGLE
   ================================================
   
   Purpose: JavaScript functionality for theme toggle
   
   Contains:
   - Event handlers
   - User interactions
   - Dynamic functionality
   
   Dependencies: utils.js (typically)
   Load Order: Load as needed for specific pages
   ================================================ */

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

