/**
 * Alpine.js Initialization
 * 
 * This file contains Alpine.js component registrations and initializations.
 * It also sets up global event handling for theme changes and other UI interactions.
 */

// Initialize theme before Alpine.js loads to prevent flashing
function initializeTheme() {
    const getTheme = () => {
        const persistedTheme = localStorage.getItem('theme');
        if (persistedTheme) return persistedTheme;
        
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    };
    
    const theme = getTheme();
    const root = document.documentElement;
    
    if (theme === 'dark' || ['space', 'neon', 'contrast'].includes(theme)) {
        root.classList.add('dark');
    } else {
        root.classList.remove('dark');
    }
    
    if (theme !== 'light' && theme !== 'dark') {
        root.classList.add(`theme-${theme}`);
    }
    
    // Wait for document.body to be available
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            if (document.body) {
                document.body.setAttribute('data-theme', theme);
            }
        });
    } else if (document.body) {
        document.body.setAttribute('data-theme', theme);
    }
}

// Run theme initialization immediately
if (typeof document !== 'undefined') {
    initializeTheme();
}

document.addEventListener('alpine:init', () => {
    // Register any additional Alpine.js components or stores here
    
    // Setup collapse plugin if available
    if (typeof Alpine.plugin === 'function' && typeof Alpine.collapse === 'object') {
        Alpine.plugin(Alpine.collapse);
    } else {
        console.log('Alpine collapse plugin not available - using auto import');
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
        current: localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'),
        isDark: localStorage.getItem('theme') === 'dark' || 
                localStorage.getItem('theme') === 'space' || 
                localStorage.getItem('theme') === 'neon' || 
                localStorage.getItem('theme') === 'contrast' || 
                (localStorage.getItem('theme') === null && window.matchMedia('(prefers-color-scheme: dark)').matches),
        menuOpen: false,
        
        // Premium theme check
        isPremiumTheme(theme) {
            return ['space', 'neon', 'contrast'].includes(theme);
        },
        
        // Toggle between light and dark
        toggle() {
            this.isDark = !this.isDark;
            this.current = this.isDark ? 'dark' : 'light';
            this.apply(this.current);
        },
        
        // Set a specific theme
        set(themeName) {
            // Check if it's a premium theme and user has premium
            if (this.isPremiumTheme(themeName) && !document.body.getAttribute('data-premium') === 'true') {
                console.warn('Cannot apply premium theme - user does not have premium subscription');
                return;
            }
            
            this.current = themeName;
            this.isDark = themeName === 'dark' || this.isPremiumTheme(themeName);
            this.apply(themeName);
            this.menuOpen = false;
        },
        
        // Apply the selected theme
        apply(themeName) {
            if (!document.documentElement) return;
            
            const root = document.documentElement;
            
            // Clear existing theme classes
            root.classList.remove('theme-space', 'theme-neon', 'theme-contrast');
            
            // Set dark mode class
            if (themeName === 'dark' || this.isPremiumTheme(themeName)) {
                root.classList.add('dark');
            } else {
                root.classList.remove('dark');
            }
            
            // Add specific theme class
            if (this.isPremiumTheme(themeName)) {
                root.classList.add(`theme-${themeName}`);
            }
            
            // Store the theme preference
            localStorage.setItem('theme', themeName);
            
            // Safely update body data attribute
            if (document.body) {
                document.body.setAttribute('data-theme', themeName);
                
                // If user is authenticated, save preference to server
                if (document.body.hasAttribute('data-user-authenticated') && 
                    document.body.getAttribute('data-user-authenticated') === 'true') {
                    this.saveToServer(themeName);
                }
            }
            
            // Dispatch theme change event
            window.dispatchEvent(new CustomEvent('theme-changed', {
                detail: { theme: themeName, isDark: this.isDark }
            }));
        },
        
        // Save theme preference to server
        saveToServer(themeName) {
            fetch('/update_theme_preference', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''
                },
                body: JSON.stringify({ theme: themeName })
            }).catch(err => {
                console.error('Failed to save theme preference:', err);
            });
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