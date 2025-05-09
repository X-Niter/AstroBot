/**
 * AstroBot AI - Theme Manager
 * 
 * Manages theme selection, persistence, and transitions.
 * Supports dark/light mode toggling and premium themes.
 */

// Theme constants
const THEMES = {
  LIGHT: 'light',
  DARK: 'dark',
  SPACE: 'space',
  NEON: 'neon',
  CONTRAST: 'contrast'
};

// Theme options available to users
const THEME_OPTIONS = [
  { id: THEMES.LIGHT, name: 'Light', isPremium: false },
  { id: THEMES.DARK, name: 'Dark', isPremium: false },
  { id: THEMES.SPACE, name: 'Space', isPremium: true },
  { id: THEMES.NEON, name: 'Neon', isPremium: true },
  { id: THEMES.CONTRAST, name: 'High Contrast', isPremium: true }
];

// Default theme if none is selected
const DEFAULT_THEME = THEMES.LIGHT;

// Main theme handler
window.ThemeManager = {
  /**
   * Alpine.js init function
   */
  init() {
    this.theme = this.getSavedTheme() || this.getPreferredTheme() || DEFAULT_THEME;
    this.setTheme(this.theme);
    this.mounted = false;
    this.premium = false; // Set to true if premium themes are available

    // Set initial view data
    this.darkMode = this.isDarkMode();
    this.selectedTheme = this.theme;
    this.availableThemes = THEME_OPTIONS;

    // Wait for document to be ready before showing UI
    window.addEventListener('DOMContentLoaded', () => {
      setTimeout(() => {
        this.mounted = true;
      }, 200);
    });
    
    // Listen for OS dark mode changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
      if (!this.getSavedTheme()) {
        const newTheme = e.matches ? THEMES.DARK : THEMES.LIGHT;
        this.darkMode = e.matches;
        this.setTheme(newTheme);
      }
    });
  },

  /**
   * Toggles between dark and light mode
   */
  toggleDarkMode() {
    const newTheme = this.isDarkMode() ? THEMES.LIGHT : THEMES.DARK;
    this.darkMode = !this.darkMode;
    this.setTheme(newTheme);
    this.saveThemePreference(newTheme);
  },

  /**
   * Sets a premium theme
   * @param {string} themeId Theme identifier
   */
  setPremiumTheme(themeId) {
    if (!this.premium && this.isPremiumTheme(themeId)) {
      console.log('Premium theme not available');
      return;
    }

    if (this.isPremiumTheme(themeId) || themeId === THEMES.LIGHT || themeId === THEMES.DARK) {
      this.selectedTheme = themeId;
      this.darkMode = themeId === THEMES.DARK || this.isPremiumTheme(themeId);
      this.setTheme(themeId);
      this.saveThemePreference(themeId);
    }
  },

  /**
   * Checks if a theme is premium
   * @param {string} themeId Theme identifier
   * @returns {boolean} True if premium
   */
  isPremiumTheme(themeId) {
    const theme = THEME_OPTIONS.find(t => t.id === themeId);
    return theme ? theme.isPremium : false;
  },

  /**
   * Checks if dark mode is active
   * @returns {boolean} True if dark mode
   */
  isDarkMode() {
    return [THEMES.DARK, THEMES.SPACE, THEMES.NEON].includes(this.theme);
  },
  
  /**
   * Checks if current theme has dark background
   * @returns {boolean} True if dark background
   */
  hasDarkBackground() {
    return [THEMES.DARK, THEMES.SPACE, THEMES.NEON, THEMES.CONTRAST].includes(this.theme);
  },

  /**
   * Applies theme classes to HTML element
   * @param {string} theme Theme identifier
   */
  setTheme(theme) {
    const root = document.documentElement;
    const isDark = [THEMES.DARK, THEMES.SPACE, THEMES.NEON, THEMES.CONTRAST].includes(theme);

    // Apply theme class
    THEME_OPTIONS.forEach(t => {
      if (t.id === theme) {
        root.classList.add(`theme-${t.id}`);
      } else {
        root.classList.remove(`theme-${t.id}`);
      }
    });

    // Apply dark/light class
    if (isDark) {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }

    // Store current theme
    this.theme = theme;
    this.selectedTheme = theme;

    // Update UI state
    this.darkMode = this.isDarkMode();

    // Dispatch event for other components
    this.dispatchThemeChanged(theme);
  },

  /**
   * Saves theme selection to localStorage
   * @param {string} theme Theme identifier
   */
  saveThemePreference(theme) {
    localStorage.setItem('theme', theme);
    this.dispatchThemeChanged(theme);
  },

  /**
   * Retrieves saved theme from localStorage
   * @returns {string|null} Saved theme or null
   */
  getSavedTheme() {
    return localStorage.getItem('theme');
  },

  /**
   * Gets system preferred color scheme
   * @returns {string} THEMES.DARK or THEMES.LIGHT
   */
  getPreferredTheme() {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? THEMES.DARK : THEMES.LIGHT;
  },
  
  /**
   * Resets to system preferred theme
   */
  resetToSystemTheme() {
    localStorage.removeItem('theme');
    const preferredTheme = this.getPreferredTheme();
    this.setTheme(preferredTheme);
    this.darkMode = preferredTheme === THEMES.DARK;
    this.selectedTheme = preferredTheme;
    this.dispatchThemeChanged(preferredTheme);
  },

  /**
   * Dispatches custom event when theme changes
   * @param {string} theme New theme
   */
  dispatchThemeChanged(theme) {
    const event = new CustomEvent('theme-changed', { 
      detail: { theme, isDark: this.isDarkMode() } 
    });
    window.dispatchEvent(event);
  }
};