/**
 * Theme Transitions Module
 * Enhanced animations and transitions for theme switching
 */

/**
 * Creates a smooth transition effect when switching themes
 * @param {string} fromTheme - The name of the theme being switched from
 * @param {string} toTheme - The name of the theme being switched to
 */
function createThemeTransition(fromTheme, toTheme) {
    // Create overlay for transition effect
    const overlay = document.createElement('div');
    overlay.id = 'theme-transition-overlay';
    overlay.style.position = 'fixed';
    overlay.style.top = '0';
    overlay.style.left = '0';
    overlay.style.width = '100%';
    overlay.style.height = '100%';
    overlay.style.backgroundColor = getTransitionColor(fromTheme, toTheme);
    overlay.style.zIndex = '9999';
    overlay.style.opacity = '0';
    overlay.style.pointerEvents = 'none';
    overlay.style.transition = 'opacity 0.4s ease';
    document.body.appendChild(overlay);
    
    // Execute the transition animation
    requestAnimationFrame(() => {
        overlay.style.opacity = '0.25';
        
        setTimeout(() => {
            overlay.style.opacity = '0';
            
            setTimeout(() => {
                overlay.remove();
            }, 400);
        }, 200);
    });
}

/**
 * Determine the appropriate transition color based on themes
 * @param {string} fromTheme - Current theme
 * @param {string} toTheme - Target theme
 * @returns {string} - CSS color value for transition
 */
function getTransitionColor(fromTheme, toTheme) {
    // Special transitions for premium themes
    if (toTheme === 'space') {
        return 'rgba(0, 0, 50, 0.3)';
    } else if (toTheme === 'neon') {
        return 'rgba(50, 0, 50, 0.3)';
    } else if (toTheme === 'contrast') {
        return 'rgba(0, 0, 0, 0.5)';
    } else if (toTheme === 'light') {
        return 'rgba(255, 255, 255, 0.3)';
    } else {
        // Default dark theme transition
        return 'rgba(0, 0, 0, 0.3)';
    }
}

/**
 * Apply animation to cards when theme changes
 * Creates a subtle scale/fade effect on all cards
 */
function animateCardsOnThemeChange() {
    const cards = document.querySelectorAll('.card');
    
    cards.forEach((card, index) => {
        // Save original transform for later restoration
        const originalTransform = card.style.transform;
        const originalTransition = card.style.transition;
        
        // Apply temporary styles for animation
        card.style.transition = 'all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1)';
        card.style.transform = 'scale(0.98)';
        card.style.opacity = '0.8';
        
        // Stagger the animations slightly
        setTimeout(() => {
            card.style.transform = originalTransform || 'scale(1)';
            card.style.opacity = '1';
            
            // Restore original transition after animation completes
            setTimeout(() => {
                card.style.transition = originalTransition;
            }, 400);
        }, 50 + (index * 30)); // Staggered delay based on card index
    });
}

/**
 * Apply animation to buttons when theme changes
 */
function animateButtonsOnThemeChange() {
    const buttons = document.querySelectorAll('.btn');
    
    buttons.forEach((button, index) => {
        // Save original background for later restoration
        const originalBackground = button.style.background;
        const originalTransition = button.style.transition;
        const originalTransform = button.style.transform;
        
        // Apply temporary styles for animation
        button.style.transition = 'all 0.3s ease-out';
        button.style.transform = 'scale(0.97)';
        
        // Stagger the animations slightly
        setTimeout(() => {
            button.style.transform = originalTransform || 'scale(1)';
            
            // Restore original properties after animation completes
            setTimeout(() => {
                button.style.transition = originalTransition;
                button.style.background = originalBackground;
            }, 300);
        }, 50 + (index * 20)); // Staggered delay based on button index
    });
}

/**
 * Update the theme with enhanced transitions and animations
 * @param {string} theme - The name of the theme to apply
 */
function updateThemeWithAnimations(theme) {
    const body = document.body;
    const previousTheme = body.dataset.theme || 'dark';
    
    // Only run animations if theme is actually changing
    if (previousTheme === theme) {
        return;
    }
    
    // Create transition overlay effect
    createThemeTransition(previousTheme, theme);
    
    // Apply the actual theme change
    window.updateTheme(theme);
    
    // Animate cards and buttons
    setTimeout(() => {
        animateCardsOnThemeChange();
        animateButtonsOnThemeChange();
    }, 100);
}

// Make functions available globally
window.createThemeTransition = createThemeTransition;
window.animateCardsOnThemeChange = animateCardsOnThemeChange;
window.animateButtonsOnThemeChange = animateButtonsOnThemeChange;
window.updateThemeWithAnimations = updateThemeWithAnimations;