/**
 * Theme Toggle Module
 * Handles theme switching between light and dark modes
 * Works with premium themes as well
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get references to elements
    const themeToggleBtn = document.getElementById('theme-toggle');
    const lightIcon = document.querySelector('.theme-light-icon');
    const darkIcon = document.querySelector('.theme-dark-icon');
    
    if (!themeToggleBtn) return;

    // Initialize icons based on current theme
    const currentTheme = document.body.dataset.theme || 'dark';
    updateThemeIcons(currentTheme);
    
    // Add click event listener to toggle button
    themeToggleBtn.addEventListener('click', function() {
        const currentTheme = document.body.dataset.theme || 'dark';
        const isLightTheme = currentTheme === 'light';
        
        // Determine new theme
        let newTheme;
        if (isLightTheme) {
            // Switch to dark or last used dark theme
            const lastDarkTheme = localStorage.getItem('last_dark_theme') || 'dark';
            newTheme = lastDarkTheme;
        } else {
            // Store current dark theme before switching to light
            if (currentTheme !== 'light') {
                localStorage.setItem('last_dark_theme', currentTheme);
            }
            newTheme = 'light';
        }
        
        // Use the updateThemeWithAnimations function for a smooth transition
        if (window.updateThemeWithAnimations) {
            window.updateThemeWithAnimations(newTheme);
        } else {
            window.updateTheme(newTheme);
        }
        
        // Update theme icons
        updateThemeIcons(newTheme);
        
        // Send theme preference to server if user is logged in
        if (document.body.dataset.userAuthenticated === 'true') {
            sendThemePreference(newTheme);
        }
    });
    
    /**
     * Updates the visibility of theme icons based on current theme
     * @param {string} theme - The current theme name
     */
    function updateThemeIcons(theme) {
        if (theme === 'light') {
            darkIcon.classList.add('hidden');
            lightIcon.classList.remove('hidden');
        } else {
            lightIcon.classList.add('hidden');
            darkIcon.classList.remove('hidden');
        }
    }
    
    /**
     * Sends the user's theme preference to the server
     * @param {string} theme - The theme preference to save
     */
    function sendThemePreference(theme) {
        fetch('/update_theme_preference', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ theme: theme })
        })
        .then(response => {
            if (!response.ok) {
                console.error('Failed to save theme preference');
            }
        })
        .catch(error => {
            console.error('Error saving theme preference:', error);
        });
    }
});

// Add shortcut keys for theme toggling (Alt+T)
document.addEventListener('keydown', function(event) {
    // Alt+T for theme toggle
    if (event.altKey && event.key === 't') {
        const themeToggleBtn = document.getElementById('theme-toggle');
        if (themeToggleBtn) {
            themeToggleBtn.click();
        }
    }
});