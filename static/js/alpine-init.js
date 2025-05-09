/**
 * AstroBot AI - Alpine.js Initialization
 * This file registers and initializes Alpine.js plugins and data stores
 */

document.addEventListener('DOMContentLoaded', () => {
  try {
    if (window.Alpine) {
      // Register theme manager data
      window.Alpine.data('themeManager', () => {
        return {
          theme: localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'),
          darkMode: localStorage.getItem('theme') === 'dark' || (localStorage.getItem('theme') === null && window.matchMedia('(prefers-color-scheme: dark)').matches),
          availableThemes: [
            { id: 'light', name: 'Light', isPremium: false },
            { id: 'dark', name: 'Dark', isPremium: false },
            { id: 'space', name: 'Space', isPremium: true },
            { id: 'neon', name: 'Neon', isPremium: true },
            { id: 'contrast', name: 'High Contrast', isPremium: true }
          ],
          premium: true, // Should be dynamically set based on user's premium status
          mounted: false,
          init() {
            this.setTheme(this.theme);
            this.mounted = true;
            
            // Listen for OS dark mode changes
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
              if (!localStorage.getItem('theme')) {
                this.darkMode = e.matches;
                this.theme = e.matches ? 'dark' : 'light';
                this.setTheme(this.theme);
              }
            });
          },
          toggleDarkMode() {
            this.darkMode = !this.darkMode;
            const newTheme = this.darkMode ? 'dark' : 'light';
            this.setTheme(newTheme);
            localStorage.setItem('theme', newTheme);
          },
          setPremiumTheme(themeId) {
            if (this.isPremiumTheme(themeId) && !this.premium) {
              // Handle non-premium users trying to use premium themes
              console.log('Premium theme not available');
              return;
            }
            
            this.theme = themeId;
            this.darkMode = themeId === 'dark' || this.isPremiumTheme(themeId);
            this.setTheme(themeId);
            localStorage.setItem('theme', themeId);
          },
          isPremiumTheme(themeId) {
            return ['space', 'neon', 'contrast'].includes(themeId);
          },
          setTheme(theme) {
            const root = document.documentElement;
            
            // Remove all theme classes first
            root.classList.remove('theme-light', 'theme-dark', 'theme-space', 'theme-neon', 'theme-contrast');
            
            // Add the selected theme class
            if (theme !== 'light') {
              root.classList.add(`theme-${theme}`);
            }
            
            // Set dark mode if needed
            if (theme === 'dark' || this.isPremiumTheme(theme)) {
              root.classList.add('dark');
            } else {
              root.classList.remove('dark');
            }
            
            // Set data attributes
            document.body.setAttribute('data-theme', theme);
            
            // Dispatch event for other components to react
            window.dispatchEvent(new CustomEvent('theme-changed', { 
              detail: { theme, isDark: theme === 'dark' || this.isPremiumTheme(theme) } 
            }));
          },
          resetToSystemTheme() {
            localStorage.removeItem('theme');
            const preferredTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
            this.theme = preferredTheme;
            this.darkMode = preferredTheme === 'dark';
            this.setTheme(preferredTheme);
          }
        };
      });
      
      // Register collapse plugin if available
      if (window.Alpine.plugin && window.Alpine.collapse) {
        window.Alpine.plugin(window.Alpine.collapse);
        console.log('Alpine Collapse plugin registered successfully');
      } else {
        console.warn('Alpine Collapse plugin not registered - plugin may not be available');
      }
      
      console.log('Alpine.js initialization completed');
    } else {
      console.error('Alpine.js not found. Make sure it is properly loaded before this script.');
    }
  } catch (error) {
    console.error('Error initializing Alpine.js:', error);
  }
});