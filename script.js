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
const MAX_ID_GENERATION_ATTEMPTS = 100;

// Delay before printing to ensure MathJax has fully rendered equations
const MATHJAX_RENDER_DELAY_MS = 100;

// Additional height buffer for Critics Corner content expansion
// Accounts for padding and dynamic content sizing
const CRITICS_CORNER_PADDING_OFFSET = 50;

// ⚡ Bolt Optimization: Lazy initialize to avoid synchronous layout thrashing at top level
let HEADER_OFFSET = 140;
let TOC_SCROLL_OFFSET = 140; // Active section detection offset

const getScrollOffset = () => {
  if (typeof window !== "undefined") {
    const value = getComputedStyle(document.documentElement).getPropertyValue(
      "--scroll-offset",
    );
    return value ? parseInt(value) : 140;
  }
  return 140;
};

const runOnDomReady = (callback) => {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", callback);
  } else {
    callback();
  }
};

// Helper function to debounce events
function debounce(func, wait) {
  let timeout;
  return function (...args) {
    const context = this;
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(context, args), wait);
  };
}

// ⚡ Bolt Optimization: Helper to run non-critical tasks when idle
function runWhenIdle(callback) {
  if (typeof requestIdleCallback !== "undefined") {
    requestIdleCallback(callback);
  } else {
    setTimeout(callback, 0);
  }
}

// Helper function to generate unique IDs
function generateUniqueId(text, usedIds) {
  let baseId = text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
  if (!baseId) baseId = "section"; // Fallback for empty text

  let id = baseId;
  let counter = 1;

  // ⚡ Bolt Optimization: Check both local set and DOM to avoid global scan
  const exists = (candidateId) => {
    return (
      usedIds.has(candidateId) || document.getElementById(candidateId) !== null
    );
  };

  // First try base ID
  if (!exists(id)) {
    return id;
  }

  // Try incrementing counter
  while (exists(id) && counter < MAX_ID_GENERATION_ATTEMPTS) {
    id = `${baseId}-${counter}`;
    counter++;
  }

  // Fallback if still colliding
  if (usedIds.has(id)) {
    id = `${baseId}-${Date.now()}`;
  }

  return id;
}

