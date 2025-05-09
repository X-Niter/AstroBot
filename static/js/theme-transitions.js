/**
 * Theme Transition System
 * Handles smooth transitions between themes
 */

// Global theme transitions
let currentTransition = null;

/**
 * Updates the theme with smooth animations
 * @param {string} theme - The theme name to switch to
 */
window.updateThemeWithAnimations = function(theme) {
    // If there's already a transition in progress, clear it
    if (currentTransition) {
        clearTimeout(currentTransition);
    }
    
    // Add transition classes to smoothly fade between themes
    document.body.classList.add('theme-transition');
    
    // Short timeout to ensure the transition class is applied
    setTimeout(() => {
        // Update the theme attribute and class
        document.body.setAttribute('data-theme', theme);
        
        // Remove all theme classes
        document.body.classList.remove('dark', 'light', 'theme-space', 'theme-neon', 'theme-contrast');
        
        // Add the appropriate theme class
        if (theme === 'light') {
            // Light theme has no additional class as it's the default
        } else if (theme === 'dark') {
            document.body.classList.add('dark');
        } else if (theme.startsWith('theme-')) {
            // Premium themes
            document.body.classList.add(theme);
            
            // Premium themes are variants of dark mode
            document.body.classList.add('dark');
        }
        
        // Track transition in localStorage for persistence
        localStorage.setItem('theme', theme);
        
        // Schedule the removal of the transition class
        currentTransition = setTimeout(() => {
            document.body.classList.remove('theme-transition');
            currentTransition = null;
        }, 400); // Match this to the CSS transition duration
    }, 50);
};

/**
 * Simple theme update without animations
 * @param {string} theme - The theme name to switch to
 */
window.updateTheme = function(theme) {
    // Update the theme attribute
    document.body.setAttribute('data-theme', theme);
    
    // Remove all theme classes
    document.body.classList.remove('dark', 'light', 'theme-space', 'theme-neon', 'theme-contrast');
    
    // Add the appropriate theme class
    if (theme === 'light') {
        // Light theme has no additional class as it's the default
    } else if (theme === 'dark') {
        document.body.classList.add('dark');
    } else if (theme.startsWith('theme-')) {
        // Premium themes
        document.body.classList.add(theme);
        
        // Premium themes are variants of dark mode
        document.body.classList.add('dark');
    }
    
    // Store the theme in localStorage
    localStorage.setItem('theme', theme);
};

/**
 * Initialize theme from storage or system preference
 */
document.addEventListener('DOMContentLoaded', function() {
    // Check for stored theme preference
    const storedTheme = localStorage.getItem('theme');
    
    if (storedTheme) {
        // If we have a stored theme, use it
        window.updateTheme(storedTheme);
    } else {
        // Check for system preference
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        if (prefersDark) {
            window.updateTheme('dark');
        } else {
            window.updateTheme('light');
        }
    }
    
    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        if (!localStorage.getItem('theme')) {
            // Only auto-switch if the user hasn't set a preference
            const newTheme = e.matches ? 'dark' : 'light';
            window.updateThemeWithAnimations(newTheme);
        }
    });
});