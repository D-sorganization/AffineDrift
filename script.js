/**
 * AffineDrift - Interactive JavaScript
 * Handles smooth scrolling, navigation highlights, and interactive elements
 * ⚡ Optimized by Bolt: Implements Shared Scroll Manager & Geometry Caching
 */

// Constants for scroll offsets
// Note: Uses --scroll-offset not --header-offset because:
// - --header-offset is for sidebar positioning (top: 120px)
// - --scroll-offset is for scroll behavior (scroll-margin-top: 140px)
// JS smooth scrolling must match CSS scroll-margin-top for consistency
const getScrollOffset = () => {
    if (typeof window !== 'undefined') {
        const value = getComputedStyle(document.documentElement).getPropertyValue('--scroll-offset');
        return value ? parseInt(value) : 140;
    }
    return 140;
};
const HEADER_OFFSET = getScrollOffset(); // Smooth scrolling offset
const TOC_SCROLL_OFFSET = HEADER_OFFSET; // Active section detection offset
const MAX_ID_GENERATION_ATTEMPTS = 100;

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

/**
 * ⚡ SectionGeometryCache
 * Caches element positions to prevent layout thrashing (reflows) during scroll events.
 * Only recalculates on resize or explicit update.
 */
class SectionGeometryCache {
    constructor() {
        this.sections = [];
        this.navLinks = [];
        this.tocLinks = [];
    }

    scan() {
        this.sections = [];
        this.navLinks = [];
        this.tocLinks = [];

        // 1. Navbar Links
        const navLinks = document.querySelectorAll('.navbar-nav a.nav-link[href^="#"]');
        this.navLinks = Array.from(navLinks).map(link => ({
            element: link,
            targetId: link.getAttribute('href').substring(1)
        }));

        // 2. TOC Links
        const tocList = document.getElementById('toc-list');
        if (tocList) {
            this.tocLinks = Array.from(tocList.querySelectorAll('a')).map(link => ({
                element: link,
                targetId: link.getAttribute('href').substring(1)
            }));
        }

        // 3. Identify all target sections
        const targetIds = new Set([
            ...this.navLinks.map(l => l.targetId),
            ...this.tocLinks.map(l => l.targetId)
        ]);

        targetIds.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                this.sections.push({
                    id: id,
                    element: element,
                    top: 0,
                    bottom: 0
                });
            }
        });
    }

    update() {
        const scrollY = window.scrollY;
        this.sections.forEach(section => {
            const rect = section.element.getBoundingClientRect();
            section.top = rect.top + scrollY;
            section.bottom = rect.bottom + scrollY;
        });
    }
}

/**
 * ⚡ ScrollManager
 * Centralizes scroll handling using requestAnimationFrame to optimize performance.
 */
class ScrollManager {
    constructor() {
        this.cache = new SectionGeometryCache();
        this.ticking = false;
        this.backToTopBtn = null;
        this.resizeTimeout = null;
    }

    init() {
        this.backToTopBtn = document.querySelector('.back-to-top');

        // Initial scan and measure
        this.cache.scan();
        this.cache.update();

        // Bind events
        window.addEventListener('scroll', () => this.onScroll(), { passive: true });
        window.addEventListener('resize', () => this.onResize(), { passive: true });

        // Initial visual update
        this.updateVisuals();
    }

    onScroll() {
        if (!this.ticking) {
            window.requestAnimationFrame(() => {
                this.updateVisuals();
                this.ticking = false;
            });
            this.ticking = true;
        }
    }

    onResize() {
        if (this.resizeTimeout) clearTimeout(this.resizeTimeout);
        this.resizeTimeout = setTimeout(() => {
            this.cache.update();
            this.updateVisuals();
        }, 100);
    }