runOnDomReady(function () {
  // Update offset from CSS variable once DOM is ready
  HEADER_OFFSET = getScrollOffset();
  TOC_SCROLL_OFFSET = HEADER_OFFSET;

  // --- 1. Interactive Elements Setup ---

  // Smooth scroll for anchor links
  document.addEventListener("click", function (e) {
    const link = e.target.closest('a[href^="#"]');
    if (link) {
      const href = link.getAttribute("href");
      if (href && href !== "#" && href.length > 1) {
        if (
          link.hasAttribute("data-bs-toggle") ||
          link.hasAttribute("data-toggle")
        )
          return;

        const targetId = href.substring(1);
        const targetElement = document.getElementById(targetId);

        if (targetElement) {
          e.preventDefault();
          const elementPosition = targetElement.getBoundingClientRect().top;
          const offsetPosition =
            elementPosition + window.scrollY - HEADER_OFFSET;

          // 🎨 Palette UX: Update URL for sharing
          history.pushState(null, null, href);

          // 🎨 Palette UX: Smooth scroll
          window.scrollTo({
            top: offsetPosition,
            behavior: "smooth",
          });

          // 🎨 Palette UX: Accessible Focus Management
          if (!targetElement.hasAttribute("tabindex")) {
            targetElement.setAttribute("tabindex", "-1");
          }
          targetElement.focus({ preventScroll: true });

          // 🎨 Palette UX: Visual confirmation flash
          targetElement.classList.remove("target-highlight");
          void targetElement.offsetWidth; // Trigger reflow
          targetElement.classList.add("target-highlight");
        }
      }
    }
  });

  // Navbar collapse logic
  const navbarCollapse = document.getElementById("navbarCollapse");
  const navLinks = document.querySelectorAll(
    '.navbar-nav a.nav-link[href^="#"]',
  );
  navLinks.forEach((link) => {
    link.addEventListener("click", () => {
      if (navbarCollapse && navbarCollapse.classList.contains("show")) {
        const collapseInstance =
          window.bootstrap?.Collapse?.getInstance
            ? window.bootstrap.Collapse.getInstance(navbarCollapse)
            : null;
        if (collapseInstance) {
          collapseInstance.hide();
        } else {
          navbarCollapse.classList.remove("show");
        }
      }
    });
  });

  // Fade-in animation (IntersectionObserver)
  const NAV_BREAKPOINT = 768;
  const isMobile = window.innerWidth <= NAV_BREAKPOINT;
  const prefersReducedMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)",
  ).matches;

  if (!isMobile && !prefersReducedMotion) {
    const observerOptions = { threshold: 0.1, rootMargin: "0px 0px 0px 0px" };
    const observer = new IntersectionObserver(function (entries) {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.style.opacity = "1";
          entry.target.style.transform = "translateY(0)";
          observer.unobserve(entry.target); // ⚡ Bolt Optimization: Stop observing once visible
        }
      });
    }, observerOptions);

    const sectionsToAnimate = document.querySelectorAll(
      "section:not(.page-header):not(.article-section)",
    );
    const animationStates = [];

    // ⚡ Bolt Optimization: Batch DOM reads to prevent layout thrashing
    // Phase 1: Read (getBoundingClientRect)
    sectionsToAnimate.forEach((section) => {
      const rect = section.getBoundingClientRect();
      animationStates.push({
        section,
        shouldAnimate: rect.top > window.innerHeight,
      });
    });

    // Phase 2: Write (style updates)
    animationStates.forEach(({ section, shouldAnimate }) => {
      if (shouldAnimate) {
        section.style.opacity = "0";
        section.style.transform = "translateY(20px)";
        section.style.transition = "opacity 0.4s ease, transform 0.4s ease";
        observer.observe(section);
      } else {
        section.style.opacity = "1";
        section.style.transform = "translateY(0)";
      }
    });
  } else {
    const allSections = document.querySelectorAll("section");
    allSections.forEach((section) => {
      section.style.opacity = "1";
      section.style.transform = "translateY(0)";
      section.style.visibility = "visible";
    });
  }

  // --- 1b. Lazy Loading Images ---
  // Add 'loaded' class to lazy images once they load for CSS animation removal
  const lazyImages = document.querySelectorAll('img[loading="lazy"]');
  lazyImages.forEach((img) => {
    if (img.complete) {
      img.classList.add("loaded");
    } else {
      img.addEventListener("load", function () {
        this.classList.add("loaded");
      });
      img.addEventListener("error", function () {
        this.classList.add("loaded"); // Remove shimmer even on error
      });
    }
  });

  // --- 2. History & TOC Generation ---

  // History Sidebar
  function updateHistorySidebar() {
    const historyList = document.getElementById("history-list");
    if (!historyList) return;

    const MAX_HISTORY_TITLE_LENGTH = 40;
    const MAX_HISTORY_ITEMS = 10;
    let history = JSON.parse(
      localStorage.getItem("affinedrift_history") || "[]",
    );

    let pageTitle = document.title;
    if (pageTitle.includes(" - AffineDrift")) {
      pageTitle = pageTitle.replace(" - AffineDrift", "");
    } else if (pageTitle.startsWith("AffineDrift - ")) {
      pageTitle = pageTitle.replace("AffineDrift - ", "");
    } else if (pageTitle === "AffineDrift") {
      pageTitle = "Home";
    }

    const currentPage = {
      title: pageTitle,
      url: window.location.pathname.split("/").pop() || "index.html",
      fullUrl: window.location.href,
    };

    // Remove current page if it's already in history
    history = history.filter((item) => item.url !== currentPage.url);
    // Add current page to front
    history.unshift(currentPage);
    // Keep only last N items
    history = history.slice(0, MAX_HISTORY_ITEMS);
    localStorage.setItem("affinedrift_history", JSON.stringify(history));

    const excludedPages = [
      "index.html",
      "home.html",
      "articles.html",
      "article.html",
      "resources.html",
      "tools.html",
      "programs.html",
      "contact.html",
      "about.html",
      "research-reviews.html",
      "book-reviews.html",
      "daydreams-doodles.html",
      "daydreams.html",
      "doodles.html",
    ];

    const displayHistory = history.filter(
      (item) =>
        item.url !== currentPage.url &&
        !excludedPages.includes(item.url.toLowerCase()) &&
        !item.url.match(
          /^(tools|contact|about|resources|articles|research-reviews|book-reviews|daydreams)/i,
        ),
    );

    // ⚡ Bolt Optimization: Use DocumentFragment to minimize reflows
    historyList.textContent = "";
    if (displayHistory.length === 0) {
      const li = document.createElement("li");
      li.className = "history-empty";
      li.textContent = "No recent articles yet";
      historyList.appendChild(li);
    } else {
      const fragment = document.createDocumentFragment();
      displayHistory.forEach((item) => {
        const li = document.createElement("li");
        const a = document.createElement("a");
        a.href = item.url;
        const displayTitle =
          item.title.length > MAX_HISTORY_TITLE_LENGTH
            ? item.title.substring(0, MAX_HISTORY_TITLE_LENGTH) + "..."
            : item.title;
        a.textContent = displayTitle;
        li.appendChild(a);
        fragment.appendChild(li);
      });
      historyList.appendChild(fragment);
    }
  }
  // ⚡ Bolt Optimization: Defer history updates to unblock main thread
  runWhenIdle(updateHistorySidebar);

  // Table of Contents
  function generateTableOfContents() {
    const leftSidebar = document.querySelector(".left-sidebar");
    const sidebar = leftSidebar || document.getElementById("history-sidebar");
    if (!sidebar) return;

    let tocSection;
    if (leftSidebar) {
      tocSection = leftSidebar.querySelector(".sidebar-toc");
      if (!tocSection) {
        tocSection = document.createElement("div");
        tocSection.className = "sidebar-toc";
        tocSection.innerHTML =
          '<h3 class="sidebar-heading">On This Page</h3><ul class="sidebar-links" id="toc-list"></ul>';
        const existingTocNav = leftSidebar.querySelector(".toc-nav");
        if (existingTocNav) {
          existingTocNav.insertAdjacentElement("afterend", tocSection);
        } else {
          leftSidebar.insertBefore(tocSection, leftSidebar.firstChild);
        }
      }
    } else {
      const sidebarNav = sidebar.querySelector(".sidebar-nav");
      if (!sidebarNav) return;
      tocSection = sidebar.querySelector(".sidebar-toc");
      if (!tocSection) {
        tocSection = document.createElement("div");
        tocSection.className = "sidebar-section sidebar-toc";
        tocSection.innerHTML =
          '<h3 class="sidebar-heading">On This Page</h3><ul class="sidebar-links" id="toc-list"></ul>';
        sidebarNav.insertBefore(tocSection, sidebarNav.firstChild);
      }
    }

    const tocList = document.getElementById("toc-list");
    if (!tocList) return;
    tocList.innerHTML = "";

    const sections = [];
    const usedIds = new Set();

    const pageSections = document.querySelectorAll(
      ".page-section[id], section[id]",
    );
    pageSections.forEach((section) => {
      const heading = section.querySelector(".section-heading, h2, h1");
      if (heading && section.id) {
        sections.push({
          id: section.id,
          text: heading.textContent.trim(),
          level: 2,
        });
        usedIds.add(section.id);
      }
    });

    const categories = document.querySelectorAll(".article-category");
    categories.forEach((category) => {
      const heading = category.querySelector("h3");
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
          level: 2,
        });
      }
    });

    if (sections.length === 0) {
      const h2s = document.querySelectorAll("h2");
      h2s.forEach((h2, index) => {
        let id = h2.id;
        if (!id || usedIds.has(id)) {
          id = generateUniqueId(
            h2.textContent || `section-${index + 1}`,
            usedIds,
          );
          h2.id = id;
        }
        usedIds.add(id);
        sections.push({
          id: id,
          text: h2.textContent.trim(),
          level: 2,
        });
      });
    }

    // ⚡ Bolt Optimization: Use DocumentFragment for TOC generation
    if (sections.length > 0) {
      const fragment = document.createDocumentFragment();
      sections.forEach((section) => {
        const li = document.createElement("li");
        const a = document.createElement("a");
        a.href = `#${section.id}`;
        a.textContent = section.text;
        a.className = `toc-level-${section.level}`;
        li.appendChild(a);
        fragment.appendChild(li);
      });
      tocList.appendChild(fragment);
    } else {
      if (tocSection) tocSection.style.display = "none";
      else if (tocList) tocList.style.display = "none";
    }
  }
  generateTableOfContents();

  // 🎨 Palette UX: Add Permalink Anchors
  function initAnchorLinks() {
    const headings = document.querySelectorAll(
      ".main-content-area h2, .main-content-area h3",
    );

    // ⚡ Bolt Optimization: Use empty set and check DOM on demand
    // Removing the full DOM scan (querySelectorAll("[id]")) improves performance
    // from O(N_dom_nodes) to O(N_headings)
    const usedIds = new Set();

    // ⚡ Bolt Optimization: Pre-create SVG to clone instead of parsing HTML string for every heading
    const anchorIcon = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "svg",
    );
    anchorIcon.setAttribute("aria-hidden", "true");
    anchorIcon.setAttribute("width", "18");
    anchorIcon.setAttribute("height", "18");
    anchorIcon.setAttribute("viewBox", "0 0 24 24");
    anchorIcon.setAttribute("fill", "none");
    anchorIcon.setAttribute("stroke", "currentColor");
    anchorIcon.setAttribute("stroke-width", "2");
    anchorIcon.setAttribute("stroke-linecap", "round");
    anchorIcon.setAttribute("stroke-linejoin", "round");
    anchorIcon.innerHTML =
      '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>';

    headings.forEach((heading) => {
      // Skip if already has anchor
      if (heading.querySelector(".anchor-link")) return;

      // Ensure ID exists
      if (!heading.id) {
        heading.id = generateUniqueId(heading.textContent, usedIds);
        usedIds.add(heading.id);
      }

      const anchor = document.createElement("a");
      anchor.className = "anchor-link";
      anchor.href = `#${heading.id}`;
      anchor.setAttribute("aria-label", "Link to this section");
      // Simple Link Icon
      anchor.appendChild(anchorIcon.cloneNode(true));

      heading.appendChild(anchor);
    });
  }
  initAnchorLinks();

  // ScrollSpy for Table of Contents
  function initScrollSpy() {
    const tocLinks = document.querySelectorAll("#toc-list a");
    if (tocLinks.length === 0) return;

    // ⚡ Bolt Optimization: Pre-calculate map for O(1) lookup
    const linkMap = new Map();
    tocLinks.forEach((link) => {
      const href = link.getAttribute("href");
      if (href && href.startsWith("#")) {
        linkMap.set(href.substring(1), link);
      }
    });
    let currentActiveLink = null;

    const sections = document.querySelectorAll(
      ".page-section[id], section[id]",
    );

    // ⚡ Bolt Optimization: Map section IDs to their DOM index for O(1) sort
    const sectionIndexMap = new Map();
    sections.forEach((section, index) => {
      sectionIndexMap.set(section.id, index);
    });

    // ⚡ Bolt Optimization: Track visible sections by index rather than ID
    // This allows finding the "first" visible section using Math.min() (O(k))
    // instead of iterating through all sections (O(N))
    const visibleIndices = new Set();

    const observerOptions = {
      root: null,
      rootMargin: "-100px 0px -60% 0px",
      threshold: 0,
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        const index = sectionIndexMap.get(entry.target.id);
        if (index !== undefined) {
          if (entry.isIntersecting) {
            visibleIndices.add(index);
          } else {
            visibleIndices.delete(index);
          }
        }
      });

      // ⚡ Bolt Optimization: Find first visible section via index math
      let activeId = null;
      if (visibleIndices.size > 0) {
        const firstVisibleIndex = Math.min(...visibleIndices);
        if (firstVisibleIndex >= 0 && firstVisibleIndex < sections.length) {
          activeId = sections[firstVisibleIndex].id;
        }
      }

      if (activeId) {
        // ⚡ Bolt Optimization: Only update classes if active link changed
        const newActiveLink = linkMap.get(activeId);
        if (newActiveLink && newActiveLink !== currentActiveLink) {
          if (currentActiveLink) {
            currentActiveLink.classList.remove("active");
            currentActiveLink.removeAttribute("aria-current");
          }
          newActiveLink.classList.add("active");
          newActiveLink.setAttribute("aria-current", "location");
          currentActiveLink = newActiveLink;
        }
      }
    }, observerOptions);

    sections.forEach((section) => {
      if (linkMap.has(section.id)) {
        observer.observe(section);
      }
    });
  }
  initScrollSpy();

  // Lazy load images
  // ⚡ Bolt Optimization: Use document.images (O(1)) instead of querySelectorAll (O(N))
  if ("loading" in HTMLImageElement.prototype) {
    for (const img of document.images) {
      if (img.src && !img.hasAttribute("loading")) {
        img.setAttribute("loading", "lazy");
      }
    }
  }

  // Lazy load iframes
  if ("loading" in HTMLIFrameElement.prototype) {
    // ⚡ Bolt Optimization: Use getElementsByTagName (Live Collection)
    const iframes = document.getElementsByTagName("iframe");
    for (const iframe of iframes) {
      if (iframe.src && !iframe.hasAttribute("loading")) {
        iframe.setAttribute("loading", "lazy");
      }
    }
  }

  // Accordion functionality
  // ⚡ Bolt Optimization: Event Delegation for Accordions
  // Separate initialization from event handling to reduce memory usage (1 listener vs N)
  const accordionHeaders = document.querySelectorAll(".accordion-header");
  accordionHeaders.forEach((header, index) => {
    const content = header.nextElementSibling;
    if (content && content.classList.contains("accordion-content")) {
      if (!content.id) {
        content.id = `accordion-content-${index}`;
      }
      header.setAttribute("aria-controls", content.id);
      const isExpanded = header.getAttribute("aria-expanded") === "true";
      content.setAttribute("aria-hidden", !isExpanded);
    }
  });

  document.addEventListener("click", (e) => {
    const header = e.target.closest(".accordion-header");
    if (!header) return;

    const content = header.nextElementSibling;
    if (content && content.classList.contains("accordion-content")) {
      const isExpanded = header.getAttribute("aria-expanded") === "true";
      header.setAttribute("aria-expanded", !isExpanded);
      content.setAttribute("aria-hidden", isExpanded);
    }
  });

  // Repository links
  document
    .querySelectorAll('.navbar-nav a[href^="https://github.com"]')
    .forEach((link) => {
      link.setAttribute("target", "_blank");
      // rel handled by secure external links below
    });

  // Secure external links
  // ⚡ Bolt Optimization: Use document.links (O(1)) instead of querySelectorAll (O(N))
  const currentHostname = window.location.hostname;
  for (const link of document.links) {
    // ⚡ Bolt Optimization: Use link.hostname instead of new URL() to avoid object creation overhead
    if (
      link.hostname &&
      link.hostname !== currentHostname &&
      link.protocol.startsWith("http")
    ) {
      if (!link.hasAttribute("target")) {
        link.setAttribute("target", "_blank");
      }
      const rel = link.getAttribute("rel") || "";
      const parts = rel.split(" ").filter((p) => p);
      if (!parts.includes("noopener")) parts.push("noopener");
      if (!parts.includes("noreferrer")) parts.push("noreferrer");
      link.setAttribute("rel", parts.join(" "));
      if (
        !link.querySelector("img, svg") &&
        !link.classList.contains("external-link")
      ) {
        link.classList.add("external-link");
        // 🎨 Palette UX: Add accessible SVG icon for external links
        const icon = document.createElement("span");
        icon.className = "external-link-icon";
        icon.setAttribute("aria-hidden", "true");
        icon.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>`;
        link.appendChild(icon);
      }
    }
  }

  // Back to Top Button
  const backToTopBtn = document.createElement("button");
  backToTopBtn.className = "back-to-top";
  backToTopBtn.setAttribute("aria-label", "Scroll to top");

  // Progress ring circumference: 2 * PI * r = 2 * PI * 21 ≈ 131.95
  const radius = 21;
  const circumference = 2 * Math.PI * radius;

  backToTopBtn.innerHTML = `
        <svg class="progress-ring" width="48" height="48" viewBox="0 0 48 48">
            <circle
                class="progress-ring-circle"
                stroke="white"
                stroke-width="3"
                fill="transparent"
                r="${radius}"
                cx="24"
                cy="24"
                style="stroke-dasharray: ${circumference}; stroke-dashoffset: ${circumference};"
            />
        </svg>
        <svg class="back-to-top-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <path d="M12 4l-8 8h6v8h4v-8h6z"/>
        </svg>
    `;
  document.body.appendChild(backToTopBtn);

  const progressCircle = backToTopBtn.querySelector(".progress-ring-circle");

  backToTopBtn.addEventListener("click", () => {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
    // 🎨 Palette UX: Move focus to top for keyboard users
    document.body.setAttribute("tabindex", "-1");
    document.body.focus({ preventScroll: true });
    // Cleanup tabindex after blur to keep DOM clean
    document.body.addEventListener(
      "blur",
      () => {
        document.body.removeAttribute("tabindex");
      },
      { once: true },
    );
  });

  // ⚡ Bolt Optimization: Debounce scroll events with requestAnimationFrame & Cache Geometry
  let isScrollTicking = false;
  let isBackToTopVisible = false;
  let maxScroll = 0;
  const SCROLL_THRESHOLD = 300;

  // Cache document geometry to avoid layout thrashing in scroll loop
  const updateGeometry = () => {
    maxScroll = document.documentElement.scrollHeight - window.innerHeight;
  };

  // Initial calculation
  updateGeometry();

  // Update on resize (Debounced)
  window.addEventListener("resize", debounce(updateGeometry, 250));

  // Update on content changes (e.g., accordions)
  if (typeof ResizeObserver !== "undefined") {
    const resizeObserver = new ResizeObserver(
      debounce(() => {
        updateGeometry();
      }, 250),
    );
    resizeObserver.observe(document.body);
  }

  function updateScrollProgress() {
    const scrollTop = window.scrollY;

    // Visibility toggle with state tracking
    const shouldBeVisible = scrollTop > SCROLL_THRESHOLD;
    if (shouldBeVisible !== isBackToTopVisible) {
      isBackToTopVisible = shouldBeVisible;
      if (shouldBeVisible) {
        backToTopBtn.classList.add("visible");
      } else {
        backToTopBtn.classList.remove("visible");
      }
    }

    // Progress ring update using cached geometry
    if (maxScroll > 0) {
      const scrollPercent = Math.min(scrollTop / maxScroll, 1);
      const offset = circumference - scrollPercent * circumference;
      progressCircle.style.strokeDashoffset = offset;
    }

    isScrollTicking = false;
  }

  function onScroll() {
    if (!isScrollTicking) {
      window.requestAnimationFrame(updateScrollProgress);
      isScrollTicking = true;
    }
  }

  // Update on scroll (passive listener for better performance)
  window.addEventListener("scroll", onScroll, { passive: true });

  // Initial check
  updateScrollProgress();

  // Export to PDF Button
  const exportToPdfBtn = document.createElement("button");
  exportToPdfBtn.className = "export-to-pdf";
  exportToPdfBtn.setAttribute("aria-label", "Export page to PDF");
  exportToPdfBtn.innerHTML = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
      <polyline points="14 2 14 8 20 8"></polyline>
      <line x1="12" y1="18" x2="12" y2="12"></line>
      <line x1="9" y1="15" x2="15" y2="15"></line>
    </svg>
    <span class="tooltip">Export to PDF</span>
  `;
  document.body.appendChild(exportToPdfBtn);

  // Show/hide export button based on scroll (same as back-to-top)
  function updateExportButtonVisibility() {
    const scrollTop = window.scrollY;
    const shouldBeVisible = scrollTop > SCROLL_THRESHOLD;
    if (shouldBeVisible) {
      exportToPdfBtn.classList.add("visible");
    } else {
      exportToPdfBtn.classList.remove("visible");
    }
  }

  // Update visibility on scroll
  window.addEventListener(
    "scroll",
    debounce(updateExportButtonVisibility, 100),
    { passive: true },
  );

  // Initial visibility check
  updateExportButtonVisibility();

  // Export to PDF functionality
  exportToPdfBtn.addEventListener("click", () => {
    // Wait for MathJax to finish rendering if present
    const mathjaxDelay =
      typeof MathJax !== "undefined" ? MATHJAX_RENDER_DELAY_MS : 0;

    // Add print-specific class to body for CSS targeting
    document.body.classList.add("printing");

    setTimeout(() => {
      window.print();
      // Remove print class after print dialog closes
      window.addEventListener(
        "afterprint",
        () => {
          document.body.classList.remove("printing");
        },
        { once: true },
      );
      // Fallback for browsers that don't support afterprint
      setTimeout(() => {
        document.body.classList.remove("printing");
      }, 1000);
    }, mathjaxDelay);
  });

  // Initialize Article History Tracking and Display

  // Article History Logic
  function initArticleHistory() {
    // List of article pages for history tracking
    const ARTICLE_PAGES = [
      "theory-part1.html",
      "theory-part2.html",
      "theory-part3.html",
      "theory-part4.html",
      "theory-part5.html",
      "inverse-dynamics.html",
      "wrist-universal-joint.html",
      "nonlinear-control-insights.html",
      "drift-components-wrench-double-pendulum.html",
      "secondary-axis-stability.html",
      "controllability-drift-ratio.html",
      "strokes-gained-limitations.html",
      "superposition.html",
      "screw-theory-reference.html",
      "null-space-constraint-jacobian.html",
      "lagrangian-reference.html",
      "inverse-dynamics-inference.html",
      "force-mobility-matrices.html",
      "mobility-force-ellipses.html",
      "affine-nature-golf-swing.html",
      "appendix-applications.html",
    ];

    const STORAGE_KEY = "affinedrift_articles_history";
    const currentPath = window.location.pathname;
    const currentUrl = currentPath.split("/").pop() || "";
    const isArticlePage =
      currentPath.includes("/articles/") && currentUrl.endsWith(".html");

    // 1. Track Visit (runs on article pages)
    if (isArticlePage && ARTICLE_PAGES.includes(currentUrl)) {
      let history = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
      const currentPage = {
        title: document.title
          .replace(" - AffineDrift", "")
          .replace("AffineDrift - ", ""),
        url: "articles/" + currentUrl,
      };

      // Remove if existing, add to top
      history = history.filter((item) => item.url !== currentPage.url);
      history.unshift(currentPage);
      history = history.slice(0, 10); // Keep last 10
      localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
    }

    // 2. Display History (runs on articles.html where the list exists)
    const articlesHistoryList = document.getElementById(
      "articles-history-list",
    );
    if (articlesHistoryList) {
      const history = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
      articlesHistoryList.textContent = "";
      // ⚡ Bolt Optimization: Use DocumentFragment
      if (!history || history.length === 0) {
        const li = document.createElement("li");
        li.className = "history-empty";
        li.textContent = "No recent articles yet";
        articlesHistoryList.appendChild(li);
      } else {
        const fragment = document.createDocumentFragment();
        history.forEach((item) => {
          const li = document.createElement("li");
          const a = document.createElement("a");
          a.href = item.url;
          a.textContent = item.title;
          li.appendChild(a);
          fragment.appendChild(li);
        });
        articlesHistoryList.appendChild(fragment);
      }
    }
  }
  // ⚡ Bolt Optimization: Defer history updates to unblock main thread
  runWhenIdle(initArticleHistory);

  // 🎨 Palette UX: Copy Email Functionality
  function initEmailCopy() {
    // ⚡ Bolt Optimization: Use document.links to avoid extra DOM query; still iterates over all links
    const links = document.links;
    if (links.length === 0) return;

    // Pre-define SVGs strings to avoid repetitive DOM creation
    const copyIcon = '<svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>';
    const checkIcon = '<svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"></polyline></svg>';

    for (const link of links) {
      if (link.protocol !== "mailto:") continue;

      // Skip if already processed
      if (
        link.nextElementSibling &&
        link.nextElementSibling.classList.contains("copy-email-btn")
      )
        continue;

      const href = link.getAttribute("href");
      // Simple extraction of email (handling potential ?subject=...)
      const email = href.replace(/^mailto:/, "").split("?")[0];
      if (!email) continue;

      const button = document.createElement("button");
      button.className = "copy-email-btn";
      button.setAttribute("aria-label", "Copy email address");
      button.setAttribute("type", "button");
      button.innerHTML = copyIcon;
      button.title = "Copy email address";

      button.addEventListener("click", (e) => {
        e.preventDefault(); // Prevent opening mail client if they click the button specifically
        e.stopPropagation();

        navigator.clipboard.writeText(email)
          .then(() => {
            button.innerHTML = checkIcon;
            button.classList.add("success");
            button.setAttribute("aria-label", "Email copied");

            setTimeout(() => {
              button.innerHTML = copyIcon;
              button.classList.remove("success");
              button.setAttribute("aria-label", "Copy email address");
            }, 2000);
          })
          .catch((err) => {
            console.error("Failed to copy email:", err);
          });
      });

      link.insertAdjacentElement("afterend", button);
    }
  }
  runWhenIdle(initEmailCopy);

  // ⚡ Bolt Optimization: Defer non-critical interactive elements to runWhenIdle
  runWhenIdle(() => {
    // 🎨 Palette UX: Responsive Tables
    const tables = document.querySelectorAll("#quarto-document-content table");
    // Use a shared set for unique IDs across all tables
    const tableUsedIds = new Set();
    tables.forEach((table) => {
      // Check for existing wrapper (both class and overflow style)
      const parent = table.parentElement;
      if (
        parent.classList.contains("table-wrapper") ||
        parent.style.overflowX === "auto" ||
        window.getComputedStyle(parent).overflowX === "auto"
      ) {
        return;
      }

      const wrapper = document.createElement("div");
      wrapper.className = "table-wrapper";
      wrapper.setAttribute("tabindex", "0");
      wrapper.setAttribute("role", "region");

      const caption = table.querySelector("caption");
      if (caption) {
        if (!caption.id) {
          caption.id = generateUniqueId(
            caption.textContent || "table",
            tableUsedIds,
          );
        }
        tableUsedIds.add(caption.id);
        wrapper.setAttribute("aria-labelledby", caption.id);
      } else {
        wrapper.setAttribute("aria-label", "Table content");
      }

      table.parentNode.insertBefore(wrapper, table);
      wrapper.appendChild(table);
    });

    // Copy to Clipboard
    const codeBlocks = document.querySelectorAll("pre");
    codeBlocks.forEach((pre) => {
      if (pre.parentNode.classList.contains("code-wrapper")) return;
      if (!pre.textContent.trim()) return;

      // 🎨 Palette UX: Keyboard access for overflow code
      pre.setAttribute("tabindex", "0");
      pre.setAttribute("role", "region");
      pre.setAttribute("aria-label", "Code snippet");

      const wrapper = document.createElement("div");
      wrapper.className = "code-wrapper";
      pre.parentNode.insertBefore(wrapper, pre);
      wrapper.appendChild(pre);

      const button = document.createElement("button");
      button.className = "copy-btn";
      button.textContent = "Copy";
      button.setAttribute("aria-label", "Copy code to clipboard");
      button.type = "button";
      // ⚡ Bolt Optimization: Use data attribute for delegation instead of adding N listeners
      button.dataset.action = "copy-code";

      wrapper.appendChild(button);
    });

    // ⚡ Bolt Optimization: Global Event Delegation for Copy Buttons
    // Reduces memory usage by removing closures and event listeners per button
    document.addEventListener("click", async (e) => {
      const button = e.target.closest('button[data-action="copy-code"]');
      if (!button) return;

      // Verify it's our copy button (double check class)
      if (!button.classList.contains("copy-btn")) return;

      // Find associated pre element relative to the button
      // Structure: .code-wrapper > pre + button
      const wrapper = button.closest(".code-wrapper");
      if (!wrapper) return;

      const pre = wrapper.querySelector("pre");
      if (!pre) return;

      try {
        await navigator.clipboard.writeText(pre.innerText || pre.textContent);
        button.textContent = "Copied!";
        button.setAttribute("aria-label", "Code copied to clipboard");
        button.classList.add("copied");
        setTimeout(() => {
          button.textContent = "Copy";
          button.setAttribute("aria-label", "Copy code to clipboard");
          button.classList.remove("copied");
        }, 2000);
      } catch (err) {
        console.error("Failed to copy:", err);
        button.textContent = "Error";
        setTimeout(() => (button.textContent = "Copy"), 2000);
      }
    });

    // Form Accessibility - Required Field Indicators
    const requiredInputs = document.querySelectorAll(
      "input[required], textarea[required], select[required]",
    );
    requiredInputs.forEach((input) => {
      if (input.id) {
        const label = document.querySelector(`label[for="${input.id}"]`);
        if (label && !label.querySelector(".required-indicator")) {
          const indicator = document.createElement("span");
          indicator.className = "required-indicator";
          indicator.textContent = " *";
          indicator.style.color = "var(--accent-blue)";
          indicator.style.fontWeight = "bold";
          indicator.setAttribute("aria-hidden", "true");
          indicator.title = "Required field";
          label.appendChild(indicator);
        }
      }
    });
  });

  // Skip to Content Link
  if (!document.querySelector(".skip-to-content")) {
    const skipLink = document.createElement("a");
    skipLink.href = "#quarto-document-content";
    skipLink.className = "skip-to-content";
    skipLink.textContent = "Skip to main content";
    skipLink.setAttribute("aria-label", "Skip to main content");

    // Manage focus for accessibility
    skipLink.addEventListener("click", (e) => {
      const targetId = skipLink.getAttribute("href").substring(1);
      const targetElement = document.getElementById(targetId);
      if (targetElement) {
        if (!targetElement.getAttribute("tabindex")) {
          targetElement.setAttribute("tabindex", "-1");
        }
        targetElement.focus({ preventScroll: true });
      }
    });

    if (document.body.firstChild) {
      document.body.insertBefore(skipLink, document.body.firstChild);
    } else {
      document.body.appendChild(skipLink);
    }
  }

  // ⚡ Bolt Optimization: Reading Time Estimate
  function initReadingTime() {
    // Only run on article pages in the /articles/ subdirectory
    if (!window.location.pathname.includes("/articles/")) return;

    const articleContent = document.getElementById("quarto-document-content");
    if (!articleContent) return;

    // Use the article body text for calculation
    // ⚡ Bolt Optimization: Prefer textContent to avoid reflow (layout thrashing) from innerText
    const text = articleContent.textContent || articleContent.innerText;

    // ⚡ Bolt Optimization: Manual character iteration to count words
    // Avoids creating an array of strings like .split(/\s+/) which causes high GC pressure
    // O(1) memory, O(N) CPU
    let wordCount = 0;
    let inWord = false;
    const len = text.length;
    for (let i = 0; i < len; i++) {
      const c = text.charCodeAt(i);
      // Check for whitespace: Space(32), Tab(9), LF(10), CR(13), NBSP(160)
      // Also Form Feed (12)
      if (
        c === 32 ||
        c === 9 ||
        c === 10 ||
        c === 13 ||
        c === 160 ||
        c === 12
      ) {
        inWord = false;
      } else {
        if (!inWord) wordCount++;
        inWord = true;
      }
    }

    // Average reading speed (words per minute)
    const wordsPerMinute = 225;
    const minutes = Math.ceil(wordCount / wordsPerMinute);

    // Create the reading time element
    const timeDiv = document.createElement("div");
    timeDiv.className = "reading-time-estimate";
    timeDiv.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-clock" viewBox="0 0 16 16" style="vertical-align: text-bottom; margin-right: 5px; opacity: 0.8;" aria-hidden="true">
                <path d="M8 3.5a.5.5 0 0 0-1 0V9a.5.5 0 0 0 .252.434l3.5 2a.5.5 0 0 0 .496-.868L8 8.71V3.5z"/>
                <path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm7-8A7 7 0 1 1 1 8a7 7 0 0 1 14 0z"/>
            </svg>
            <span>${minutes} min read</span>
        `;

    // Style the element
    Object.assign(timeDiv.style, {
      marginBottom: "1.5rem",
      color: "var(--text-light)",
      fontStyle: "italic",
      display: "flex",
      alignItems: "center",
      fontSize: "0.95rem",
      fontWeight: "500",
    });

    timeDiv.setAttribute(
      "aria-label",
      `Estimated reading time: ${minutes} minutes`,
    );

    // Insert logic: Try to insert after the header if it exists and is visible
    const header = document.getElementById("title-block-header");
    // ⚡ Bolt Optimization: Check offsetParent instead of getComputedStyle to avoid forced layout
    // offsetParent is null if display: none or parent is hidden
    const isHeaderVisible = header && header.offsetParent !== null;

    if (isHeaderVisible) {
      // Check if meta block exists inside header
      const meta = header.querySelector(".quarto-title-meta");
      if (meta) {
        meta.appendChild(timeDiv);
      } else {
        header.appendChild(timeDiv);
      }
    } else {
      // Fallback: insert at the top of the content
      articleContent.insertBefore(timeDiv, articleContent.firstChild);
    }
  }
  initReadingTime();

  // 🎨 Palette UX: Lightbox for Article Images
  // Removed length check to allow dynamic injection and more robust initialization
  // Always initialize lightbox container if content area exists
  const articleContainer = document.getElementById("quarto-document-content");
  if (articleContainer) {
    // ⚡ Bolt Optimization: Use getElementsByTagName (O(1) Live Collection) instead of querySelectorAll (O(N))
    const contentImages = articleContainer.getElementsByTagName("img");
    let lastFocusedElement = null; // 🎨 Palette UX: Track focus for restoration

    const lightbox = document.createElement("div");
    lightbox.className = "lightbox-overlay";
    lightbox.setAttribute("tabindex", "-1"); // 🎨 Palette UX: Allow programmatic focus
    lightbox.style.outline = "none"; // 🎨 Palette UX: Remove outline on container
    lightbox.setAttribute("aria-hidden", "true");
    lightbox.setAttribute("role", "dialog");
    lightbox.setAttribute("aria-modal", "true");
    lightbox.setAttribute("aria-label", "Image zoom"); // 🎨 Palette UX: Accessible name

    // 🎨 Palette UX: Create Close Button
    const closeBtn = document.createElement("button");
    closeBtn.className = "lightbox-close";
    closeBtn.setAttribute("aria-label", "Close zoom");
    closeBtn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>`;

    // Close on click (Background)
    lightbox.addEventListener("click", (e) => {
      if (e.target !== lightbox) return;
      closeLightbox();
    });

    // Close on click (Button)
    closeBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      closeLightbox();
    });

    // 🎨 Palette UX: Trap focus inside lightbox
    lightbox.addEventListener("keydown", (e) => {
      if (e.key !== "Tab") return;

      const focusableSelector =
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
      const focusableContent = lightbox.querySelectorAll(focusableSelector);

      if (focusableContent.length === 0) return;

      const firstFocusable = focusableContent[0];
      const lastFocusable = focusableContent[focusableContent.length - 1];

      if (e.shiftKey) {
        if (document.activeElement === firstFocusable) {
          lastFocusable.focus();
          e.preventDefault();
        }
      } else {
        if (document.activeElement === lastFocusable) {
          firstFocusable.focus();
          e.preventDefault();
        }
      }
    });

    function closeLightbox() {
      lightbox.classList.remove("active");
      lightbox.setAttribute("aria-hidden", "true");
      lightbox.innerHTML = ""; // Clear content

      // 🎨 Palette UX: Restore focus
      if (lastFocusedElement) {
        lastFocusedElement.focus();
        lastFocusedElement = null;
      }
    }

    document.body.appendChild(lightbox);

    // Initial pass for existing images
    for (const img of contentImages) {
      // Skip if already inside a link or interactive element
      if (img.closest("a") || img.closest("button")) continue;

      img.classList.add("zoomable");
      img.setAttribute("tabindex", "0"); // Keyboard focusable
      img.setAttribute("role", "button");
      img.setAttribute("aria-label", "Zoom image");
    }

    // ⚡ Bolt Optimization: Event Delegation for Lightbox
    // Instead of adding listeners to every image (O(N)), add one listener to the container (O(1))
    const handleLightboxTrigger = (e) => {
      const img = e.target.closest(".zoomable");
      if (!img) return;

      // Verify the image is within our content area (safety check)
      if (!articleContainer.contains(img)) return;

      if (e.type === "keydown" && e.key !== "Enter" && e.key !== " ") return;

      e.preventDefault();

      // 🎨 Palette UX: Capture focus
      lastFocusedElement = document.activeElement;

      const clone = img.cloneNode();
      clone.className = "lightbox-img";
      clone.removeAttribute("loading"); // Ensure it loads immediately
      clone.removeAttribute("id"); // Prevent duplicate IDs
      // Remove interactive attributes from clone
      clone.removeAttribute("tabindex");
      clone.removeAttribute("role");
      clone.removeAttribute("aria-label");
      clone.classList.remove("zoomable");

      lightbox.innerHTML = ""; // Clear previous
      lightbox.appendChild(clone);
      lightbox.appendChild(closeBtn); // 🎨 Palette UX: Add close button

      // 🎨 Palette UX: Handle Caption
      const figure = img.closest("figure");
      if (figure) {
        const figcaption = figure.querySelector("figcaption");
        if (figcaption) {
          const captionClone = figcaption.cloneNode(true);
          captionClone.className = "lightbox-caption";
          lightbox.appendChild(captionClone);
        }
      }

      lightbox.classList.add("active");
      lightbox.setAttribute("aria-hidden", "false");

      // 🎨 Palette UX: Move focus to close button for better keyboard UX
      closeBtn.focus();
    };

    articleContainer.addEventListener("click", handleLightboxTrigger);
    articleContainer.addEventListener("keydown", handleLightboxTrigger);

    // Close on Escape
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && lightbox.classList.contains("active")) {
        closeLightbox();
      }
    });
  }

  // --- PDF Download Button ---
  initPDFDownload();

  // --- Layman's Terms Toggle ---
  initLaymansTermsToggle();

  // --- Critics Corner Toggle ---
  initCriticsCorner();

  // --- Critics Comments Toggle ---
  initCriticsCommentsToggle();

  // --- Contact Form Feedback ---
  initContactFormFeedback();
});

