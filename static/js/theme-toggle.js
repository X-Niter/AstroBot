/**
 * AstroBot AI - Theme Toggle Script
 * 
 * Manages the theme toggle button functionality.
 * This script is a simpler version of the ThemeManager
 * specifically for the toggle button in the navigation.
 */

document.addEventListener('DOMContentLoaded', () => {
  const themeToggle = document.getElementById('theme-toggle');
  const moonIcon = document.querySelector('.theme-dark-icon');
  const sunIcon = document.querySelector('.theme-light-icon');
  const htmlElement = document.documentElement;
  
  // Function to toggle between light and dark theme
  function toggleTheme() {
    // Check if we're in dark mode
    const isDarkMode = htmlElement.classList.contains('dark');
    
    // If we're in dark mode, switch to light
    if (isDarkMode) {
      htmlElement.classList.remove('dark');
      moonIcon.classList.add('hidden');
      sunIcon.classList.remove('hidden');
      localStorage.setItem('theme', 'light');
      
      // Remove any premium theme class if present
      const themeClasses = Array.from(htmlElement.classList).filter(cls => cls.startsWith('theme-'));
      themeClasses.forEach(cls => htmlElement.classList.remove(cls));
      
      // Update data attributes
      document.body.setAttribute('data-theme', 'light');
    }
    // If we're in light mode, switch to dark
    else {
      htmlElement.classList.add('dark');
      moonIcon.classList.remove('hidden');
      sunIcon.classList.add('hidden');
      localStorage.setItem('theme', 'dark');
      
      // Remove any premium theme class if present
      const themeClasses = Array.from(htmlElement.classList).filter(cls => cls.startsWith('theme-'));
      themeClasses.forEach(cls => htmlElement.classList.remove(cls));
      
      // Update data attributes
      document.body.setAttribute('data-theme', 'dark');
    }
    
    // Dispatch custom event for other components to react
    window.dispatchEvent(new CustomEvent('theme-changed', { 
      detail: { 
        theme: isDarkMode ? 'light' : 'dark',
        isDark: !isDarkMode
      } 
    }));
  }
  
  // Set up event listener for theme toggle click
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      // Apply transition class to body for smooth theme change
      document.body.classList.add('theme-transition');
      
      // Toggle the theme
      toggleTheme();
      
      // Remove transition class after transition completes
      setTimeout(() => {
        document.body.classList.remove('theme-transition');
      }, 400); // Duration should match CSS transition
    });
  }
  
  // Initialize theme based on stored preference or OS preference
  function initializeTheme() {
    const storedTheme = localStorage.getItem('theme');
    const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const currentTheme = storedTheme || (prefersDarkMode ? 'dark' : 'light');
    
    if (currentTheme === 'dark') {
      htmlElement.classList.add('dark');
      if (moonIcon && sunIcon) {
        moonIcon.classList.remove('hidden');
        sunIcon.classList.add('hidden');
      }
    } else {
      htmlElement.classList.remove('dark');
      if (moonIcon && sunIcon) {
        moonIcon.classList.add('hidden');
        sunIcon.classList.remove('hidden');
      }
    }
    
    // Check for premium themes
    const premiumThemes = ['space', 'neon', 'contrast'];
    if (premiumThemes.includes(currentTheme)) {
      htmlElement.classList.add(`theme-${currentTheme}`);
      htmlElement.classList.add('dark'); // Premium themes are dark by default
    }
  }
  
  // Initialize theme on page load
  initializeTheme();
  
  // Listen for OS theme changes
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
    const storedTheme = localStorage.getItem('theme');
    if (!storedTheme) {
      if (e.matches) {
        htmlElement.classList.add('dark');
        if (moonIcon && sunIcon) {
          moonIcon.classList.remove('hidden');
          sunIcon.classList.add('hidden');
        }
      } else {
        htmlElement.classList.remove('dark');
        if (moonIcon && sunIcon) {
          moonIcon.classList.add('hidden');
          sunIcon.classList.remove('hidden');
        }
      }
    }
  });
});