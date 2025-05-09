/**
 * AstroBot AI - Utility Functions
 * Contains shared functionality for Chart.js, Socket.IO, and GSAP animations
 */

// -----------------------------
// Chart.js Utilities
// -----------------------------

/**
 * Creates and returns a Chart.js configuration with AstroBot theme styling
 * @param {string} type - Chart type (line, bar, doughnut, etc.)
 * @param {Object} data - Chart data object with labels and datasets
 * @param {Object} options - Additional chart options
 * @returns {Object} Chart.js configuration object
 */
function createChartConfig(type, data, options = {}) {
  // Default theme colors that match our application themes
  const defaultColors = {
    light: {
      primary: '#007bff',
      secondary: '#6c757d',
      success: '#28a745',
      danger: '#dc3545',
      background: '#ffffff',
      text: '#212529'
    },
    dark: {
      primary: '#375a7f',
      secondary: '#444444',
      success: '#00bc8c',
      danger: '#e74c3c',
      background: '#222222',
      text: '#ffffff'
    },
    space: {
      primary: '#6f42c1',
      secondary: '#20c997',
      success: '#17a2b8',
      danger: '#fd7e14',
      background: '#121212',
      text: '#e1e1e1'
    },
    neon: {
      primary: '#ff00ff',
      secondary: '#00ffff',
      success: '#00ff00',
      danger: '#ff0000',
      background: '#1e1e24',
      text: '#ffffff'
    },
    contrast: {
      primary: '#ffcc00',
      secondary: '#ffffff',
      success: '#00ff00',
      danger: '#ff0000',
      background: '#000000',
      text: '#ffffff'
    }
  };

  // Get current theme
  const currentTheme = document.documentElement.getAttribute('data-bs-theme') || 'light';
  const colors = defaultColors[currentTheme];

  // Apply theme-specific styling to chart
  const themeOptions = {
    color: colors.text,
    backgroundColor: colors.background,
    borderColor: colors.primary,
    plugins: {
      legend: {
        labels: {
          color: colors.text
        }
      },
      tooltip: {
        backgroundColor: colors.background,
        titleColor: colors.text,
        bodyColor: colors.text,
        borderColor: colors.primary,
        borderWidth: 1
      }
    },
    scales: {
      x: {
        grid: {
          color: colors.text + '22' // Add transparency
        },
        ticks: {
          color: colors.text
        }
      },
      y: {
        grid: {
          color: colors.text + '22' // Add transparency
        },
        ticks: {
          color: colors.text
        }
      }
    }
  };

  // Merge default options with user options
  const mergedOptions = {...themeOptions, ...options};

  return {
    type,
    data,
    options: mergedOptions
  };
}

/**
 * Creates a responsive Chart.js chart that adapts to theme changes
 * @param {string} canvasId - HTML canvas element ID
 * @param {string} type - Chart type (line, bar, doughnut, etc.)
 * @param {Object} data - Chart data object with labels and datasets
 * @param {Object} options - Additional chart options
 * @returns {Chart} The created Chart.js instance
 */
function createResponsiveChart(canvasId, type, data, options = {}) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) {
    console.error(`Canvas element with ID "${canvasId}" not found`);
    return null;
  }

  const config = createChartConfig(type, data, options);
  const chart = new Chart(canvas, config);

  // Update chart when theme changes
  document.addEventListener('theme-changed', () => {
    chart.destroy();
    const newConfig = createChartConfig(type, data, options);
    new Chart(canvas, newConfig);
  });

  return chart;
}

// -----------------------------
// Socket.IO Utilities
// -----------------------------

/**
 * Creates and configures a Socket.IO connection
 * @param {string} namespace - Optional Socket.IO namespace
 * @returns {Socket} Configured Socket.IO connection
 */
function createSocketConnection(namespace = '') {
  const socket = io(namespace, {
    transports: ['websocket'],
    reconnection: true,
    reconnectionAttempts: 5,
    reconnectionDelay: 1000
  });

  socket.on('connect', () => {
    console.log('Socket.IO connected!');
    // Dispatch event that components can listen for
    document.dispatchEvent(new CustomEvent('socket-connected'));
  });

  socket.on('disconnect', () => {
    console.log('Socket.IO disconnected');
    document.dispatchEvent(new CustomEvent('socket-disconnected'));
  });

  socket.on('connect_error', (err) => {
    console.error('Socket.IO connection error:', err);
  });

  return socket;
}

