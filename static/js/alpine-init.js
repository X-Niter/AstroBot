/**
 * AstroBot AI - Alpine.js Initialization
 * 
 * This file handles Alpine.js initialization, including plugin registration.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Alpine plugins need to be registered before Alpine.start()
  try {
    // Load the collapse plugin when available
    if (window.Alpine && window.Alpine.plugin && typeof window.Alpine.plugin === 'function' && window.Alpine.collapse) {
      window.Alpine.plugin(window.Alpine.collapse);
      console.log('Alpine Collapse plugin registered');
    } else {
      console.warn('Alpine Collapse plugin not available, dynamically loading it');
      loadCollapsePlugin();
    }
    
    // Register theme manager data
    if (window.Alpine && window.ThemeManager) {
      window.Alpine.data('themeManager', () => window.ThemeManager);
      console.log('ThemeManager registered');
    }
    
    // Add custom directives
    addCustomDirectives();
    
  } catch (error) {
    console.error('Error initializing Alpine plugins:', error);
  }
});

/**
 * Dynamically load the Alpine Collapse plugin
 * This function will add the plugin to the page if it's not already loaded
 */
function loadCollapsePlugin() {
  // Create script tag
  const script = document.createElement('script');
  script.setAttribute('src', 'https://cdn.jsdelivr.net/npm/@alpinejs/collapse@3.x.x/dist/cdn.min.js');
  script.setAttribute('defer', 'true');
  document.head.appendChild(script);
  
  // Register after load
  script.onload = () => {
    if (window.Alpine && window.Alpine.plugin && window.Alpine.collapse) {
      window.Alpine.plugin(window.Alpine.collapse);
      console.log('Alpine Collapse plugin loaded and registered');
      
      // Restart Alpine if it's already started
      if (window.Alpine.version) {
        window.dispatchEvent(new CustomEvent('alpine:init'));
      }
    }
  };
}

/**
 * Add custom Alpine.js directives for enhanced functionality
 */
function addCustomDirectives() {
  if (!window.Alpine || !window.Alpine.directive) return;
  
  // Add a smooth transition directive for theme changes
  window.Alpine.directive('theme-transition', (el, { expression }, { effect, evaluateLater }) => {
    const duration = expression ? parseInt(expression) : 400;
    
    el.style.transition = `background-color ${duration}ms ease, 
                           color ${duration}ms ease, 
                           border-color ${duration}ms ease, 
                           box-shadow ${duration}ms ease`;
  });
  
  // Loading state directive
  window.Alpine.directive('loading', (el, { modifiers, expression }, { effect, evaluateLater }) => {
    const evaluate = evaluateLater(expression);
    
    effect(() => {
      evaluate(loading => {
        if (loading) {
          el.setAttribute('disabled', true);
          if (modifiers.includes('spinner')) {
            // Add loading spinner
            const originalContent = el.innerHTML;
            el.dataset.originalContent = originalContent;
            el.innerHTML = `<svg class="animate-spin -ml-1 mr-2 h-4 w-4 inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>${modifiers.includes('text') ? 'Loading...' : originalContent}`;
          }
        } else {
          el.removeAttribute('disabled');
          if (modifiers.includes('spinner') && el.dataset.originalContent) {
            el.innerHTML = el.dataset.originalContent;
          }
        }
      });
    });
  });
}