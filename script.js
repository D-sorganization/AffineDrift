/**
 * AffineDrift - Interactive JavaScript
 * Handles smooth scrolling, navigation highlights, and interactive elements
 */

// Smooth scrolling for navigation links
document.addEventListener('DOMContentLoaded', function() {
    // Smooth scroll for anchor links
    const links = document.querySelectorAll('a[href^="#"]');

    links.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');

            // Only handle internal anchors
            if (href !== '#' && href.length > 1) {
                const targetId = href.substring(1);
                const targetElement = document.getElementById(targetId);

                if (targetElement) {
                    e.preventDefault();

                    // Smooth scroll to target
                    const headerOffset = 80; // Account for sticky header
                    const elementPosition = targetElement.getBoundingClientRect().top;
                    const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                    window.scrollTo({
                        top: offsetPosition,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // Highlight active navigation link on scroll
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-links a[href^="#"]');

    function highlightNavigation() {
        const scrollPosition = window.scrollY + 150;

        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            const sectionId = section.getAttribute('id');

            if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                navLinks.forEach(link => {
                    link.style.opacity = '0.8';
                    if (link.getAttribute('href') === `#${sectionId}`) {
                        link.style.opacity = '1';
                    }
                });
            }
        });
    }

    // Debounce scroll event for performance
    let scrollTimeout;
    window.addEventListener('scroll', function() {
        if (scrollTimeout) {
            clearTimeout(scrollTimeout);
        }
        scrollTimeout = setTimeout(highlightNavigation, 50);
    });

    // Initial call
    highlightNavigation();

    // Add fade-in animation for sections on scroll (only if not already visible)
    // Content is visible by default - animation is optional enhancement
    const observerOptions = {
        threshold: 0.01,
        rootMargin: '0px 0px 0px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Only apply animation if element doesn't already have opacity set
                // Use getComputedStyle to check actual rendered opacity value
                const computedOpacity = window.getComputedStyle(entry.target).opacity;
                if (computedOpacity === '0' || computedOpacity === '') {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            }
        });
    }, observerOptions);

    // Observe sections for fade-in effect (only apply to sections that should animate)
    // Don't hide content initially - let it be visible
    const sectionsToAnimate = document.querySelectorAll('section:not(.page-header):not(.article-section)');
    sectionsToAnimate.forEach(section => {
        // Only animate if section is below the fold
        const rect = section.getBoundingClientRect();
        if (rect.top > window.innerHeight) {
            section.style.opacity = '0';
            section.style.transform = 'translateY(20px)';
            section.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            observer.observe(section);
        } else {
            // Content above the fold should be immediately visible
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
        }
    });

    // Mobile menu toggle (for future implementation)
    const navToggle = document.querySelector('.nav-toggle');
    if (navToggle) {
        navToggle.addEventListener('click', function() {
            const navLinks = document.querySelector('.nav-links');
            navLinks.classList.toggle('active');
        });
    }

    // Log page load for analytics (optional)
    console.log('AffineDrift loaded successfully');
    console.log('Mathematical notation rendering via MathJax');
});

// Utility function for future features
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Export for potential module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        scrollToTop
    };
}
