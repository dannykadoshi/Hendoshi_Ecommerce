/**
 * Seasonal Themes - JavaScript Particle Engine
 * Creates and manages animated particles for seasonal themes
 */

const SeasonalThemes = {
    // Configuration
    config: {
        theme: 'everyday',
        speed: 'normal',
        density: 'medium',
        isPaused: false
    },

    // State
    particles: [],
    containers: [],
    animationId: null,
    isInitialized: false,

    // Density map - number of particles per container
    densityMap: {
        light: 12,
        medium: 25,
        heavy: 45
    },

    // Speed multiplier for animations
    speedMap: {
        slow: 0.5,
        normal: 1,
        fast: 2
    },

    // Theme configurations with particles, colors, and animation types
    themeConfigs: {
        new_years: {
            particles: ['🎆', '✨', '🍾', '🎊', '⭐', '🥂'],
            colors: ['gold', 'silver'],
            animations: ['sparkle', 'burst', 'bubble'],
            weights: [3, 3, 2, 2, 1, 1]
        },
        valentines: {
            particles: ['❤️', '💕', '💗', '💖', '🌹', '💝'],
            colors: ['pink', 'red'],
            animations: ['heart', 'petal'],
            weights: [3, 2, 2, 2, 1, 1]
        },
        st_patricks: {
            particles: ['☘️', '🍀', '💰', '🌈', '🪙', '⭐'],
            colors: ['light-green', 'dark-green', 'gold'],
            animations: ['shamrock', 'gold', 'rainbow'],
            weights: [3, 3, 2, 1, 2, 1]
        },
        mothers_day: {
            particles: ['🌸', '🦋', '💐', '💜', '🌷', '🌺'],
            colors: ['pink', 'purple', 'lavender'],
            animations: ['flower', 'butterfly'],
            weights: [2, 2, 2, 1, 2, 2]
        },
        fathers_day: {
            particles: ['🔧', '👔', '⭐', '🏆', '🎯', '⚡'],
            colors: ['navy', 'silver', 'charcoal'],
            animations: ['tie', 'tool', 'star'],
            weights: [2, 2, 2, 1, 1, 1]
        },
        fourth_july: {
            particles: ['🎆', '⭐', '🎇', '✨', '🇺🇸', '💥'],
            colors: ['red', 'white', 'blue'],
            animations: ['firework', 'star', 'sparkle'],
            weights: [3, 3, 2, 2, 1, 1]
        },
        rock_n_roll: {
            particles: ['🎸', '⚡', '🤘', '🎵', '💀', '🔥'],
            colors: ['electric-purple', 'hot-pink', 'neon-blue'],
            animations: ['guitar', 'lightning', 'note', 'skull'],
            weights: [2, 3, 2, 2, 2, 1]
        },
        thanksgiving: {
            particles: ['🍂', '🍁', '🦃', '🌾', '🌻', '🥧'],
            colors: ['orange', 'red', 'gold', 'brown', 'yellow'],
            animations: ['leaf', 'wheat', 'acorn'],
            weights: [3, 3, 1, 2, 1, 1]
        },
        christmas: {
            particles: ['❄️', '🎄', '⭐', '🔔', '🎁', '🎅'],
            colors: ['red', 'green', 'gold', 'silver'],
            animations: ['snowflake', 'ornament', 'light', 'star'],
            weights: [4, 2, 2, 1, 1, 1]
        },
        everyday: {
            particles: ['💀', '🦇', '🔥', '⚡', '☠️', '🖤'],
            colors: ['blood-red', 'dark-purple', 'neon-pink', 'shadow'],
            animations: ['skull', 'bat', 'flame', 'lightning', 'pentagram'],
            weights: [3, 2, 2, 2, 1, 1]
        },
        celebration: {
            particles: ['🎉', '🎊', '✨', '⭐', '🎈', '💫'],
            colors: ['confetti-pink', 'confetti-gold', 'confetti-cyan', 'confetti-purple', 'confetti-orange'],
            animations: ['confetti', 'sparkle', 'burst', 'float'],
            weights: [3, 3, 2, 2, 1, 1]
        }
    },

    /**
     * Initialize the seasonal themes system
     */
    init: function(options = {}) {
        // Merge options with defaults
        this.config = { ...this.config, ...options };

        // Find all vault-hero or page-hero sections
        this.setupContainers();

        // Create particles for each container
        this.createParticles();

        // Start animation if not paused
        if (!this.config.isPaused) {
            this.startAnimation();
        }

        this.isInitialized = true;
        console.log(`[SeasonalThemes] Initialized with theme: ${this.config.theme}`);
    },

    /**
     * Set up animation containers in vault-hero sections
     */
    setupContainers: function() {
        const heroes = document.querySelectorAll('.page-hero, .vault-hero');

        heroes.forEach((hero) => {
            // Add theme-active class if not already present
            hero.classList.add('theme-active');
            hero.classList.add(`theme-speed-${this.config.speed}`);

            if (this.config.isPaused) {
                hero.classList.add('theme-paused');
            }

            // Create animation layer if it doesn't exist
            let layer = hero.querySelector('.theme-animation-layer');
            if (!layer) {
                layer = document.createElement('div');
                layer.className = 'theme-animation-layer';
                layer.setAttribute('data-theme', this.config.theme);
                hero.insertBefore(layer, hero.firstChild);
            }

            this.containers.push(layer);
        });
    },

    /**
     * Create particles for all containers
     */
    createParticles: function() {
        const themeConfig = this.themeConfigs[this.config.theme];
        if (!themeConfig) {
            console.warn(`[SeasonalThemes] Unknown theme: ${this.config.theme}`);
            return;
        }

        const particleCount = this.densityMap[this.config.density];

        this.containers.forEach(container => {
            for (let i = 0; i < particleCount; i++) {
                this.createParticle(container, themeConfig);
            }
        });
    },

    /**
     * Create a single particle
     */
    createParticle: function(container, themeConfig) {
        const particle = document.createElement('span');
        particle.className = `theme-particle ${this.config.theme}`;

        // Select random particle based on weights
        const particleEmoji = this.weightedRandom(themeConfig.particles, themeConfig.weights);
        particle.textContent = particleEmoji;

        // Add random color class
        const colorClass = themeConfig.colors[Math.floor(Math.random() * themeConfig.colors.length)];
        particle.classList.add(colorClass);

        // Add random animation class
        const animClass = themeConfig.animations[Math.floor(Math.random() * themeConfig.animations.length)];
        particle.classList.add(animClass);

        // Random positioning
        particle.style.left = `${Math.random() * 100}%`;
        particle.style.top = `${Math.random() * 100}%`;

        // Random size variation
        const baseSize = 1 + Math.random() * 0.8;
        particle.style.fontSize = `${baseSize}rem`;

        // Random animation delay (stagger particle appearances)
        const delay = Math.random() * 8;
        particle.style.animationDelay = `${delay}s`;

        // Adjust animation duration based on speed
        const baseDuration = 6 / this.speedMap[this.config.speed];
        const duration = baseDuration + (Math.random() * 4);
        particle.style.animationDuration = `${duration}s`;

        container.appendChild(particle);
        this.particles.push(particle);
    },

    /**
     * Weighted random selection
     */
    weightedRandom: function(items, weights) {
        const totalWeight = weights.reduce((sum, w) => sum + w, 0);
        let random = Math.random() * totalWeight;

        for (let i = 0; i < items.length; i++) {
            random -= weights[i];
            if (random <= 0) {
                return items[i];
            }
        }

        return items[items.length - 1];
    },

    /**
     * Start animations
     */
    startAnimation: function() {
        this.config.isPaused = false;

        document.querySelectorAll('.page-hero, .vault-hero').forEach(hero => {
            hero.classList.remove('theme-paused');
        });

        this.containers.forEach(layer => {
            layer.classList.remove('paused');
        });
    },

    /**
     * Pause animations
     */
    pauseAnimation: function() {
        this.config.isPaused = true;

        document.querySelectorAll('.page-hero, .vault-hero').forEach(hero => {
            hero.classList.add('theme-paused');
        });

        this.containers.forEach(layer => {
            layer.classList.add('paused');
        });
    },

    /**
     * Toggle animation state
     */
    toggleAnimation: function() {
        if (this.config.isPaused) {
            this.startAnimation();
        } else {
            this.pauseAnimation();
        }
    },

    /**
     * Destroy all particles and reset
     */
    destroy: function() {
        // Remove all particles
        this.particles.forEach(particle => {
            if (particle.parentNode) {
                particle.parentNode.removeChild(particle);
            }
        });
        this.particles = [];

        // Remove animation layers
        this.containers.forEach(layer => {
            if (layer.parentNode) {
                layer.parentNode.removeChild(layer);
            }
        });
        this.containers = [];

        // Remove classes from vault-heroes
        document.querySelectorAll('.page-hero, .vault-hero').forEach(hero => {
            hero.classList.remove('theme-active', 'theme-paused');
            hero.classList.remove('theme-speed-slow', 'theme-speed-normal', 'theme-speed-fast');
        });

        this.isInitialized = false;
    },

    /**
     * Change theme dynamically
     */
    changeTheme: function(newTheme) {
        if (this.themeConfigs[newTheme]) {
            this.destroy();
            this.config.theme = newTheme;
            this.init(this.config);
        } else {
            console.warn(`[SeasonalThemes] Unknown theme: ${newTheme}`);
        }
    },

    /**
     * Update configuration
     */
    updateConfig: function(options) {
        const needsRestart = options.theme !== this.config.theme ||
                            options.density !== this.config.density;

        this.config = { ...this.config, ...options };

        if (needsRestart && this.isInitialized) {
            this.destroy();
            this.init(this.config);
        } else {
            // Just update speed classes
            document.querySelectorAll('.page-hero, .vault-hero').forEach(hero => {
                hero.classList.remove('theme-speed-slow', 'theme-speed-normal', 'theme-speed-fast');
                hero.classList.add(`theme-speed-${this.config.speed}`);
            });
        }
    }
};

// Auto-initialize if seasonal theme data is present in DOM
document.addEventListener('DOMContentLoaded', function() {
    // Check for theme initialization data
    const themeData = document.querySelector('[data-seasonal-theme]');
    if (themeData) {
        SeasonalThemes.init({
            theme: themeData.dataset.seasonalTheme,
            speed: themeData.dataset.themeSpeed || 'normal',
            density: themeData.dataset.themeDensity || 'medium',
            isPaused: themeData.dataset.themePaused === 'true'
        });
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SeasonalThemes;
}
