/**
 * Alpine.js Initialization
 * 
 * This file contains Alpine.js component registrations and initializations.
 * It also sets up global event handling for theme changes and other UI interactions.
 */

document.addEventListener('alpine:init', () => {
    // Register any additional Alpine.js components or stores here
    
    // Setup collapse plugin if available
    if (typeof Alpine.plugin === 'function' && typeof Alpine.collapse === 'object') {
        Alpine.plugin(Alpine.collapse);
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