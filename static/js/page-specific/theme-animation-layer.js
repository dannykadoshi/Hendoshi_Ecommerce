/**
 * Theme Animation Layer Scripts
 * Initializes seasonal theme animations on vault-hero sections
 */

document.addEventListener('DOMContentLoaded', function() {
    const themeType = document.body.dataset.seasonalTheme;
    const animSpeed = document.body.dataset.seasonalSpeed;
    const density = document.body.dataset.seasonalDensity;
    const isPaused = document.body.dataset.seasonalPaused === 'true';

    if (themeType) {
        const heroes = document.querySelectorAll('.vault-hero');
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
