/* ================================================
   HENDOSHI - THEME ANIMATION LAYER
   ================================================
   
   Purpose: JavaScript functionality for theme animation layer
   
   Contains:
   - Event handlers
   - User interactions
   - Dynamic functionality
   
   Dependencies: utils.js (typically)
   Load Order: Load as needed for specific pages
   ================================================ */

document.addEventListener('DOMContentLoaded', function() {
    const themeType = document.body.dataset.seasonalTheme;
    const animSpeed = document.body.dataset.seasonalSpeed;
    const density = document.body.dataset.seasonalDensity;
    const isPaused = document.body.dataset.seasonalPaused === 'true';

    if (themeType) {
        const heroes = document.querySelectorAll('.page-hero, .vault-hero');
        heroes.forEach(function(hero) {
            hero.classList.add('theme-active');
            hero.classList.add('theme-speed-' + animSpeed);
            if (isPaused) {
                hero.classList.add('theme-paused');
            }
        });

        if (typeof SeasonalThemes !== 'undefined') {
            SeasonalThemes.init({
                theme: themeType,
                speed: animSpeed,
                density: density,
                isPaused: isPaused
            });
        }
    }
});