    updateVisuals() {
        const scrollY = window.scrollY;

        // 1. Back to Top Button
        if (this.backToTopBtn) {
            if (scrollY > 300) {
                this.backToTopBtn.classList.add('visible');
            } else {
                this.backToTopBtn.classList.remove('visible');
            }
        }

        // 2. Active Section Highlighting
        // Use roughly same offset as original (HEADER_OFFSET approx 140-150)
        const checkPoint = scrollY + HEADER_OFFSET + 10;

        let activeId = null;
        for (const section of this.cache.sections) {
            if (checkPoint >= section.top && checkPoint < section.bottom) {
                activeId = section.id;
            }
        }

        // Update Nav Links
        this.cache.navLinks.forEach(link => {
            const isActive = link.targetId === activeId;
            // Only toggle if necessary to minimize DOM operations
            if (isActive !== link.element.classList.contains('active')) {
                link.element.classList.toggle('active', isActive);
            }
        });

        // Update TOC Links
        this.cache.tocLinks.forEach(link => {
            const isActive = link.targetId === activeId;
            if (isActive !== link.element.classList.contains('active')) {
                link.element.classList.toggle('active', isActive);
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', function () {

    // --- 1. Interactive Elements Setup ---

    // Smooth scroll for anchor links
    document.addEventListener('click', function (e) {
        const link = e.target.closest('a[href^="#"]');
        if (link) {
            const href = link.getAttribute('href');
            if (href && href !== '#' && href.length > 1) {
                if (link.hasAttribute('data-bs-toggle') || link.hasAttribute('data-toggle')) return;

                const targetId = href.substring(1);
                const targetElement = document.getElementById(targetId);

                if (targetElement) {
                    e.preventDefault();
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

    // Navbar collapse logic
    const navbarCollapse = document.getElementById('navbarCollapse');
    const navLinks = document.querySelectorAll('.navbar-nav a.nav-link[href^="#"]');
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

    // Fade-in animation (IntersectionObserver)
    const NAV_BREAKPOINT = 768;
    const isMobile = window.innerWidth <= NAV_BREAKPOINT;
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (!isMobile && !prefersReducedMotion) {
        const observerOptions = { threshold: 0.1, rootMargin: '0px 0px 0px 0px' };
        const observer = new IntersectionObserver(function (entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const computedOpacity = window.getComputedStyle(entry.target).opacity;
                    if (computedOpacity === '0') {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }
                }
            });
        }, observerOptions);

        const sectionsToAnimate = document.querySelectorAll('section:not(.page-header):not(.article-section)');
        sectionsToAnimate.forEach(section => {
            const rect = section.getBoundingClientRect();
            if (rect.top > window.innerHeight) {
                section.style.opacity = '0';
                section.style.transform = 'translateY(20px)';
                section.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
                observer.observe(section);
            } else {
                section.style.opacity = '1';
                section.style.transform = 'translateY(0)';
            }
        });
    } else {
        const allSections = document.querySelectorAll('section');
        allSections.forEach(section => {
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
            section.style.visibility = 'visible';
        });
    }

    // --- 2. History & TOC Generation ---

    // History Sidebar
    function updateHistorySidebar() {
        const historyList = document.getElementById('history-list');
        if (!historyList) return;

        const MAX_HISTORY_TITLE_LENGTH = 40;
        const MAX_HISTORY_ITEMS = 10;
        let history = JSON.parse(localStorage.getItem('affinedrift_history') || '[]');

        let pageTitle = document.title;
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
        localStorage.setItem('affinedrift_history', JSON.stringify(history));

        const excludedPages = [
            'index.html', 'home.html', 'articles.html', 'article.html',
            'resources.html', 'tools.html', 'programs.html', 'contact.html',
            'about.html', 'research-reviews.html', 'book-reviews.html',
            'daydreams-doodles.html', 'daydreams.html', 'doodles.html'
        ];

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
    updateHistorySidebar();

    // Table of Contents
    function generateTableOfContents() {
        const leftSidebar = document.querySelector('.left-sidebar');
        const sidebar = leftSidebar || document.getElementById('history-sidebar');
        if (!sidebar) return;

        let tocSection;
        if (leftSidebar) {
            tocSection = leftSidebar.querySelector('.sidebar-toc');
            if (!tocSection) {
                tocSection = document.createElement('div');
                tocSection.className = 'sidebar-toc';
                tocSection.innerHTML = '<h3 class="sidebar-heading">On This Page</h3><ul class="sidebar-links" id="toc-list"></ul>';
                const existingTocNav = leftSidebar.querySelector('.toc-nav');
                if (existingTocNav) {
                    existingTocNav.insertAdjacentElement('afterend', tocSection);
                } else {
                    leftSidebar.insertBefore(tocSection, leftSidebar.firstChild);
                }
            }
        } else {
            const sidebarNav = sidebar.querySelector('.sidebar-nav');
            if (!sidebarNav) return;
            tocSection = sidebar.querySelector('.sidebar-toc');
            if (!tocSection) {
                tocSection = document.createElement('div');
                tocSection.className = 'sidebar-section sidebar-toc';
                tocSection.innerHTML = '<h3 class="sidebar-heading">On This Page</h3><ul class="sidebar-links" id="toc-list"></ul>';
                sidebarNav.insertBefore(tocSection, sidebarNav.firstChild);
            }
        }

        const tocList = document.getElementById('toc-list');
        if (!tocList) return;
        tocList.innerHTML = '';

        const sections = [];
        const usedIds = new Set();

        const pageSections = document.querySelectorAll('.page-section[id], section[id]');
        pageSections.forEach(section => {
            const heading = section.querySelector('.section-heading, h2, h1');
            if (heading && section.id) {
                sections.push({
                    id: section.id,
                    text: heading.textContent.trim(),
                    level: 2
                });
                usedIds.add(section.id);
            }
        });

        const categories = document.querySelectorAll('.article-category');
        categories.forEach(category => {
            const heading = category.querySelector('h3');
            if (heading) {
                let id = category.id;
                if (!id) {
                    id = generateUniqueId(heading.textContent, usedIds);
                    category.id = id;
                } else if (usedIds.has(id)) {
                    id = generateUniqueId(id, usedIds);
                    category.id = id;
                }
                usedIds.add(id);
                sections.push({
                    id: id,
                    text: heading.textContent.trim(),
                    level: 2
                });
            }
        });

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
                    level: 2
                });
            });
        }

        if (sections.length > 0) {
            sections.forEach(section => {
                const li = document.createElement('li');
                const a = document.createElement('a');
                a.href = `#${section.id}`;
                a.textContent = section.text;
                a.className = `toc-level-${section.level}`;
                li.appendChild(a);
                tocList.appendChild(li);
            });
        } else {
             if (tocSection) tocSection.style.display = 'none';
             else if (tocList) tocList.style.display = 'none';
        }
    }
    generateTableOfContents();

    // Lazy load images
    if ('loading' in HTMLImageElement.prototype) {
        document.querySelectorAll('img[src]').forEach(img => {
            if (!img.hasAttribute('loading')) {
                img.setAttribute('loading', 'lazy');
            }
        });
    }

    // Accordion functionality
    const accordionHeaders = document.querySelectorAll('.accordion-header');
    accordionHeaders.forEach((header, index) => {
        const content = header.nextElementSibling;
        if (content && content.classList.contains('accordion-content')) {
            if (!content.id) {
                content.id = `accordion-content-${index}`;
            }
            header.setAttribute('aria-controls', content.id);
            const isExpanded = header.getAttribute('aria-expanded') === 'true';
            content.setAttribute('aria-hidden', !isExpanded);
        }
        header.addEventListener('click', function () {
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            this.setAttribute('aria-expanded', !isExpanded);
            if (content && content.classList.contains('accordion-content')) {
                content.setAttribute('aria-hidden', isExpanded);
            }
        });
    });

    // Repository links
    document.querySelectorAll('.navbar-nav a[href^="https://github.com"]').forEach(link => {
        link.setAttribute('target', '_blank');
        // rel handled by secure external links below
    });

    // Secure external links
    const currentHostname = window.location.hostname;
    document.querySelectorAll('a[href^="http"]').forEach(link => {
        try {
            const url = new URL(link.href);
            if (url.hostname !== currentHostname && url.hostname !== '') {
                if (!link.hasAttribute('target')) {
                    link.setAttribute('target', '_blank');
                }
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

    // Article History
    function initArticleHistory() {
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

        if (isArticlePage && ARTICLE_PAGES.includes(currentUrl)) {
            let history = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
            const currentPage = {
                title: document.title.replace(' - AffineDrift', '').replace('AffineDrift - ', ''),
                url: 'articles/' + currentUrl
            };
            history = history.filter(item => item.url !== currentPage.url);
            history.unshift(currentPage);
            history = history.slice(0, 10);
            localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
        }

        const articlesHistoryList = document.getElementById('articles-history-list');
        if (articlesHistoryList) {
            const history = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
            articlesHistoryList.textContent = '';
            if (!history || history.length === 0) {
                const li = document.createElement('li');
                li.className = 'history-empty';
                li.textContent = 'No recent articles yet';
                articlesHistoryList.appendChild(li);
            } else {
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
    initArticleHistory();

    // Copy to Clipboard
    const codeBlocks = document.querySelectorAll('pre');
    codeBlocks.forEach(pre => {
        if (pre.parentNode.classList.contains('code-wrapper')) return;
        if (!pre.textContent.trim()) return;

        const wrapper = document.createElement('div');
        wrapper.className = 'code-wrapper';
        pre.parentNode.insertBefore(wrapper, pre);
        wrapper.appendChild(pre);

        const button = document.createElement('button');
        button.className = 'copy-btn';
        button.textContent = 'Copy';
        button.setAttribute('aria-label', 'Copy code to clipboard');
        button.type = 'button';

        button.addEventListener('click', async () => {
            try {
                await navigator.clipboard.writeText(pre.innerText || pre.textContent);
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

    // Skip to Content Link
    if (!document.querySelector('.skip-to-content')) {
        const skipLink = document.createElement('a');
        skipLink.href = '#quarto-document-content';
        skipLink.className = 'skip-to-content';
        skipLink.textContent = 'Skip to main content';
        skipLink.setAttribute('aria-label', 'Skip to main content');

        if (document.body.firstChild) {
            document.body.insertBefore(skipLink, document.body.firstChild);
        } else {
            document.body.appendChild(skipLink);
        }
    }

    console.log('AffineDrift loaded successfully (Optimized)');

    // --- 3. Initialize Scroll Manager (⚡ Optimization) ---
    // Must run after TOC generation and element creation
    const scrollManager = new ScrollManager();
    scrollManager.init();
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
