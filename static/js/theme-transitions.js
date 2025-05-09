/**
 * Theme Transitions Utility
 * Provides animation utilities for smoother theme transitions
 */

// Create a global namespace for our theme utilities
window.AstroBotTheme = window.AstroBotTheme || {};

/**
 * Theme transition utilities
 */
AstroBotTheme.transitions = {
    /**
     * Adds a transition effect to an element or the entire body
     * @param {HTMLElement|null} element - Element to transition, defaults to document.body
     * @param {number} duration - Transition duration in milliseconds
     * @returns {Promise} - Resolves when transition is complete
     */
    addTransition: function(element = null, duration = 400) {
        const target = element || document.body;
        
        return new Promise(resolve => {
            // Add the transition class
            target.classList.add('theme-transition');
            
            // Wait for the transition to complete
            setTimeout(() => {
                target.classList.remove('theme-transition');
                resolve();
            }, duration);
        });
    },
    
    /**
     * Perform a theme change with a crossfade animation
     * @param {string} newTheme - The new theme to apply
     * @param {number} duration - Animation duration in milliseconds
     */
    crossfade: function(newTheme, duration = 600) {
        // Create an overlay for the animation
        const overlay = document.createElement('div');
        overlay.className = 'theme-transition-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(0, 0, 0, 0.3);
            z-index: 9999;
            opacity: 0;
            pointer-events: none;
            transition: opacity ${duration / 2}ms ease-in-out;
        `;
        
        document.body.appendChild(overlay);
        
        // Fade in the overlay
        setTimeout(() => {
            overlay.style.opacity = '1';
        }, 10);
        
        // Change theme once overlay is visible
        setTimeout(() => {
            // Remove existing theme classes
            document.body.classList.remove('light', 'dark', 'theme-space', 'theme-neon', 'theme-contrast');
            
            // Apply new theme
            if (newTheme === 'light') {
                document.body.classList.add('light');
            } else if (newTheme.startsWith('theme-')) {
                document.body.classList.add('dark');
                document.body.classList.add(newTheme);
            } else {
                document.body.classList.add('dark');
            }
            
            // Update the data attribute
            document.body.setAttribute('data-theme', newTheme);
            
            // Start fading out the overlay
            overlay.style.opacity = '0';
            
            // Remove overlay once animation is complete
            setTimeout(() => {
                document.body.removeChild(overlay);
            }, duration / 2);
        }, duration / 2);
    },
    
    /**
     * Apply a wipe animation during theme change
     * @param {string} direction - Direction of wipe: 'left', 'right', 'up', 'down'
     * @param {string} newTheme - The new theme to apply
     * @param {number} duration - Animation duration in milliseconds
     */
    wipe: function(direction, newTheme, duration = 800) {
        // Set starting position based on direction
        let startPosition;
        switch (direction) {
            case 'left':
                startPosition = 'translateX(100%)';
                break;
            case 'right':
                startPosition = 'translateX(-100%)';
                break;
            case 'up':
                startPosition = 'translateY(100%)';
                break;
            case 'down':
                startPosition = 'translateY(-100%)';
                break;
            default:
                startPosition = 'translateX(100%)';
        }
        
        // Create the wipe element
        const wipe = document.createElement('div');
        wipe.className = 'theme-wipe-overlay';
        wipe.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: 9999;
            background-color: var(--primary-bg);
            transform: ${startPosition};
            transition: transform ${duration}ms cubic-bezier(0.65, 0, 0.35, 1);
            pointer-events: none;
        `;
        
        // Apply the new theme to the wipe element
        if (newTheme === 'light') {
            wipe.classList.add('light');
        } else if (newTheme.startsWith('theme-')) {
            wipe.classList.add('dark');
            wipe.classList.add(newTheme);
        } else {
            wipe.classList.add('dark');
        }
        
        document.body.appendChild(wipe);
        
        // Trigger the wipe animation
        setTimeout(() => {
            wipe.style.transform = 'translate(0)';
        }, 10);
        
        // Change the theme once wipe completes
        setTimeout(() => {
            // Remove existing theme classes
            document.body.classList.remove('light', 'dark', 'theme-space', 'theme-neon', 'theme-contrast');
            
            // Apply new theme
            if (newTheme === 'light') {
                document.body.classList.add('light');
            } else if (newTheme.startsWith('theme-')) {
                document.body.classList.add('dark');
                document.body.classList.add(newTheme);
            } else {
                document.body.classList.add('dark');
            }
            
            // Update the data attribute
            document.body.setAttribute('data-theme', newTheme);
            
            // Remove the wipe element
            document.body.removeChild(wipe);
        }, duration + 50);
    }
};

// Add simpler aliases for commonly used transitions
AstroBotTheme.fade = function(newTheme) {
    return AstroBotTheme.transitions.crossfade(newTheme);
};

AstroBotTheme.wipeRight = function(newTheme) {
    return AstroBotTheme.transitions.wipe('right', newTheme);
};