/**
 * AstroBot AI - Theme Transitions
 * 
 * Adds smooth transition effects when switching themes.
 * Works with the ThemeManager to provide visual feedback during theme changes.
 */

(function() {
  // Configuration
  const TRANSITION_DURATION = 400; // milliseconds, should match CSS var --theme-transition-duration
  const TRANSITION_CLASS = 'theme-transition';
  
  // Elements to apply transition to
  const APPLY_TO_SELECTORS = [
    'body', 
    'header', 
    'main', 
    'footer', 
    'nav', 
    '.card', 
    '.btn', 
    'input', 
    'select', 
    'textarea',
    '.alert',
    '.table',
    '.badge',
    '.navbar',
    '.sidebar'
  ];
  
  // Properties to transition
  const TRANSITION_PROPS = [
    'background-color',
    'color',
    'border-color',
    'box-shadow'
  ];
  
  // Initialize once DOM is loaded
  document.addEventListener('DOMContentLoaded', () => {
    setupThemeTransitions();
  });

  /**
   * Set up theme transition listeners and handlers
   */
  function setupThemeTransitions() {
    // Watch for theme changes
    window.addEventListener('theme-changed', handleThemeChange);
    
    // Also apply transitions when theme toggler is clicked directly
    document.querySelectorAll('[data-theme-toggle]').forEach(toggler => {
      toggler.addEventListener('click', applyTransitionEffect);
    });
    
    // Apply to theme selector change
    document.querySelectorAll('[data-theme-select]').forEach(select => {
      select.addEventListener('change', applyTransitionEffect);
    });
  }
  
  /**
   * Handler for theme-changed event
   * @param {CustomEvent} event Theme changed event
   */
  function handleThemeChange(event) {
    const { theme, isDark } = event.detail;
    applyTransitionEffect();
  }
  
  /**
   * Apply CSS transition classes, then remove after transition completes
   */
  function applyTransitionEffect() {
    const elements = findTransitionElements();
    
    // Apply transition class to elements
    elements.forEach(el => {
      el.classList.add(TRANSITION_CLASS);
    });
    
    // Remove transition class after duration
    setTimeout(() => {
      elements.forEach(el => {
        el.classList.remove(TRANSITION_CLASS);
      });
    }, TRANSITION_DURATION + 50); // Add a small buffer to ensure transitions complete
  }
  
  /**
   * Find all elements to apply transitions to
   * @returns {Element[]} Array of matched elements
   */
  function findTransitionElements() {
    const elements = [];
    
    APPLY_TO_SELECTORS.forEach(selector => {
      const matched = document.querySelectorAll(selector);
      matched.forEach(el => elements.push(el));
    });
    
    return elements;
  }
  
  /**
   * Creates a style element with transition rules
   * Only needed if CSS variables aren't working properly
   */
  function injectTransitionStyles() {
    const styleEl = document.createElement('style');
    const transitionProps = TRANSITION_PROPS.join(', ');
    
    styleEl.textContent = `
      .${TRANSITION_CLASS} {
        transition: ${transitionProps} ${TRANSITION_DURATION}ms ease !important;
      }
    `;
    
    document.head.appendChild(styleEl);
  }
})();