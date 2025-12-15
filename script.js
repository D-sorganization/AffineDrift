/**
 * AffineDrift - Interactive JavaScript
 * Handles smooth scrolling, navigation highlights, and interactive elements
 */

// Constants for scroll offsets and timing
// Note: Uses --scroll-offset not --header-offset because:
// - --header-offset is for sidebar positioning (top: 120px)
// - --scroll-offset is for scroll behavior (scroll-margin-top: 140px)
// JS smooth scrolling must match CSS scroll-margin-top for consistency
// Fetch offset from CSS variable or default to 140
const getScrollOffset = () => {
    if (typeof window !== 'undefined') {
        const value = getComputedStyle(document.documentElement).getPropertyValue('--scroll-offset');
        return value ? parseInt(value) : 140;
    }
    return 140;
};
const HEADER_OFFSET = getScrollOffset(); // Smooth scrolling offset (matches CSS --scroll-offset)
const TOC_SCROLL_OFFSET = HEADER_OFFSET; // Active section detection offset
const TOC_SCROLL_DEBOUNCE_MS = 50; // Debounce delay for scroll events
const MAX_ID_GENERATION_ATTEMPTS = 100; // Safety limit for ID generation

// Helper function to generate unique IDs
function generateUniqueId(text, usedIds) {
    let baseId = text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
    if (!baseId) baseId = 'section'; // Fallback for empty text

    let id = baseId;
    let counter = 1;

    // First try base ID
    if (!usedIds.has(id)) {
        return id;
    }

    // Try incrementing counter
    while (usedIds.has(id) && counter < MAX_ID_GENERATION_ATTEMPTS) {
        id = `${baseId}-${counter}`;
        counter++;
    }

    // Fallback if still colliding
    if (usedIds.has(id)) {
        id = `${baseId}-${Date.now()}`;
    }

    return id;
}

