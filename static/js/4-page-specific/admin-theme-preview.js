/* ================================================
   HENDOSHI - ADMIN THEME PREVIEW
   ================================================

   Purpose: Initialises the seasonal theme animation on the admin
   theme preview page. Reads theme configuration from data-* attributes
   on <body>, calls SeasonalThemes.init(), and wires the play/pause
   toggle button and the restart button for live preview control.

   Contains:
   - DOMContentLoaded init: reads body.dataset and calls SeasonalThemes.init()
   - Play/pause toggle button handler
   - Restart animation button handler

   Dependencies: seasonal_themes.js (SeasonalThemes global)
   Load Order: Load after seasonal_themes.js on the theme preview page
   ================================================ */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the theme animation for preview
    const themeType = document.body.dataset.themeType;
    const animSpeed = document.body.dataset.animSpeed;
    const density = document.body.dataset.density;
    const isPausedData = document.body.dataset.isPaused === 'true';

    if (typeof SeasonalThemes !== 'undefined' && themeType) {
        SeasonalThemes.init({
            theme: themeType,
            speed: animSpeed,
            density: density,
            isPaused: isPausedData
        });
    }

    // Preview controls
    let isPaused = isPausedData;
    const toggleBtn = document.getElementById('toggleAnimation');
    const toggleIcon = document.getElementById('toggleIcon');
    const restartBtn = document.getElementById('restartAnimation');

    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            isPaused = !isPaused;
            if (isPaused) {
                toggleIcon.className = 'fas fa-play';
                if (typeof SeasonalThemes !== 'undefined') {
                    SeasonalThemes.pauseAnimation();
                }
            } else {
                toggleIcon.className = 'fas fa-pause';
                if (typeof SeasonalThemes !== 'undefined') {
                    SeasonalThemes.startAnimation();
                }
            }
        });
    }

    if (restartBtn) {
        restartBtn.addEventListener('click', function() {
            if (typeof SeasonalThemes !== 'undefined') {
                SeasonalThemes.destroy();
                SeasonalThemes.init({
                    theme: themeType,
                    speed: animSpeed,
                    density: density,
                    isPaused: false
                });
                isPaused = false;
                toggleIcon.className = 'fas fa-pause';
            }
        });
    }
});