// 🎨 Palette UX: Auto-growing Textareas
function initAutoGrowTextareas() {
  const textareas = document.querySelectorAll("textarea");
  if (textareas.length === 0) return;

  function adjustHeight(el) {
    el.style.height = "auto";
    const newHeight = Math.min(el.scrollHeight, 500); // Max height 500px
    el.style.height = newHeight + "px";
    el.style.overflowY = newHeight >= 500 ? "auto" : "hidden";
  }

  textareas.forEach((textarea) => {
    // Initial adjustment if content exists
    if (textarea.value) {
      // Defer slightly to ensure styles are applied
      setTimeout(() => adjustHeight(textarea), 0);
    }

    textarea.addEventListener("input", () => adjustHeight(textarea));
  });

  // Single resize listener for all
  window.addEventListener(
    "resize",
    debounce(() => {
      textareas.forEach(adjustHeight);
    }, 250),
  );
}
runWhenIdle(initAutoGrowTextareas);

// 🎨 Palette UX: Contact Form Feedback
function initContactFormFeedback() {
  // ⚡ Bolt Optimization: Use document.forms to avoid extra DOM query; still iterates over all forms
  for (const form of document.forms) {
    if (!form.action || !form.action.startsWith("mailto:")) continue;

    form.addEventListener("submit", (e) => {
      // Do NOT prevent default - let the browser open the mail client
      // But update the UI to show something happened

      const button = form.querySelector('button[type="submit"]');
      if (!button) return;

      // Save original state
      if (!button.dataset.originalHtml) {
        button.dataset.originalHtml = button.innerHTML;
      }

      // Update state (allow expansion)
      button.innerHTML = "Opening Email Client...";

      // Manually apply style changes if .success class is missing
      const originalBg = button.style.backgroundColor;
      const originalBorder = button.style.borderColor;

      // Check if .success is defined in CSS, if not, apply inline
      // Note: We use existing 'success' class if available (e.g. from copy-btn), otherwise fallback
      button.classList.add("success");

      // Disable briefly to prevent double clicks while app opens
      button.disabled = true;

      // Revert after delay
      setTimeout(() => {
        button.innerHTML = button.dataset.originalHtml;
        button.classList.remove("success");
        button.disabled = false;
      }, 3000);
    });
  }
}

