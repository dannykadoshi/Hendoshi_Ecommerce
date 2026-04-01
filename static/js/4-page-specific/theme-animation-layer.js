/* ================================================
   HENDOSHI - THEME ANIMATION LAYER
   ================================================

   Purpose: Reads seasonal theme configuration from body data attributes and
            activates the particle animation system on .page-hero and .vault-hero elements

   Contains:
   - Reads data-seasonal-theme, data-seasonal-speed, data-seasonal-density, data-seasonal-paused from <body>
   - Applies .theme-active and .theme-speed-{speed} CSS classes to hero containers
   - Calls SeasonalThemes.init() from seasonal_themes.js if a theme is active

   Dependencies: seasonal_themes.js (SeasonalThemes global)
   Load Order: Load on all pages after seasonal_themes.js
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
