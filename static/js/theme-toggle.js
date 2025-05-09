/**
 * Theme Toggle
 * 
 * This file contains functionality for theme toggling and syncing
 * theme preferences across the interface.
 */

// Theme toggle functionality - will be executed when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Constants
    const PREMIUM_THEMES = ['space', 'neon', 'contrast'];
    const DEFAULT_THEME = 'light';
    
    // Use the theme that was initialized early in the page load process
    // or determine it again if that wasn't available
    const initialTheme = window.__initialTheme || getThemePreference();
    
    // Store the theme in the global variable
    window.__initialTheme = initialTheme;
    
    // Safely get theme preference with error handling
    function getThemePreference() {
        try {
            // Try to get from localStorage
            const storedTheme = localStorage.getItem('theme');
            if (storedTheme) return storedTheme;
            
            // Fall back to system preference
            try {
                return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : DEFAULT_THEME;
            } catch (e) {
                console.warn('Could not detect system theme preference:', e);
                return DEFAULT_THEME;
            }
        } catch (e) {
            console.warn('Error accessing localStorage:', e);
            return DEFAULT_THEME;
        }
    }
    
    // Listen for system preference changes
    try {
        const darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        
        // Use the appropriate event listener method (some browsers use 'change', others 'addListener')
        const attachListener = (mq, callback) => {
            if (mq.addEventListener) {
                mq.addEventListener('change', callback);
            } else if (mq.addListener) {
                // For older browsers
                mq.addListener(callback);
            }
        };
        
        attachListener(darkModeMediaQuery, (e) => {
            // Only change theme if user hasn't set a preference
            try {
                if (!localStorage.getItem('theme')) {
                    const newTheme = e.matches ? 'dark' : 'light';
                    applyTheme(newTheme);
                }
            } catch (err) {
                console.warn('Error handling theme media query change:', err);
            }
        });
    } catch (e) {
        console.warn('Could not set up theme media query listener:', e);
    }
    
    // Create a helper function for theme changes
    window.setTheme = (theme) => {
        applyTheme(theme);
        localStorage.setItem('theme', theme);
        
        // Also update server-side preference if user is logged in
        const isAuthenticated = document.body.getAttribute('data-user-authenticated') === 'true';
        if (isAuthenticated) {
            updateServerThemePreference(theme);
        }
    };
    
    // Function to apply theme changes to the document
    function applyTheme(theme) {
        // Remove all theme classes
        document.documentElement.classList.remove('theme-light', 'theme-dark', 'theme-space', 'theme-neon', 'theme-contrast');
        
        // Add dark mode class if needed
        if (theme === 'dark' || ['space', 'neon', 'contrast'].includes(theme)) {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
        
        // Add specific theme class if it's not light or dark
        if (theme !== 'light' && theme !== 'dark') {
            document.documentElement.classList.add(`theme-${theme}`);
        }
        
        // Update body data attribute
        if (document.body) {
            document.body.setAttribute('data-theme', theme);
        }
        
        // Dispatch theme change event
        window.dispatchEvent(new CustomEvent('theme-changed', {
            detail: {
                theme,
                isDark: theme === 'dark' || ['space', 'neon', 'contrast'].includes(theme)
            }
        }));
    }
    
    // Function to update server-side theme preference
    function updateServerThemePreference(theme) {
        fetch('/update_theme_preference', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''
            },
            body: JSON.stringify({ theme })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status !== 'success') {
                console.error('Error updating theme preference:', data.message);
            }
        })
        .catch(error => {
            console.error('Error updating theme preference:', error);
        });
    }
});