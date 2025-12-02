/**
 * AffineDrift - Interactive JavaScript
 * Handles smooth scrolling, navigation highlights, and interactive elements
 */

// Constants for scroll offsets and timing
// Matches scroll-margin-top: 140px defined in styles.css for page sections
const HEADER_OFFSET = 140; // Offset for smooth scrolling to account for fixed header
const TOC_SCROLL_OFFSET = 160; // Offset for active section detection in TOC
const TOC_SCROLL_DEBOUNCE_MS = 50; // Debounce delay for scroll events
const MAX_ID_GENERATION_ATTEMPTS = 100; // Safety limit for ID generation

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
                    const elementPosition = targetElement.getBoundingClientRect().top;
                    const offsetPosition = elementPosition + window.scrollY - HEADER_OFFSET;

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
    const navLinksContainer = document.querySelector('.nav-links');
    const sidebar = document.querySelector('.sidebar');
    const navContainer = document.querySelector('.top-nav .container');
    let navToggleButton;
    let sidebarToggleButton;
    let overlay;

    // Responsive breakpoints - match CSS media queries
    const NAV_BREAKPOINT = 768; // Matches @media (max-width: 768px) in styles.css
    const SIDEBAR_BREAKPOINT = 768; // Matches @media (max-width: 768px) in styles.css

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
    // Disabled on mobile to prevent content loading issues and improve performance
    const isMobile = window.innerWidth <= NAV_BREAKPOINT;
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (!isMobile && !prefersReducedMotion) {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px 0px 0px'
        };

        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    // Only apply animation if element doesn't already have opacity set
                    // Use getComputedStyle to check actual rendered opacity value
                    const computedOpacity = window.getComputedStyle(entry.target).opacity;
                    if (computedOpacity === '0') {
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
    } else {
        // On mobile, ensure all content is immediately visible
        const allSections = document.querySelectorAll('section');
        allSections.forEach(section => {
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
            section.style.visibility = 'visible';
        });
    }

    // Mobile menu toggle and sidebar toggle creation
    if (navContainer) {
        navToggleButton = document.createElement('button');
        navToggleButton.className = 'nav-toggle';
        navToggleButton.type = 'button';
        navToggleButton.setAttribute('aria-expanded', 'false');
        navToggleButton.setAttribute('aria-label', 'Toggle navigation menu');
        navToggleButton.textContent = 'Menu';

        sidebarToggleButton = document.createElement('button');
        sidebarToggleButton.className = 'sidebar-toggle';
        sidebarToggleButton.type = 'button';
        sidebarToggleButton.setAttribute('aria-expanded', 'false');
        sidebarToggleButton.setAttribute('aria-label', 'Toggle recent pages panel');
        sidebarToggleButton.textContent = 'History';

        const firstChild = navContainer.firstElementChild;
        navContainer.insertBefore(navToggleButton, firstChild);
        navContainer.insertBefore(sidebarToggleButton, firstChild);
    }

    function ensureOverlay() {
        if (overlay) return overlay;

        overlay = document.createElement('div');
        overlay.className = 'screen-overlay';
        overlay.setAttribute('aria-hidden', 'true');
        document.body.appendChild(overlay);

        overlay.addEventListener('click', () => {
            closeNavMenu();
            closeSidebar();
        });

        return overlay;
    }

    function updateOverlayState() {
        const navOpen = navLinksContainer && navLinksContainer.classList.contains('active') && window.innerWidth <= NAV_BREAKPOINT;
        const sidebarOpen = sidebar && sidebar.classList.contains('open') && window.innerWidth <= SIDEBAR_BREAKPOINT;
        const shouldShowOverlay = navOpen || sidebarOpen;

        if (!overlay && shouldShowOverlay) {
            ensureOverlay();
        }

        if (overlay) {
            overlay.classList.toggle('active', shouldShowOverlay);
        }

        document.body.classList.toggle('no-scroll', shouldShowOverlay);
    }

    function toggleNavMenu() {
        if (!navLinksContainer || !navToggleButton) return;
        const isActive = navLinksContainer.classList.toggle('active');
        navToggleButton.setAttribute('aria-expanded', isActive.toString());
        if (isActive) {
            ensureOverlay();
        }
        updateOverlayState();
    }

    function closeNavMenu() {
        if (!navLinksContainer || !navToggleButton) return;
        navLinksContainer.classList.remove('active');
        navToggleButton.setAttribute('aria-expanded', 'false');
        updateOverlayState();
    }

    if (navToggleButton && navLinksContainer) {
        navToggleButton.addEventListener('click', toggleNavMenu);

        navLinksContainer.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth <= NAV_BREAKPOINT) {
                    closeNavMenu();
                }
            });
        });
    }

    function toggleSidebar() {
        if (!sidebar || !sidebarToggleButton) return;
        const isOpen = sidebar.classList.toggle('open');
        sidebarToggleButton.setAttribute('aria-expanded', isOpen.toString());
        if (isOpen) {
            ensureOverlay();
        }
        updateOverlayState();
    }

    function closeSidebar() {
        if (!sidebar || !sidebarToggleButton) return;
        sidebar.classList.remove('open');
        sidebarToggleButton.setAttribute('aria-expanded', 'false');
        updateOverlayState();
    }

    if (sidebarToggleButton && sidebar) {
        sidebarToggleButton.addEventListener('click', toggleSidebar);
    }

    function handleResize() {
        if (window.innerWidth > NAV_BREAKPOINT) {
            closeNavMenu();
        }

        if (window.innerWidth > SIDEBAR_BREAKPOINT) {
            closeSidebar();
        }

        updateOverlayState();
    }

    window.addEventListener('resize', handleResize);

    document.addEventListener('keydown', event => {
        if (event.key === 'Escape') {
            closeNavMenu();
            closeSidebar();
        }
    });

    // Page history tracking for sidebar
    function updateHistorySidebar() {
        const historyList = document.getElementById('history-list');
        if (!historyList) return;

        // Constants
        const MAX_HISTORY_TITLE_LENGTH = 40;
        const MAX_HISTORY_ITEMS = 10;

        // Get history from localStorage
        let history = JSON.parse(localStorage.getItem('affinedrift_history') || '[]');
        
        // Get current page info with improved title extraction
        let pageTitle = document.title;
        // Handle different title formats
        if (pageTitle.includes(' - AffineDrift')) {
            pageTitle = pageTitle.replace(' - AffineDrift', '');
        } else if (pageTitle.startsWith('AffineDrift - ')) {
            pageTitle = pageTitle.replace('AffineDrift - ', '');
        } else if (pageTitle === 'AffineDrift') {
            pageTitle = 'Home';
        }
        
        const currentPage = {
            title: pageTitle,
            url: window.location.pathname.split('/').pop() || 'index.html',
            fullUrl: window.location.href
        };

        // Remove current page if it's already in history
        history = history.filter(item => item.url !== currentPage.url);
        
        // Add current page to front
        history.unshift(currentPage);
        
        // Keep only last N items
        history = history.slice(0, MAX_HISTORY_ITEMS);
        
        // Save back to localStorage
        localStorage.setItem('affinedrift_history', JSON.stringify(history));
        
        // Update sidebar display
        // Filter to only show articles (exclude navigation pages)
        const excludedPages = [
            'index.html', 'home.html',
            'articles.html', 'article.html',
            'resources.html', 'tools.html', 'programs.html',
            'contact.html', 'about.html',
            'research-reviews.html', 'book-reviews.html',
            'daydreams-doodles.html', 'daydreams.html', 'doodles.html'
        ];
        
        // Filter out current page and non-article pages
        const displayHistory = history.filter(item => 
            item.url !== currentPage.url && 
            !excludedPages.includes(item.url.toLowerCase()) &&
            !item.url.match(/^(tools|contact|about|resources|articles|research-reviews|book-reviews|daydreams)/i)
        );
        
        if (displayHistory.length === 0) {
            historyList.innerHTML = '<li class="history-empty">No recent articles yet</li>';
        } else {
            historyList.innerHTML = displayHistory.map(item => {
                const displayTitle = item.title.length > MAX_HISTORY_TITLE_LENGTH 
                    ? item.title.substring(0, MAX_HISTORY_TITLE_LENGTH) + '...' 
                    : item.title;
                return `<li><a href="${item.url}">${displayTitle}</a></li>`;
            }).join('');
        }
    }

    // Initialize history sidebar
    updateHistorySidebar();

    // Table of Contents functionality
    function generateTableOfContents() {
        const sidebar = document.getElementById('history-sidebar');
        if (!sidebar) return;

        const sidebarNav = sidebar.querySelector('.sidebar-nav');
        if (!sidebarNav) return;

        // Find or create TOC section
        let tocSection = sidebar.querySelector('.sidebar-toc');
        if (!tocSection) {
            tocSection = document.createElement('div');
            tocSection.className = 'sidebar-section sidebar-toc';
            tocSection.innerHTML = '<h3 class="sidebar-heading">On This Page</h3><ul class="sidebar-links" id="toc-list"></ul>';
            sidebarNav.insertBefore(tocSection, sidebarNav.firstChild);
        }

        const tocList = document.getElementById('toc-list');
        if (!tocList) return;

        // Clear existing TOC
        tocList.innerHTML = '';

        // Find all section headings (h2 with IDs or page-section divs with IDs)
        const sections = [];
        const usedIds = new Set(); // Track used IDs to prevent duplicates
        
        // Look for page-section divs with IDs
        const pageSections = document.querySelectorAll('.page-section[id], section[id]');
        pageSections.forEach(section => {
            const heading = section.querySelector('.section-heading, h2, h1');
            if (heading && section.id) {
                sections.push({
                    id: section.id,
                    text: heading.textContent.trim(),
                    element: section,
                    level: 2
                });
                usedIds.add(section.id);
            }
        });

        // Also look for article-category containers (use container ID, not heading ID)
        const categories = document.querySelectorAll('.article-category');
        categories.forEach((category, categoryIndex) => {
            const heading = category.querySelector('h2');
            if (heading) {
                // Use container ID if it exists, otherwise generate one
                let id = category.id;
                if (!id) {
                    // Generate ID from heading text, ensuring uniqueness
                    let baseId = heading.textContent.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
                    id = baseId;
                    let counter = 1;
                    while (usedIds.has(id) && counter < MAX_ID_GENERATION_ATTEMPTS) {
                        id = `${baseId}-${counter}`;
                        counter++;
                    }
                    if (usedIds.has(id)) {
                        // Fallback: use timestamp to ensure uniqueness
                        id = `${baseId}-${Date.now()}`;
                    }
                    category.id = id;
                } else if (usedIds.has(id)) {
                    // If ID already exists, generate a new unique one
                    let baseId = id;
                    let counter = 1;
                    while (usedIds.has(id) && counter < MAX_ID_GENERATION_ATTEMPTS) {
                        id = `${baseId}-${counter}`;
                        counter++;
                    }
                    if (usedIds.has(id)) {
                        // Fallback: use timestamp to ensure uniqueness
                        id = `${baseId}-${Date.now()}`;
                    }
                    category.id = id;
                }
                usedIds.add(id);
                sections.push({
                    id: id,
                    text: heading.textContent.trim(),
                    element: category, // Use container element, not heading
                    level: 2
                });
            }
        });

        // If no sections found, look for any h2 headings
        if (sections.length === 0) {
            const h2s = document.querySelectorAll('h2');
            h2s.forEach((h2, index) => {
                let id = h2.id;
                if (!id || usedIds.has(id)) {
                    // Generate unique ID with safety limit
                    let counter = 1;
                    let attempts = 0;
                    do {
                        id = `section-${index + 1}${counter > 1 ? `-${counter}` : ''}`;
                        counter++;
                        attempts++;
                    } while (usedIds.has(id) && attempts < MAX_ID_GENERATION_ATTEMPTS);
                    // If we hit the max attempts, assign a fallback ID
                    if (usedIds.has(id)) {
                        id = `section-${index + 1}-unique-${Math.random().toString(36).substr(2, 6)}`;
                    }
                    h2.id = id;
                }
                usedIds.add(id);
                sections.push({
                    id: id,
                    text: h2.textContent.trim(),
                    element: h2,
                    level: 2
                });
            });
        }

        // Generate TOC links
        if (sections.length > 0) {
            sections.forEach(section => {
                const li = document.createElement('li');
                const a = document.createElement('a');
                a.href = `#${section.id}`;
                a.textContent = section.text;
                a.className = `toc-level-${section.level}`;
                a.addEventListener('click', function(e) {
                    e.preventDefault();
                    const target = document.getElementById(section.id);
                    if (target) {
                        const elementPosition = target.getBoundingClientRect().top;
                        const offsetPosition = elementPosition + window.scrollY - HEADER_OFFSET;
                        window.scrollTo({
                            top: offsetPosition,
                            behavior: 'smooth'
                        });
                    }
                });
                li.appendChild(a);
                tocList.appendChild(li);
            });
        } else {
            // Hide TOC if no sections found
            tocSection.style.display = 'none';
        }

        // Highlight active section on scroll
        function highlightActiveSection() {
            const scrollPosition = window.scrollY + TOC_SCROLL_OFFSET;
            const tocLinks = tocList.querySelectorAll('a');
            
            sections.forEach((section, index) => {
                const element = section.element;
                if (!element) return;
                
                const rect = element.getBoundingClientRect();
                const elementTop = rect.top + window.scrollY;
                const elementBottom = elementTop + rect.height;
                
                if (index < tocLinks.length) {
                    tocLinks[index].classList.remove('active');
                    
                    if (scrollPosition >= elementTop && scrollPosition < elementBottom) {
                        tocLinks[index].classList.add('active');
                    }
                }
            });
        }

        // Update on scroll
        let tocScrollTimeout;
        window.addEventListener('scroll', function() {
            if (tocScrollTimeout) {
                clearTimeout(tocScrollTimeout);
            }
            tocScrollTimeout = setTimeout(highlightActiveSection, TOC_SCROLL_DEBOUNCE_MS);
        });

        // Initial highlight
        highlightActiveSection();
    }

    // Generate TOC after page loads
    generateTableOfContents();

    // Lazy load images
    if ('loading' in HTMLImageElement.prototype) {
        const images = document.querySelectorAll('img[src]');
        images.forEach(img => {
            if (!img.hasAttribute('loading')) {
                img.setAttribute('loading', 'lazy');
            }
        });
    }

    // Accordion functionality
    const accordionHeaders = document.querySelectorAll('.accordion-header');
    accordionHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            const content = this.nextElementSibling;
            
            // Toggle current accordion
            this.setAttribute('aria-expanded', !isExpanded);
        });
    });

    // Make repository dropdown links open in new tabs
    const repositoryLinks = document.querySelectorAll('.navbar-nav a[href^="https://github.com"]');
    repositoryLinks.forEach(link => {
        link.setAttribute('target', '_blank');
        link.setAttribute('rel', 'noopener noreferrer');
    });

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
