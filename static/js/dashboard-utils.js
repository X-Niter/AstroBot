/**
 * AstroBot Dashboard Utilities
 * A collection of utility functions for the analytics dashboard
 */

// Create a namespace for AstroBot utilities if it doesn't exist
window.AstroBotUtils = window.AstroBotUtils || {};

// Animation utilities using GSAP
AstroBotUtils.animation = {
  /**
   * Safely check if GSAP is available and if elements exist before animating
   * @param {string} selector - CSS selector for target elements
   * @returns {boolean} - Whether GSAP is available and elements exist
   */
  canAnimate: function(selector) {
    if (typeof gsap === 'undefined') {
      console.warn('GSAP is not available');
      return false;
    }
    
    if (!selector) {
      console.warn('No selector provided for animation');
      return false;
    }
    
    const elements = document.querySelectorAll(selector);
    if (elements.length === 0) {
      console.warn(`No elements found for selector: ${selector}`);
      return false;
    }
    
    return true;
  },
  /**
   * Animate elements with an entrance animation
   * @param {string} selector - CSS selector for target elements
   * @param {Object} options - GSAP animation options
   */
  animateEntrance: function(selector, options = {}) {
    // Use our utility to check if we can animate
    if (this.canAnimate(selector)) {
      try {
        const elements = document.querySelectorAll(selector);
        gsap.from(elements, {
          opacity: 0,
          y: 20,
          duration: 0.5,
          stagger: 0.1,
          ease: 'power2.out',
          ...options
        });
      } catch (err) {
        console.warn('GSAP animation error:', err);
      }
    }
  },

  /**
   * Add hover effects to elements
   * @param {string} selector - CSS selector for target elements
   * @param {Object} options - GSAP animation options for hover effect
   */
  addHoverEffects: function(selector, options = {}) {
    // Use our utility to check if we can animate
    if (this.canAnimate(selector)) {
      try {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
          element.addEventListener('mouseenter', () => {
            gsap.to(element, {
              scale: 1.02,
              duration: 0.3,
              ease: 'power1.out',
              ...options
            });
          });
          
          element.addEventListener('mouseleave', () => {
            gsap.to(element, {
              scale: 1,
              duration: 0.3,
              ease: 'power1.out',
              ...options
            });
          });
        });
      } catch (err) {
        console.warn('GSAP hover effect error:', err);
      }
    }
  },

  /**
   * Animate notification or toast elements
   * @param {HTMLElement} element - Element to animate
   */
  animateNotification: function(element) {
    // Check if GSAP is available
    if (typeof gsap !== 'undefined' && element) {
      try {
        // Initial state
        gsap.set(element, { opacity: 0, y: -20 });
        
        // Animate in
        gsap.to(element, {
          opacity: 1,
          y: 0,
          duration: 0.5,
          ease: 'power2.out'
        });
        
        // Auto-remove after delay
        setTimeout(() => {
          gsap.to(element, {
            opacity: 0,
            y: -20,
            duration: 0.5,
            ease: 'power2.in',
            onComplete: () => {
              element.remove();
            }
          });
        }, 5000);
      } catch (err) {
        console.warn('GSAP notification animation error:', err);
      }
    }
  }
};

// Chart utilities
AstroBotUtils.charts = {
  /**
   * Create a responsive chart with proper sizing
   * @param {string} elementId - Canvas element ID
   * @param {string} type - Chart type (line, bar, pie, etc.)
   * @param {Object} data - Chart data
   * @param {Object} options - Chart options
   * @returns {Chart} Chart instance
   */
  createResponsiveChart: function(elementId, type, data, options = {}) {
    const element = document.getElementById(elementId);
    if (!element) {
      console.warn(`Canvas element not found: ${elementId}`);
      return null;
    }
    
    try {
      // Safely get the 2D context
      let context;
      try {
        context = element.getContext('2d');
      } catch (contextErr) {
        console.error(`Error getting canvas context for ${elementId}:`, contextErr);
        return null;
      }
      
      // Default options for responsive charts
      const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'top'
          },
          tooltip: {
            enabled: true
          }
        }
      };
      
      // Look for existing chart instance on this canvas and destroy it
      const existingChart = Chart.getChart(element);
      if (existingChart) {
        try {
          existingChart.destroy();
        } catch (destroyErr) {
          console.warn(`Failed to destroy existing chart on ${elementId}:`, destroyErr);
        }
      }
      
      // Create chart with merged options
      return new Chart(context, {
        type: type,
        data: data,
        options: { ...defaultOptions, ...options }
      });
    } catch (err) {
      console.error(`Error creating chart (${elementId}):`, err);
      return null;
    }
  },
  
  /**
   * Update chart data
   * @param {Chart} chart - Chart instance
   * @param {Object} newData - New data for the chart
   */
  updateChartData: function(chart, newData) {
    if (!chart) {
      console.warn('No chart instance provided for update');
      return;
    }
    
    try {
      chart.data = { ...chart.data, ...newData };
      chart.update();
    } catch (err) {
      console.error('Error updating chart:', err);
    }
  }
};

// Socket.io event utilities
AstroBotUtils.socket = {
  /**
   * Setup event handlers for socket.io events
   * @param {SocketIO.Socket} socket - Socket.io socket instance
   * @param {Object} handlers - Object mapping event names to handler functions
   */
  setupSocketEventHandlers: function(socket, handlers = {}) {
    if (!socket) {
      console.warn('No socket instance provided');
      return;
    }
    
    try {
      Object.entries(handlers).forEach(([event, handler]) => {
        socket.on(event, handler);
      });
      
      console.log('Socket event handlers registered successfully');
    } catch (err) {
      console.error('Error setting up socket event handlers:', err);
    }
  }
};

// Theme utilities
AstroBotUtils.theme = {
  /**
   * Get current theme from body class
   * @returns {string} Theme name ('light', 'dark', 'space', 'neon')
   */
  getCurrentTheme: function() {
    const bodyClasses = document.body.className;
    if (bodyClasses.includes('theme-dark')) return 'dark';
    if (bodyClasses.includes('theme-space')) return 'space';
    if (bodyClasses.includes('theme-neon')) return 'neon';
    return 'light';
  },
  
  /**
   * Get color scheme for the current theme
   * @returns {Object} Color scheme object
   */
  getThemeColors: function() {
    const theme = this.getCurrentTheme();
    
    const themeColors = {
      light: {
        primary: '#007bff',
        secondary: '#6c757d',
        success: '#28a745',
        info: '#17a2b8',
        warning: '#ffc107',
        danger: '#dc3545',
        purple: '#6f42c1',
        pink: '#e83e8c',
        orange: '#fd7e14'
      },
      dark: {
        primary: '#375a7f',
        secondary: '#6c757d',
        success: '#00bc8c',
        info: '#3498db',
        warning: '#f39c12',
        danger: '#e74c3c',
        purple: '#8c44ad',
        pink: '#e83e8c',
        orange: '#fd7e14'
      },
      space: {
        primary: '#7269ef',
        secondary: '#6c757d',
        success: '#06d6a0',
        info: '#3fc5f0',
        warning: '#ffd166',
        danger: '#ef476f',
        purple: '#9681eb',
        pink: '#e83e8c',
        orange: '#fd7e14'
      },
      neon: {
        primary: '#00eeff',
        secondary: '#6c757d',
        success: '#39ff14',
        info: '#00ffff',
        warning: '#ffff00',
        danger: '#ff0080',
        purple: '#bf00ff',
        pink: '#ff00ff',
        orange: '#ff8000'
      }
    };
    
    return themeColors[theme] || themeColors.light;
  }
};