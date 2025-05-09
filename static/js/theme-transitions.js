/**
 * AstroBot AI - Theme Transitions
 * 
 * This script provides utilities for smooth theme transitions
 * when switching between themes to avoid harsh visual changes.
 */

class ThemeTransitionManager {
  constructor() {
    this.transitionClass = 'theme-transition';
    this.transitionDuration = 400; // milliseconds, should match CSS
    this.transitionTimers = {};
  }

  /**
   * Apply transition effect before changing theme
   * @param {string} elementSelector - CSS selector for the element to apply transition to
   * @param {Function} callback - Function to execute during the transition
   */
  applyTransition(elementSelector = 'body', callback) {
    const element = document.querySelector(elementSelector);
    if (!element) return;

    // Clear any existing transition timeout for this element
    if (this.transitionTimers[elementSelector]) {
      clearTimeout(this.transitionTimers[elementSelector]);
    }

    // Add transition class
    element.classList.add(this.transitionClass);

    // Execute the theme change callback
    if (typeof callback === 'function') {
      callback();
    }

    // Remove transition class after transition completes
    this.transitionTimers[elementSelector] = setTimeout(() => {
      element.classList.remove(this.transitionClass);
      delete this.transitionTimers[elementSelector];
    }, this.transitionDuration);
  }

  /**
   * Apply transitions to all specified elements
   * @param {Array} elements - Array of element selectors to apply transitions to
   * @param {Function} callback - Function to execute during the transition
   */
  applyTransitionToElements(elements = ['body', 'html', '.sidebar', '.navbar'], callback) {
    elements.forEach(selector => {
      this.applyTransition(selector, callback);
    });
  }
}

// Create a global instance
window.themeTransitionManager = new ThemeTransitionManager();