/**
 * Theme Toggle
 * 
 * This file contains functionality for theme toggling and syncing
 * theme preferences across the interface.
 */

// Once DOM is loaded, set up theme preferences
document.addEventListener('DOMContentLoaded', () => {
    // Get theme preference from localStorage or default to system preference
    const getThemePreference = () => {
        const storedTheme = localStorage.getItem('theme');
        if (storedTheme) return storedTheme;
        
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    };
    
    const theme = getThemePreference();
    
    // Apply theme to document root
    if (theme === 'dark' || ['space', 'neon', 'contrast'].includes(theme)) {
        document.documentElement.classList.add('dark');
    } else {
        document.documentElement.classList.remove('dark');
    }
    
    // If it's a premium theme (not light or dark), add the theme class
    if (theme !== 'light' && theme !== 'dark') {
        document.documentElement.classList.add(`theme-${theme}`);
    }
    
    // Set theme data attribute on body
    if (document.body) {
        document.body.setAttribute('data-theme', theme);
    }
    
    // Set up system preference change listener
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        // Only change theme if user hasn't set a preference
        if (!localStorage.getItem('theme')) {
            const newTheme = e.matches ? 'dark' : 'light';
            applyTheme(newTheme);
        }
    });
    
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