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
        if (!theme) return; // Guard against null/undefined values
        
        try {
            applyTheme(theme);
            
            // Safe localStorage access
            try {
                if (typeof localStorage !== 'undefined') {
                    localStorage.setItem('theme', theme);
                }
            } catch (e) {
                console.warn('Failed to save theme to localStorage:', e);
            }
            
            // Only update server if DOM is ready and user is authenticated
            if (document.readyState === 'complete' || document.readyState === 'interactive') {
                const isAuthenticated = document.body && document.body.getAttribute('data-user-authenticated') === 'true';
                if (isAuthenticated) {
                    updateServerThemePreference(theme);
                }
            } else {
                // If DOM isn't ready yet, wait for it
                document.addEventListener('DOMContentLoaded', () => {
                    const isAuthenticated = document.body && document.body.getAttribute('data-user-authenticated') === 'true';
                    if (isAuthenticated) {
                        updateServerThemePreference(theme);
                    }
                });
            }
        } catch (e) {
            console.error('Error in setTheme:', e);
        }
    };
    
    // Function to apply theme changes to the document
    function applyTheme(theme) {
        try {
            const PREMIUM_THEMES = ['space', 'neon', 'contrast'];
            const isDarkTheme = theme === 'dark' || PREMIUM_THEMES.includes(theme);
            
            // Only proceed if document is available
            if (typeof document === 'undefined' || !document.documentElement) {
                console.warn('Document not available for theme application');
                return;
            }
            
            // Apply to HTML element (documentElement)
            const root = document.documentElement;
            
            // Remove all theme classes
            root.classList.remove('theme-light', 'theme-dark', 'theme-space', 'theme-neon', 'theme-contrast');
            
            // Add dark mode class if needed
            if (isDarkTheme) {
                root.classList.add('dark');
            } else {
                root.classList.remove('dark');
            }
            
            // Add specific theme class if it's a premium theme
            if (PREMIUM_THEMES.includes(theme)) {
                root.classList.add(`theme-${theme}`);
            }
            
            // Update body data attribute ONLY if body exists
            if (document.body) {
                document.body.setAttribute('data-theme', theme);
            }
            
            // Safely dispatch theme change event
            if (typeof window !== 'undefined' && typeof CustomEvent !== 'undefined') {
                try {
                    window.dispatchEvent(new CustomEvent('theme-changed', {
                        detail: {
                            theme,
                            isDark: isDarkTheme
                        }
                    }));
                } catch (e) {
                    console.warn('Could not dispatch theme-changed event:', e);
                }
            }
        } catch (e) {
            console.error('Error applying theme:', e);
        }
    }
    
    // Function to update server-side theme preference with error handling
    function updateServerThemePreference(theme) {
        try {
            // Get CSRF token safely
            let csrfToken = '';
            try {
                const metaTag = document.querySelector('meta[name="csrf-token"]');
                if (metaTag) {
                    csrfToken = metaTag.getAttribute('content') || '';
                }
            } catch (e) {
                console.warn('Error getting CSRF token:', e);
            }
            
            // Make the fetch request with proper error handling
            fetch('/update_theme_preference', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ theme: theme || 'light' }) // Ensure theme is never null/undefined
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Server returned ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.status !== 'success') {
                    console.warn('Theme preference update had non-success status:', data.message || 'No details provided');
                }
            })
            .catch(error => {
                console.warn('Error updating theme preference:', error);
                // Non-critical error, no need to re-throw
            });
        } catch (e) {
            // Catch any synchronous errors in the try block
            console.warn('Error in updateServerThemePreference:', e);
        }
    }
});