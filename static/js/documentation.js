// Documentation JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize syntax highlighting if available
    if (typeof hljs !== 'undefined') {
        document.querySelectorAll('pre code').forEach((el) => {
            hljs.highlightElement(el);
        });
    }
    
    // Add table classes for styling
    document.querySelectorAll('.doc-content table').forEach((table) => {
        if (!table.classList.contains('table')) {
            table.classList.add('table', 'table-striped', 'table-bordered');
        }
    });
    
    // Setup smooth scrolling for in-page links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                
                // Update URL hash without page jump
                history.pushState(null, null, targetId);
            }
        });
    });
    
    // Highlight active sidebar link based on current page
    const currentPath = window.location.pathname;
    document.querySelectorAll('.doc-sidebar .nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
    
    // Setup documentation feedback
    setupDocFeedback();
    
    // Initialize copy to clipboard functionality
    setupCodeCopy();
    
    // Initialize table of contents if present
    generateTableOfContents();
});

/**
 * Sets up the documentation feedback functionality
 */
function setupDocFeedback() {
    const feedbackContainer = document.querySelector('.doc-feedback');
    if (!feedbackContainer) return;
    
    const yesBtn = feedbackContainer.querySelector('.feedback-yes');
    const noBtn = feedbackContainer.querySelector('.feedback-no');
    const feedbackForm = feedbackContainer.querySelector('.feedback-form');
    
    if (yesBtn) {
        yesBtn.addEventListener('click', function() {
            // Show thank you message
            feedbackContainer.innerHTML = '<div class="alert alert-success">Thank you for your feedback!</div>';
            
            // Send feedback to server
            sendFeedback({
                page: window.location.pathname,
                helpful: true
            });
        });
    }
    
    if (noBtn) {
        noBtn.addEventListener('click', function() {
            // Show feedback form
            if (feedbackForm) {
                feedbackForm.classList.remove('d-none');
            }
        });
    }
    
    if (feedbackForm) {
        feedbackForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const commentInput = feedbackForm.querySelector('#feedback-comment');
            const comment = commentInput ? commentInput.value : '';
            
            // Send feedback to server
            sendFeedback({
                page: window.location.pathname,
                helpful: false,
                comment: comment
            });
            
            // Show thank you message
            feedbackContainer.innerHTML = '<div class="alert alert-success">Thank you for your feedback! We\'ll use it to improve our documentation.</div>';
        });
    }
}

/**
 * Sends feedback to the server
 * @param {Object} data - Feedback data
 */
function sendFeedback(data) {
    fetch('/api/documentation/feedback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .catch(error => {
        console.error('Error sending feedback:', error);
    });
}

/**
 * Sets up copy to clipboard functionality for code blocks
 */
function setupCodeCopy() {
    document.querySelectorAll('.syntax-highlight').forEach(block => {
        // Skip if already has copy button
        if (block.querySelector('.copy-btn')) return;
        
        const button = document.createElement('button');
        button.className = 'btn btn-sm btn-light copy-btn';
        button.innerHTML = '<i class="fas fa-copy"></i>';
        button.style.position = 'absolute';
        button.style.top = '0.5rem';
        button.style.right = '0.5rem';
        button.title = 'Copy to clipboard';
        
        block.style.position = 'relative';
        block.appendChild(button);
        
        button.addEventListener('click', () => {
            const code = block.querySelector('code');
            if (!code) return;
            
            // Copy code to clipboard
            navigator.clipboard.writeText(code.textContent)
                .then(() => {
                    // Indicate success
                    button.innerHTML = '<i class="fas fa-check"></i>';
                    button.classList.add('btn-success');
                    button.classList.remove('btn-light');
                    
                    // Reset after 2 seconds
                    setTimeout(() => {
                        button.innerHTML = '<i class="fas fa-copy"></i>';
                        button.classList.add('btn-light');
                        button.classList.remove('btn-success');
                    }, 2000);
                })
                .catch(err => {
                    console.error('Could not copy text: ', err);
                    
                    // Indicate failure
                    button.innerHTML = '<i class="fas fa-times"></i>';
                    button.classList.add('btn-danger');
                    button.classList.remove('btn-light');
                    
                    // Reset after 2 seconds
                    setTimeout(() => {
                        button.innerHTML = '<i class="fas fa-copy"></i>';
                        button.classList.add('btn-light');
                        button.classList.remove('btn-danger');
                    }, 2000);
                });
        });
    });
}

/**
 * Generates a table of contents based on headings
 */
function generateTableOfContents() {
    const tocContainer = document.querySelector('.doc-toc');
    if (!tocContainer) return;
    
    const content = document.querySelector('.doc-content');
    if (!content) return;
    
    // Get all headings (h2, h3) in the content
    const headings = content.querySelectorAll('h2, h3');
    if (headings.length === 0) return;
    
    // Create TOC list
    const toc = document.createElement('ul');
    toc.className = 'list-unstyled';
    
    headings.forEach((heading, index) => {
        // Add ID to heading if it doesn't have one
        if (!heading.id) {
            heading.id = `heading-${index}`;
        }
        
        const listItem = document.createElement('li');
        const link = document.createElement('a');
        link.href = `#${heading.id}`;
        link.textContent = heading.textContent;
        
        // Indent h3 headings
        if (heading.tagName === 'H3') {
            listItem.style.paddingLeft = '1rem';
            listItem.style.fontSize = '0.9rem';
        }
        
        listItem.appendChild(link);
        toc.appendChild(listItem);
    });
    
    // Add title and toc to container
    const title = document.createElement('h5');
    title.textContent = 'Table of Contents';
    
    tocContainer.innerHTML = '';
    tocContainer.appendChild(title);
    tocContainer.appendChild(toc);
}