/**
 * Enhanced Theme Toggle System
 * Provides smooth transitions between themes and saves user preferences
 */

document.addEventListener('DOMContentLoaded', () => {
    // Get theme preference from data attribute or localStorage
    const savedTheme = localStorage.getItem('theme-preference') || 
                      document.body.getAttribute('data-theme') || 
                      'dark';
    
    // Apply the saved theme immediately on page load
    applyTheme(savedTheme);
    
    // Set up event listeners for theme toggle buttons
    const themeToggles = document.querySelectorAll('[data-theme-toggle]');
    
    themeToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const currentTheme = document.body.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            // Apply the new theme with transition
            applyThemeWithTransition(newTheme);
            
            // Save the preference to localStorage
            localStorage.setItem('theme-preference', newTheme);
            
            // Update the data attribute for consistency
            document.body.setAttribute('data-theme', newTheme);
            
            // For logged-in users, save the preference to the server
            if (document.body.getAttribute('data-user-authenticated') === 'true') {
                saveThemePreference(newTheme);
            }
        });
    });
    
    // Handle premium theme selection
    const themeSelectors = document.querySelectorAll('[data-theme-select]');
    
    themeSelectors.forEach(selector => {
        selector.addEventListener('click', function() {
            const selectedTheme = this.getAttribute('data-theme-value');
            
            // Apply the new theme with transition
            applyThemeWithTransition(selectedTheme);
            
            // Save the preference to localStorage
            localStorage.setItem('theme-preference', selectedTheme);
            
            // Update the data attribute for consistency
            document.body.setAttribute('data-theme', selectedTheme);
            
            // For logged-in users, save the preference to the server
            if (document.body.getAttribute('data-user-authenticated') === 'true') {
                saveThemePreference(selectedTheme);
            }
        });
    });
});

/**
 * Apply a theme to the document body without transition
 * @param {string} theme - The theme to apply
 */
function applyTheme(theme) {
    // Remove any existing theme classes
    document.body.classList.remove('light', 'dark', 'theme-space', 'theme-neon', 'theme-contrast');
    
    // Apply the new theme class
    if (theme === 'light') {
        document.body.classList.add('light');
    } else if (theme.startsWith('theme-')) {
        document.body.classList.add('dark');
        document.body.classList.add(theme);
    } else {
        document.body.classList.add('dark');
    }
    
    // Update theme icons visibility
    updateThemeIcons(theme);
}

/**
 * Apply a theme with a smooth transition effect
 * @param {string} theme - The theme to apply
 */
function applyThemeWithTransition(theme) {
    // Add transition class
    document.body.classList.add('theme-transition');
    
    // Apply the theme
    applyTheme(theme);
    
    // Remove transition class after transition completes
    setTimeout(() => {
        document.body.classList.remove('theme-transition');
    }, 500);
}

/**
 * Update theme toggle icons visibility based on current theme
 * @param {string} theme - The current theme
 */
function updateThemeIcons(theme) {
    const sunIcons = document.querySelectorAll('.theme-icon-sun');
    const moonIcons = document.querySelectorAll('.theme-icon-moon');
    
    if (theme === 'light') {
        sunIcons.forEach(icon => icon.classList.add('hidden'));
        moonIcons.forEach(icon => icon.classList.remove('hidden'));
    } else {
        sunIcons.forEach(icon => icon.classList.remove('hidden'));
        moonIcons.forEach(icon => icon.classList.add('hidden'));
    }
}

/**
 * Save theme preference to server via AJAX
 * @param {string} theme - The theme preference to save
 */
function saveThemePreference(theme) {
    fetch('/update_theme_preference', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ theme_preference: theme })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Theme preference saved successfully');
        } else {
            console.error('Failed to save theme preference');
        }
    })
    .catch(error => {
        console.error('Error saving theme preference:', error);
    });
}