// --- PDF Download Functionality ---
function initPDFDownload() {
  // Don't add button on home page or if already exists
  if (document.querySelector('.home-layout') || document.querySelector('.pdf-download-btn')) {
    return;
  }

  // Create the PDF download button
  const pdfBtn = document.createElement('button');
  pdfBtn.className = 'pdf-download-btn';
  pdfBtn.setAttribute('aria-label', 'Download page as PDF');
  pdfBtn.setAttribute('title', 'Download as PDF');
  pdfBtn.innerHTML = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20M12,19L8,15H10.5V12H13.5V15H16L12,19Z"/>
    </svg>
    <span>PDF</span>
  `;

  pdfBtn.addEventListener('click', function() {
    preparePDFPrint();
  });

  document.body.appendChild(pdfBtn);
}

function preparePDFPrint() {
  // Get page title
  const pageTitle = document.title.replace(' – AffineDrift', '').replace('AffineDrift – ', '');

  // Create print title block if it doesn't exist
  let printTitleBlock = document.querySelector('.print-title-block');
  if (!printTitleBlock) {
    printTitleBlock = document.createElement('div');
    printTitleBlock.className = 'print-title-block';
    printTitleBlock.style.display = 'none'; // Hidden until print
    printTitleBlock.innerHTML = `
      <h1>${pageTitle}</h1>
      <div class="print-author">AffineDrift</div>
      <div class="print-date">${new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</div>
    `;

    // Insert at start of main content
    const mainContent = document.querySelector('.main-content-area') ||
                       document.querySelector('main.content') ||
                       document.querySelector('#quarto-content');
    if (mainContent) {
      mainContent.insertBefore(printTitleBlock, mainContent.firstChild);
    }
  }

  // Ensure MathJax is fully rendered before printing
  if (window.MathJax && window.MathJax.typesetPromise) {
    MathJax.typesetPromise().then(() => {
      // Small delay to ensure rendering is complete
      setTimeout(() => {
        window.print();
      }, MATHJAX_RENDER_DELAY_MS);
    }).catch((err) => {
      console.error('MathJax typeset error, printing anyway:', err);
      window.print();
    });
  } else {
    window.print();
  }
}

// --- Layman's Terms Functionality ---
function initLaymansTermsToggle() {
  const laymansSections = document.querySelectorAll(".laymans-terms");

  laymansSections.forEach((section, index) => {
    const header = section.querySelector(".laymans-terms-header");
    const content = section.querySelector(".laymans-terms-content");

    if (!header || !content) return;

    if (!content.id) {
      content.id = `laymans-terms-content-${index + 1}`;
    }

    header.setAttribute("aria-controls", content.id);

    const isExpanded = header.getAttribute("aria-expanded") === "true";
    content.setAttribute("aria-hidden", String(!isExpanded));

    header.addEventListener("click", () => {
      const expanded = header.getAttribute("aria-expanded") === "true";
      header.setAttribute("aria-expanded", String(!expanded));
      content.setAttribute("aria-hidden", String(expanded));
    });
  });
}

// --- Critics Corner Functionality ---
function initCriticsCorner() {
  const criticsCorners = document.querySelectorAll('.critics-corner');

  criticsCorners.forEach((corner, index) => {
    const header = corner.querySelector('.critics-corner-header');
    const content = corner.querySelector('.critics-corner-content');

    if (header && content) {
      if (!content.id) {
        content.id = `critics-corner-content-${index + 1}`;
      }

      header.setAttribute('aria-controls', content.id);

      const isExpandedInitial = header.getAttribute('aria-expanded') === 'true';
      content.setAttribute('aria-hidden', String(!isExpandedInitial));

      // Set initial state
      content.style.maxHeight = '0';
      content.style.overflow = 'hidden';
      content.style.transition = 'max-height 0.4s ease-out, padding 0.4s ease-out';

      header.addEventListener('click', function() {
        const isExpanded = header.getAttribute('aria-expanded') === 'true';

        if (isExpanded) {
          // Collapse
          content.style.maxHeight = '0';
          content.style.paddingTop = '0';
          content.style.paddingBottom = '0';
          header.setAttribute('aria-expanded', 'false');
          content.setAttribute('aria-hidden', 'true');
        } else {
          // Expand
          content.style.maxHeight = content.scrollHeight + CRITICS_CORNER_PADDING_OFFSET + 'px';
          content.style.paddingTop = '1rem';
          content.style.paddingBottom = '1rem';
          header.setAttribute('aria-expanded', 'true');
          content.setAttribute('aria-hidden', 'false');
        }
      });
    }
  });
}

// --- Critics Comments Functionality ---
function initCriticsCommentsToggle() {
  const criticsSections = document.querySelectorAll(".critics-comments");

  criticsSections.forEach((section, index) => {
    const header = section.querySelector(".critics-comments-header");
    const content = section.querySelector(".critics-comments-content");

    if (!header || !content) return;

    if (!content.id) {
      content.id = `critics-comments-content-${index + 1}`;
    }

    header.setAttribute("aria-controls", content.id);

    const isExpanded = header.getAttribute("aria-expanded") === "true";
    content.setAttribute("aria-hidden", String(!isExpanded));

    header.addEventListener("click", () => {
      const expanded = header.getAttribute("aria-expanded") === "true";
      header.setAttribute("aria-expanded", String(!expanded));
      content.setAttribute("aria-hidden", String(expanded));
    });
  });
}

// Utility function for future features
function scrollToTop() {
  window.scrollTo({
    top: 0,
    behavior: "smooth",
  });
}

// Accessibility: Add ARIA labels to navigation elements
function initAriaLabels() {
  // Add ARIA labels to navigation elements
  const navElements = document.querySelectorAll('nav');
  navElements.forEach((nav) => {
    if (!nav.hasAttribute('aria-label')) {
      // Determine label based on class or heading
      if (nav.classList.contains('toc-nav')) {
        nav.setAttribute('aria-label', 'Table of contents navigation');
      } else if (nav.classList.contains('history-nav')) {
        nav.setAttribute('aria-label', 'Recent history navigation');
      } else if (nav.classList.contains('resources-nav')) {
        nav.setAttribute('aria-label', 'Resources navigation');
      } else {
        nav.setAttribute('aria-label', 'Navigation');
      }
    }
  });

  // Add ARIA labels to sidebar elements
  const sidebars = document.querySelectorAll('aside');
  sidebars.forEach((sidebar) => {
    if (!sidebar.hasAttribute('aria-label')) {
      if (sidebar.classList.contains('left-sidebar')) {
        sidebar.setAttribute('aria-label', 'Left sidebar navigation');
      } else if (sidebar.classList.contains('right-sidebar')) {
        sidebar.setAttribute('aria-label', 'Right sidebar navigation');
      } else if (sidebar.classList.contains('home-sidebar')) {
        sidebar.setAttribute('aria-label', 'Main navigation sidebar');
      } else {
        sidebar.setAttribute('aria-label', 'Sidebar');
      }
    }
  });

  // Add ARIA labels to main content areas
  const mainElements = document.querySelectorAll('main');
  mainElements.forEach((main) => {
    if (!main.hasAttribute('aria-label') && !main.hasAttribute('role')) {
      main.setAttribute('role', 'main');
      main.setAttribute('aria-label', 'Main content');
    }
  });

  // Add ARIA labels to search inputs
  const searchInputs = document.querySelectorAll('input[type="search"]');
  searchInputs.forEach((input) => {
    if (!input.hasAttribute('aria-label') && !input.id) {
      input.setAttribute('aria-label', 'Search');
    }
  });

  // Add ARIA labels to social links
  const socialLinks = document.querySelectorAll('.social-link');
  socialLinks.forEach((link) => {
    if (!link.hasAttribute('aria-label')) {
      const text = link.textContent.trim();
      link.setAttribute('aria-label', `Visit ${text}`);
    }
  });

  // Add ARIA labels to resource cards
  const resourceCards = document.querySelectorAll('.resource-card');
  resourceCards.forEach((card) => {
    if (!card.hasAttribute('aria-label')) {
      const heading = card.querySelector('h3');
      if (heading) {
        card.setAttribute('aria-label', `Resource: ${heading.textContent.trim()}`);
      }
    }
  });

  // Add ARIA labels to article cards
  const articleCards = document.querySelectorAll('.article-card');
  articleCards.forEach((card) => {
    if (!card.hasAttribute('aria-label')) {
      const heading = card.querySelector('h3');
      if (heading) {
        card.setAttribute('aria-label', `Article: ${heading.textContent.trim()}`);
      }
    }
  });

  // Add ARIA live region for dynamic content
  const historyLists = document.querySelectorAll('[id$="-history-list"]');
  historyLists.forEach((list) => {
    if (!list.hasAttribute('aria-live')) {
      list.setAttribute('aria-live', 'polite');
      list.setAttribute('aria-atomic', 'false');
    }
  });

  // Add ARIA labels to form elements without labels
  const formInputs = document.querySelectorAll('input:not([aria-label]):not([id])');
  formInputs.forEach((input) => {
    const placeholder = input.getAttribute('placeholder');
    if (placeholder) {
      input.setAttribute('aria-label', placeholder);
    }
  });
}

// Run ARIA labels initialization when DOM is ready
runOnDomReady(initAriaLabels);

// Export for potential module use
if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    scrollToTop,
    debounce,
    generateUniqueId,
    getScrollOffset,
    runOnDomReady,
    runWhenIdle,
    MAX_ID_GENERATION_ATTEMPTS,
    MATHJAX_RENDER_DELAY_MS,
    CRITICS_CORNER_PADDING_OFFSET,
    initAriaLabels,
  };
}
