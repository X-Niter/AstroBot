// Main JavaScript for AstroBot Dashboard

// Enable tooltips everywhere
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Add smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});

// Add active class to current page nav link
document.addEventListener('DOMContentLoaded', function() {
    const currentLocation = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (linkPath === currentLocation) {
            link.classList.add('active');
        }
    });
});

// Theme switcher (if implemented)
function toggleDarkMode() {
    document.body.classList.toggle('light-mode');
    
    // Store preference
    const isDarkMode = document.body.classList.contains('light-mode') ? 'light' : 'dark';
    localStorage.setItem('theme', isDarkMode);
}

// Load theme preference
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        document.body.classList.add('light-mode');
    }
});

// Format functions
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function formatTimeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHour = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHour / 24);
    const diffMonth = Math.floor(diffDay / 30);
    const diffYear = Math.floor(diffMonth / 12);
    
    if (diffYear > 0) {
        return diffYear + (diffYear === 1 ? " year ago" : " years ago");
    } else if (diffMonth > 0) {
        return diffMonth + (diffMonth === 1 ? " month ago" : " months ago");
    } else if (diffDay > 0) {
        return diffDay + (diffDay === 1 ? " day ago" : " days ago");
    } else if (diffHour > 0) {
        return diffHour + (diffHour === 1 ? " hour ago" : " hours ago");
    } else if (diffMin > 0) {
        return diffMin + (diffMin === 1 ? " minute ago" : " minutes ago");
    } else {
        return "just now";
    }
}

// Error handler
function handleFetchError(error, elementId, message) {
    console.error(error);
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <i class="fas fa-exclamation-circle me-2"></i>
                ${message || 'An error occurred while fetching data.'}
            </div>
        `;
    }
}

// Add fade-in animation for elements
document.addEventListener('DOMContentLoaded', function() {
    const fadeElements = document.querySelectorAll('.fade-in');
    fadeElements.forEach((element, index) => {
        setTimeout(() => {
            element.classList.add('visible');
        }, 100 * (index + 1));
    });
});