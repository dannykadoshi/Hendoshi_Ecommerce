/* ================================================
   HENDOSHI - ADMIN THEME FORM
   ================================================

   Purpose: Drives the admin seasonal theme configuration form — live theme
            preview descriptions and conditional message strip settings visibility

   Contains:
   - updateThemePreview() — shows emoji and description for the selected theme type in #themeTypePreview
   - themeDescriptions map for all 11 seasonal theme types
   - toggleStripSettings() — shows/hides #stripSettingsContainer based on #id_show_message_strip checkbox
   - Strip preview visibility toggle via .strip-preview-hidden CSS class on checkbox change

   Dependencies: None (vanilla JS)
   Load Order: Load on admin theme management form page only
   ================================================ */

document.addEventListener('DOMContentLoaded', function() {
    const themeDescriptions = {
        'new_years': { emoji: '🎆✨', desc: 'Gold/silver confetti, champagne bubbles, and firework sparkles' },
        'valentines': { emoji: '❤️💕', desc: 'Floating hearts and rose petals with soft pink glow' },
        'st_patricks': { emoji: '☘️🍀', desc: 'Shamrocks, gold coins, and rainbow accents' },
        'mothers_day': { emoji: '🌸🦋', desc: 'Delicate flower petals and butterflies' },
        'fathers_day': { emoji: '🔧👔', desc: 'Subtle geometric shapes with navy/gray tones' },
        'fourth_july': { emoji: '🎆⭐', desc: 'Fireworks and stars in red, white, and blue' },
        'rock_n_roll': { emoji: '🎸⚡', desc: 'Guitar picks, lightning bolts, and musical notes' },
        'thanksgiving': { emoji: '🍂🍁', desc: 'Autumn leaves and warm harvest colors' },
        'christmas': { emoji: '❄️🎄', desc: 'Snowflakes, ornaments, and twinkling lights' },
        'everyday': { emoji: '💀🦇', desc: 'Skulls, flames, bats, and dark gothic vibes' },
        'celebration': { emoji: '🎉🎊', desc: 'Colorful confetti, sparkles, and party vibes' }
    };

    const themeTypeSelect = document.getElementById('id_theme_type');
    const previewDiv = document.getElementById('themeTypePreview');
    const emojiSpan = document.getElementById('themeEmoji');
    const descSpan = document.getElementById('themeDescription');

    function updateThemePreview() {
        if (!themeTypeSelect) return;
        
        const selectedType = themeTypeSelect.value;
        if (selectedType && themeDescriptions[selectedType]) {
            const info = themeDescriptions[selectedType];
            emojiSpan.textContent = info.emoji;
            descSpan.textContent = info.desc;
            previewDiv.style.display = 'flex';
        } else {
            previewDiv.style.display = 'none';
        }
    }

    if (themeTypeSelect) {
        themeTypeSelect.addEventListener('change', updateThemePreview);
        updateThemePreview();
    }

    // Message Strip toggle functionality
    const showStripCheckbox = document.getElementById('id_show_message_strip');
    const stripSettingsContainer = document.getElementById('stripSettingsContainer');

    if (showStripCheckbox && stripSettingsContainer) {
        const toggleStripSettings = function() {
            if (showStripCheckbox.checked) {
                stripSettingsContainer.style.display = 'block';
            } else {
                stripSettingsContainer.style.display = 'none';
            }
        };

        showStripCheckbox.addEventListener('change', toggleStripSettings);
        toggleStripSettings();
    }

    // Strip Preview Display Toggle
    // Handles showing/hiding the strip preview using CSS class instead of inline style
    const stripPreview = document.getElementById('stripPreview');
    if (stripPreview && stripSettingsContainer) {
        // MutationObserver removed - using event listener instead
        
        if (showStripCheckbox) {
            showStripCheckbox.addEventListener('change', function() {
                if (this.checked) {
                    stripPreview.classList.remove('strip-preview-hidden');
                } else {
                    stripPreview.classList.add('strip-preview-hidden');
                }
            });
        }
    }
});
