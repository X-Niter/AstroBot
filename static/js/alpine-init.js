/**
 * Alpine.js Initialization
 * 
 * This file contains Alpine.js component registrations and initializations.
 * It also sets up global event handling for theme changes and other UI interactions.
 */

// Initialize theme before Alpine.js loads to prevent flashing
// We'll use a more robust approach that doesn't depend on document.body
const THEME_STORAGE_KEY = 'theme';
const DEFAULT_THEME = 'light';
const PREMIUM_THEMES = ['space', 'neon', 'contrast'];

// Global variable to store the current theme
let currentTheme = DEFAULT_THEME;

function getPreferredColorScheme() {
    // Check if window and matchMedia are available
    if (typeof window !== 'undefined' && window.matchMedia) {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return DEFAULT_THEME;
}

function getSavedTheme() {
    // Check if localStorage is available
    if (typeof localStorage !== 'undefined') {
        try {
            return localStorage.getItem(THEME_STORAGE_KEY);
        } catch (e) {
            console.warn('Error accessing localStorage:', e);
        }
    }
    return null;
}

function isDarkTheme(theme) {
    return theme === 'dark' || PREMIUM_THEMES.includes(theme);
}

function isPremiumTheme(theme) {
    return PREMIUM_THEMES.includes(theme);
}

function determineTheme() {
    const savedTheme = getSavedTheme();
    return savedTheme || getPreferredColorScheme();
}

function applyThemeToHTML(theme) {
    // Only run if document is available
    if (typeof document === 'undefined' || !document.documentElement) return;
    
    const root = document.documentElement;
    
    // Clear existing theme classes
    PREMIUM_THEMES.forEach(themeName => {
        root.classList.remove(`theme-${themeName}`);
    });
    
    // Apply dark mode if needed
    if (isDarkTheme(theme)) {
        root.classList.add('dark');
    } else {
        root.classList.remove('dark');
    }
    
    // Apply premium theme class if needed
    if (isPremiumTheme(theme)) {
        root.classList.add(`theme-${theme}`);
    }
    
    // Store the current theme
    currentTheme = theme;
}

// Initialize theme system
function initializeTheme() {
    const theme = determineTheme();
    applyThemeToHTML(theme);
    
    // We'll handle body separately in DOMContentLoaded
}

// Safe theme initialization with multiple attempts
if (typeof window !== 'undefined') {
    // Try immediately
    try {
        initializeTheme();
    } catch (e) {
        console.warn('Error during initial theme setup:', e);
    }
    
    // Set up body attribute when DOM is ready
    document.addEventListener('DOMContentLoaded', () => {
        try {
            // Set data-theme on body element if available
            if (document.body) {
                document.body.setAttribute('data-theme', currentTheme);
            }
            
            // Add listener for theme system preference changes
            if (window.matchMedia) {
                window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
                    // Only update if user hasn't explicitly set a theme
                    if (!getSavedTheme()) {
                        const newTheme = event.matches ? 'dark' : 'light';
                        applyThemeToHTML(newTheme);
                        
                        if (document.body) {
                            document.body.setAttribute('data-theme', newTheme);
                        }
                    }
                });
            }
        } catch (e) {
            console.warn('Error during DOMContentLoaded theme setup:', e);
        }
    });
}

document.addEventListener('alpine:init', () => {
    // Register any additional Alpine.js components or stores here
    
    // Register Alpine Collapse plugin if it's a global
    if (typeof Alpine.plugin === 'function') {
        // If Alpine.collapse is available as a plugin, use it
        if (typeof Alpine.collapse === 'object') {
            Alpine.plugin(Alpine.collapse);
            console.log('Using global Alpine collapse plugin');
        } else {
            // Otherwise we'll use our custom implementation in alpine-collapse.js
            console.log('Alpine collapse plugin not available - using custom implementation');
        }
    }
    
    // Create a global store for application state
    Alpine.store('app', {
        // Global application state
        sidebarOpen: window.innerWidth >= 1024, // Open by default on desktop
        notifications: [],
        
        // Methods
        toggleSidebar() {
            this.sidebarOpen = !this.sidebarOpen;
        },
        
        addNotification(message, type = 'info', timeout = 5000) {
            const id = Date.now();
            this.notifications.push({ id, message, type });
            
            if (timeout) {
                setTimeout(() => {
                    this.removeNotification(id);
                }, timeout);
            }
            
            return id;
        },
        
        removeNotification(id) {
            this.notifications = this.notifications.filter(n => n.id !== id);
        }
    });
    
    // Theme manager store
    Alpine.store('theme', {
        // State
        current: determineTheme(),
        isDark: isDarkTheme(determineTheme()),
        menuOpen: false,
        
        // Reuse the global utility functions
        isPremiumTheme(theme) {
            return isPremiumTheme(theme);
        },
        
        // Toggle between light and dark
        toggle() {
            this.isDark = !this.isDark;
            this.current = this.isDark ? 'dark' : 'light';
            this.apply(this.current);
        },
        
        // Set a specific theme
        set(themeName) {
            // Check if premium theme and if user has premium access
            // Safely check premium status without relying on document.body
            try {
                const hasPremium = typeof document !== 'undefined' && 
                                  document.body && 
                                  document.body.getAttribute('data-premium') === 'true';
                
                if (isPremiumTheme(themeName) && !hasPremium) {
                    console.warn('Cannot apply premium theme - user does not have premium subscription');
                    return;
                }
            } catch (e) {
                console.warn('Error checking premium status:', e);
            }
            
            this.current = themeName;
            this.isDark = isDarkTheme(themeName);
            this.apply(themeName);
            this.menuOpen = false;
        },
        
        // Apply the selected theme
        apply(themeName) {
            try {
                // Apply theme to HTML
                applyThemeToHTML(themeName);
                
                // Store in our state
                this.current = themeName;
                this.isDark = isDarkTheme(themeName);
                
                // Store the theme preference
                if (typeof localStorage !== 'undefined') {
                    localStorage.setItem(THEME_STORAGE_KEY, themeName);
                }
                
                // Safely update body data attribute if available
                if (typeof document !== 'undefined' && document.body) {
                    document.body.setAttribute('data-theme', themeName);
                    
                    // Check if user is authenticated
                    const isAuthenticated = document.body.hasAttribute('data-user-authenticated') && 
                                          document.body.getAttribute('data-user-authenticated') === 'true';
                    
                    // If authenticated, save to server
                    if (isAuthenticated) {
                        this.saveToServer(themeName);
                    }
                }
                
                // Dispatch theme change event
                if (typeof window !== 'undefined') {
                    window.dispatchEvent(new CustomEvent('theme-changed', {
                        detail: { theme: themeName, isDark: this.isDark }
                    }));
                }
            } catch (e) {
                console.error('Error applying theme:', e);
            }
        },
        
        // Save theme preference to server
        saveToServer(themeName) {
            try {
                const csrfToken = typeof document !== 'undefined' && 
                                 document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
                
                fetch('/update_theme_preference', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({ theme: themeName })
                }).catch(err => {
                    console.error('Failed to save theme preference:', err);
                });
            } catch (e) {
                console.warn('Error saving theme to server:', e);
            }
        }
    });
    
    // Log successful initialization
    console.log('Alpine.js initialization completed');
});

// Setup global event listeners for UI interactions
document.addEventListener('DOMContentLoaded', () => {
    // Theme change event listener
    window.addEventListener('theme-changed', (e) => {
        const { theme, isDark } = e.detail;
        console.log(`Theme changed to ${theme}, dark mode: ${isDark}`);
        
        // You can add additional theme change handlers here
    });
});