/**
 * Utility function to create event listeners for Socket.IO events
 * @param {Socket} socket - Socket.IO connection
 * @param {Object} eventHandlers - Map of event names to handler functions
 */
function setupSocketEventHandlers(socket, eventHandlers) {
  if (!socket) {
    console.error('Socket connection is required');
    return;
  }

  // Register all event handlers
  Object.entries(eventHandlers).forEach(([event, handler]) => {
    socket.on(event, handler);
  });

  // Return an unsubscribe function
  return function unsubscribe() {
    Object.keys(eventHandlers).forEach(event => {
      socket.off(event);
    });
  };
}

// -----------------------------
// GSAP Animation Utilities
// -----------------------------

/**
 * Creates a staggered entrance animation for multiple elements
 * @param {string} selector - CSS selector for target elements
 * @param {Object} options - Animation options
 */
function animateEntrance(selector, options = {}) {
  const defaults = {
    y: 20,
    opacity: 0,
    duration: 0.5,
    stagger: 0.1,
    ease: 'power2.out',
    delay: 0.2
  };

  const config = {...defaults, ...options};
  
  return gsap.from(selector, config);
}

/**
 * Animates transitions between pages or sections
 * @param {string} outSelector - Elements to animate out
 * @param {string} inSelector - Elements to animate in
 * @param {Function} callback - Function to call after out animation completes
 */
function animatePageTransition(outSelector, inSelector, callback) {
  // Timeline for sequence control
  const tl = gsap.timeline();
  
  // Animate out current elements
  tl.to(outSelector, {
    opacity: 0,
    y: -20,
    duration: 0.3,
    stagger: 0.05,
    ease: 'power1.in'
  });
  
  // Execute callback (like loading new content)
  tl.call(() => {
    if (typeof callback === 'function') {
      callback();
    }
  });
  
  // Animate in new elements
  tl.from(inSelector, {
    opacity: 0,
    y: 20,
    duration: 0.4,
    stagger: 0.1,
    ease: 'power2.out'
  });
  
  return tl;
}

/**
 * Adds hover animation effects to elements
 * @param {string} selector - CSS selector for elements
 * @param {Object} hoverOptions - GSAP options for hover state
 */
function addHoverEffects(selector, hoverOptions = {}) {
  const elements = document.querySelectorAll(selector);
  
  const defaults = {
    scale: 1.05,
    duration: 0.3,
    ease: 'power1.out'
  };
  
  const config = {...defaults, ...hoverOptions};
  
  elements.forEach(element => {
    element.addEventListener('mouseenter', () => {
      gsap.to(element, config);
    });
    
    element.addEventListener('mouseleave', () => {
      gsap.to(element, {
        scale: 1,
        duration: config.duration,
        ease: config.ease
      });
    });
  });
}

/**
 * Creates a notification animation
 * @param {HTMLElement} element - Element to animate
 * @param {Object} options - Animation options
 */
function animateNotification(element, options = {}) {
  const defaults = {
    y: -20,
    opacity: 1,
    duration: 0.5,
    ease: 'elastic.out(1, 0.5)',
    onComplete: () => {
      setTimeout(() => {
        gsap.to(element, {
          opacity: 0,
          y: -10,
          duration: 0.3,
          ease: 'power3.in',
          onComplete: () => element.remove()
        });
      }, 3000);
    }
  };
  
  const config = {...defaults, ...options};
  
  return gsap.fromTo(element, 
    { y: 0, opacity: 0 },
    config
  );
}

// Export utilities
window.AstroBotUtils = {
  charts: {
    createChartConfig,
    createResponsiveChart
  },
  socket: {
    createSocketConnection,
    setupSocketEventHandlers
  },
  animation: {
    animateEntrance,
    animatePageTransition,
    addHoverEffects,
    animateNotification
  }
};