// Smooth scrolling for navigation links
document.addEventListener('DOMContentLoaded', function () {
    // Shared Scroll Event Manager
    const scrollHandlers = {
        debounce: [],
        raf: []
    };
    let scrollTimeout;
    let ticking = false;

    window.addEventListener('scroll', () => {
        // High frequency updates (rAF)
        if (!ticking) {
            window.requestAnimationFrame(() => {
                scrollHandlers.raf.forEach(handler => {
                    try { handler(); } catch(e) { console.error(e); }
                });
                ticking = false;
            });
            ticking = true;
        }

        // Low frequency updates (Debounced)
        if (scrollTimeout) {
            clearTimeout(scrollTimeout);
        }
        scrollTimeout = setTimeout(() => {
            scrollHandlers.debounce.forEach(handler => {
                try { handler(); } catch(e) { console.error(e); }
            });
        }, TOC_SCROLL_DEBOUNCE_MS);
    }, { passive: true });

    // Shared Resize Event Manager (Performance Optimization)
    // Uses ResizeObserver to robustly detect layout changes and update caches
    const resizeHandlers = [];
    let resizeTimeout;

    const resizeObserver = new ResizeObserver((entries) => {
        // Debounce resize updates
        if (resizeTimeout) clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            resizeHandlers.forEach(handler => {
                try { handler(); } catch(e) { console.error(e); }
            });
        }, 100);
    });

    // Observe body for layout changes
    resizeObserver.observe(document.body);


    // Smooth scroll for anchor links (Event Delegation)
    // Replaces individual event listeners for better performance and handling dynamic content
    document.addEventListener('click', function (e) {
        const link = e.target.closest('a[href^="#"]');
        if (link) {
            const href = link.getAttribute('href');

            // Only handle internal anchors
            if (href && href !== '#' && href.length > 1) {
                // Check if this is a bootstrap tab/collapse toggle (don't interfere)
                if (link.hasAttribute('data-bs-toggle') || link.hasAttribute('data-toggle')) {
                    return;
                }

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
        }
    });

    // Highlight active navigation link on scroll for Quarto/Bootstrap navbar
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.navbar-nav a.nav-link[href^="#"]');
    const navbarCollapse = document.getElementById('navbarCollapse');

    if (navLinks.length > 0 && sections.length > 0) {
        // Cache for section positions to avoid layout thrashing on scroll
        let navSectionCache = [];

        function updateNavCache() {
            // Update cache with current positions
            navSectionCache = Array.from(sections).map(section => {
                const rect = section.getBoundingClientRect();
                const scrollTop = window.scrollY;
                return {
                    id: section.getAttribute('id'),
                    top: rect.top + scrollTop,
                    bottom: rect.top + scrollTop + rect.height
                };
            });
        }

        // Register to resize manager
        resizeHandlers.push(updateNavCache);
        // Initial update
        updateNavCache();

        function highlightNavigation() {
            const scrollPosition = window.scrollY + 150;

            // Use cached values instead of accessing DOM properties
            navSectionCache.forEach(section => {
                if (scrollPosition >= section.top && scrollPosition < section.bottom) {
                    navLinks.forEach(link => {
                        link.classList.toggle('active', link.getAttribute('href') === `#${section.id}`);
                    });
                }
            });
        }

        // Register to shared scroll manager
        scrollHandlers.debounce.push(highlightNavigation);

        highlightNavigation();

        // Note: Navbar collapse logic is handled by Bootstrap, but if we need custom logic:
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (navbarCollapse && navbarCollapse.classList.contains('show')) {
                    const collapseInstance = window.bootstrap?.Collapse?.getInstance?.(navbarCollapse);
                    if (collapseInstance) {
                        collapseInstance.hide();
                    } else {
                        navbarCollapse.classList.remove('show');
                    }
                }
            });
        });
    }

    // Add fade-in animation for sections on scroll (only if not already visible)
    // Content is visible by default - animation is optional enhancement
    // Disabled on mobile to prevent content loading issues and improve performance
    const NAV_BREAKPOINT = 768; // Matches @media (max-width: 768px) in styles.css
    const isMobile = window.innerWidth <= NAV_BREAKPOINT;
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (!isMobile && !prefersReducedMotion) {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px 0px 0px'
        };

        const observer = new IntersectionObserver(function (entries) {
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

    // Navigation collapsing and sidebar overlays are handled by Quarto's Bootstrap navbar,
    // so legacy toggle logic targeting `.top-nav`/`.nav-links` has been removed.

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
            historyList.textContent = '';
            const li = document.createElement('li');
            li.className = 'history-empty';
            li.textContent = 'No recent articles yet';
            historyList.appendChild(li);
        } else {
            historyList.textContent = '';
            displayHistory.forEach(item => {
                const li = document.createElement('li');
                const a = document.createElement('a');
                a.href = item.url;
                const displayTitle = item.title.length > MAX_HISTORY_TITLE_LENGTH
                    ? item.title.substring(0, MAX_HISTORY_TITLE_LENGTH) + '...'
                    : item.title;
                a.textContent = displayTitle;
                li.appendChild(a);
                historyList.appendChild(li);
            });
        }
    }

    // Initialize history sidebar
    updateHistorySidebar();

    // Table of Contents functionality
    function generateTableOfContents() {
        // Look for left-sidebar (for .qmd pages with standard-page-layout)
        const leftSidebar = document.querySelector('.left-sidebar');

        // Fallback to history-sidebar for pages without left-sidebar (legacy pages)
        const sidebar = leftSidebar || document.getElementById('history-sidebar');
        if (!sidebar) return;

        // For left-sidebar pages, add TOC section to the left-sidebar
        if (leftSidebar) {
            // Find or create TOC section in left-sidebar
            let tocSection = leftSidebar.querySelector('.sidebar-toc');
            if (!tocSection) {
                tocSection = document.createElement('div');
                tocSection.className = 'sidebar-toc';
                tocSection.innerHTML = '<h3 class="sidebar-heading">On This Page</h3><ul class="sidebar-links" id="toc-list"></ul>';
                // Insert after the existing toc-nav if it exists, otherwise at the beginning
                const existingTocNav = leftSidebar.querySelector('.toc-nav');
                if (existingTocNav) {
                    existingTocNav.insertAdjacentElement('afterend', tocSection);
                } else {
                    leftSidebar.insertBefore(tocSection, leftSidebar.firstChild);
                }
            }
        } else {
            // For legacy pages with history-sidebar, use the old approach
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
            // Fixed: use h3 because article categories use h3.category-title
            const heading = category.querySelector('h3');
            if (heading) {
                // Use container ID if it exists, otherwise generate one
                let id = category.id;
                if (!id) {
                    id = generateUniqueId(heading.textContent, usedIds);
                    category.id = id;
                } else if (usedIds.has(id)) {
                    // ID exists and is used - generate new unique one
                    id = generateUniqueId(id, usedIds);
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
                    id = generateUniqueId(h2.textContent || `section-${index + 1}`, usedIds);
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
                // Event listener removed here in favor of global delegation
                li.appendChild(a);
                tocList.appendChild(li);
            });
        } else {
            // Hide TOC if no sections found
            const tocSection = sidebar.querySelector('.sidebar-toc');
            if (tocSection) {
                tocSection.style.display = 'none';
            } else if (tocList) {
                // Fallback: hide the TOC list directly if tocSection wasn't found
                tocList.style.display = 'none';
            }
        }

        // Cache for TOC section positions
        let tocSectionCache = [];

        function updateTocCache() {
             tocSectionCache = sections.map(section => {
                 const element = section.element;
                 if (!element) return null;
                 const rect = element.getBoundingClientRect();
                 const scrollTop = window.scrollY;
                 return {
                     ...section,
                     top: rect.top + scrollTop,
                     bottom: rect.top + scrollTop + rect.height
                 };
             }).filter(s => s !== null);
        }

        // Initial update
        updateTocCache();
        // Register to resize manager
        resizeHandlers.push(updateTocCache);

        // Highlight active section on scroll
        function highlightActiveSection() {
            const scrollPosition = window.scrollY + TOC_SCROLL_OFFSET;
            const tocLinks = tocList.querySelectorAll('a');

            // Use cached positions
            tocSectionCache.forEach((section, index) => {
                if (index < tocLinks.length) {
                    tocLinks[index].classList.remove('active');

                    if (scrollPosition >= section.top && scrollPosition < section.bottom) {
                        tocLinks[index].classList.add('active');
                    }
                }
            });
        }

        // Update on scroll
        scrollHandlers.debounce.push(highlightActiveSection);

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
        header.addEventListener('click', function () {
            const isExpanded = this.getAttribute('aria-expanded') === 'true';

            // Toggle current accordion
            this.setAttribute('aria-expanded', !isExpanded);
        });
    });

    // Make repository dropdown links open in new tabs
    const repositoryLinks = document.querySelectorAll('.navbar-nav a[href^="https://github.com"]');
    repositoryLinks.forEach(link => {
        link.setAttribute('target', '_blank');
        // rel attribute will be handled by the generic security block below
    });

    // Secure all external links
    // Adds rel="noopener noreferrer" to prevent reverse tabnabbing and improve privacy
    // Applied to all external links regardless of target, as a defense-in-depth measure
    const allLinks = document.querySelectorAll('a[href^="http"]');
    const currentHostname = window.location.hostname;

    allLinks.forEach(link => {
        try {
            const url = new URL(link.href);
            if (url.hostname !== currentHostname && url.hostname !== '') {
                // Add target="_blank" if missing
                if (!link.hasAttribute('target')) {
                    link.setAttribute('target', '_blank');
                }

                // Add security attributes
                const rel = link.getAttribute('rel') || '';
                const parts = rel.split(' ').filter(p => p);
                if (!parts.includes('noopener')) parts.push('noopener');
                if (!parts.includes('noreferrer')) parts.push('noreferrer');
                link.setAttribute('rel', parts.join(' '));
            }
        } catch (e) {
            // Ignore invalid URLs
        }
    });

    // Log page load for analytics (optional)
    console.log('AffineDrift loaded successfully');
    console.log('Mathematical notation rendering via MathJax');

    // Back to Top Button
    const backToTopBtn = document.createElement('button');
    backToTopBtn.className = 'back-to-top';
    backToTopBtn.setAttribute('aria-label', 'Scroll to top');
    backToTopBtn.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <path d="M12 4l-8 8h6v8h4v-8h6z"/>
        </svg>
    `;
    document.body.appendChild(backToTopBtn);

    backToTopBtn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    function toggleBackToTop() {
        if (window.scrollY > 300) {
            backToTopBtn.classList.add('visible');
        } else {
            backToTopBtn.classList.remove('visible');
        }
    }

    // Register to shared scroll manager
    scrollHandlers.raf.push(toggleBackToTop);

    // Initial check
    toggleBackToTop();

    // Initialize Article History Tracking and Display
    initArticleHistory();
});

// Article History Logic
function initArticleHistory() {
    // List of article pages for history tracking
    const ARTICLE_PAGES = [
        'theory-part1.html',
        'theory-part2.html',
        'theory-part3.html',
        'theory-part4.html',
        'theory-part5.html',
        'inverse-dynamics.html',
        'wrist-universal-joint.html',
        'nonlinear-control-insights.html',
        'drift-components-wrench-double-pendulum.html',
        'secondary-axis-stability.html',
        'controllability-drift-ratio.html',
        'strokes-gained-limitations.html',
        'superposition.html',
        'screw-theory-reference.html',
        'null-space-constraint-jacobian.html',
        'lagrangian-reference.html',
        'inverse-dynamics-inference.html',
        'force-mobility-matrices.html',
        'mobility-force-ellipses.html',
        'affine-nature-golf-swing.html',
        'appendix-applications.html'
    ];

    const STORAGE_KEY = 'affinedrift_articles_history';
    const currentPath = window.location.pathname;
    const currentUrl = currentPath.split('/').pop() || '';
    const isArticlePage = currentPath.includes('/articles/') && currentUrl.endsWith('.html');

    // 1. Track Visit (runs on article pages)
    if (isArticlePage && ARTICLE_PAGES.includes(currentUrl)) {
        let history = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
        const currentPage = {
            title: document.title.replace(' - AffineDrift', '').replace('AffineDrift - ', ''),
            url: 'articles/' + currentUrl
        };

        // Remove if existing, add to top
        history = history.filter(item => item.url !== currentPage.url);
        history.unshift(currentPage);
        history = history.slice(0, 10); // Keep last 10
        localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
    }

    // 2. Display History (runs on articles.html where the list exists)
    const articlesHistoryList = document.getElementById('articles-history-list');
    if (articlesHistoryList) {
        const history = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');

        if (!history || history.length === 0) {
            articlesHistoryList.textContent = '';
            const li = document.createElement('li');
            li.className = 'history-empty';
            li.textContent = 'No recent articles yet';
            articlesHistoryList.appendChild(li);
        } else {
            articlesHistoryList.textContent = '';
            history.forEach(item => {
                const li = document.createElement('li');
                const a = document.createElement('a');
                a.href = item.url;
                a.textContent = item.title;
                li.appendChild(a);
                articlesHistoryList.appendChild(li);
            });
        }
    }
}

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

// Initialize on load
// Removed duplicate DOMContentLoaded listener for initArticleHistory
// It is now called inside the main listener



// Copy to Clipboard functionality
document.addEventListener('DOMContentLoaded', function() {
    // Select all pre elements
    const codeBlocks = document.querySelectorAll('pre');

    codeBlocks.forEach(pre => {
        // Skip if already processed or inside a wrapper
        if (pre.parentNode.classList.contains('code-wrapper')) return;

        // Check if pre is empty
        if (!pre.textContent.trim()) return;

        // Create wrapper
        const wrapper = document.createElement('div');
        wrapper.className = 'code-wrapper';

        // Insert wrapper before pre
        pre.parentNode.insertBefore(wrapper, pre);

        // Move pre into wrapper
        wrapper.appendChild(pre);

        // Create button
        const button = document.createElement('button');
        button.className = 'copy-btn';
        button.textContent = 'Copy';
        button.setAttribute('aria-label', 'Copy code to clipboard');
        button.type = 'button'; // Prevent form submission if inside a form

        // Add click event
        button.addEventListener('click', async () => {
            try {
                // Get text content
                const code = pre.innerText || pre.textContent;

                await navigator.clipboard.writeText(code);

                // Success feedback
                button.textContent = 'Copied!';
                button.classList.add('copied');

                setTimeout(() => {
                    button.textContent = 'Copy';
                    button.classList.remove('copied');
                }, 2000);
            } catch (err) {
                console.error('Failed to copy:', err);
                button.textContent = 'Error';
                setTimeout(() => button.textContent = 'Copy', 2000);
            }
        });

        wrapper.appendChild(button);
    });
});

// Accessibility: Skip to Content Link
// Injected dynamically to ensure it exists on all pages (especially generated ones)
document.addEventListener('DOMContentLoaded', function() {
    // Only add if it doesn't already exist
    if (document.querySelector('.skip-to-content')) return;

    const skipLink = document.createElement('a');
    skipLink.href = '#quarto-document-content';
    skipLink.className = 'skip-to-content';
    skipLink.textContent = 'Skip to main content';
    skipLink.setAttribute('aria-label', 'Skip to main content');

    // Insert as the very first element in the body
    if (document.body.firstChild) {
        document.body.insertBefore(skipLink, document.body.firstChild);
    } else {
        document.body.appendChild(skipLink);
    }
});
