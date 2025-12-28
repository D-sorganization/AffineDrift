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
  if (typeof window !== "undefined") {
    const value = getComputedStyle(document.documentElement).getPropertyValue(
      "--scroll-offset",
    );
    return value ? parseInt(value) : 140;
  }
  return 140;
};
const HEADER_OFFSET = getScrollOffset(); // Smooth scrolling offset
const TOC_SCROLL_OFFSET = HEADER_OFFSET; // Active section detection offset
const MAX_ID_GENERATION_ATTEMPTS = 100;

// Helper function to debounce events
function debounce(func, wait) {
  let timeout;
  return function (...args) {
    const context = this;
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(context, args), wait);
  };
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

document.addEventListener("DOMContentLoaded", function () {
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
          window.bootstrap?.Collapse?.getInstance?.(navbarCollapse);
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
  updateHistorySidebar();

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

  // ScrollSpy for Table of Contents
  function initScrollSpy() {
    const tocLinks = document.querySelectorAll("#toc-list a");
    if (tocLinks.length === 0) return;

    const sections = document.querySelectorAll(
      ".page-section[id], section[id]",
    );
    const visibleSections = new Set();

    const observerOptions = {
      root: null,
      rootMargin: "-100px 0px -60% 0px",
      threshold: 0,
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          visibleSections.add(entry.target.id);
        } else {
          visibleSections.delete(entry.target.id);
        }
      });

      // Find the first visible section in DOM order
      let activeId = null;
      for (const section of sections) {
        if (visibleSections.has(section.id)) {
          activeId = section.id;
          break;
        }
      }

      if (activeId) {
        tocLinks.forEach((link) => {
          if (link.getAttribute("href") === `#${activeId}`) {
            link.classList.add("active");
          } else {
            link.classList.remove("active");
          }
        });
      }
    }, observerOptions);

    sections.forEach((section) => {
      if (document.querySelector(`#toc-list a[href="#${section.id}"]`)) {
        observer.observe(section);
      }
    });
  }
  initScrollSpy();

  // Lazy load images
  if ("loading" in HTMLImageElement.prototype) {
    document.querySelectorAll("img[src]").forEach((img) => {
      if (!img.hasAttribute("loading")) {
        img.setAttribute("loading", "lazy");
      }
    });
  }

  // Accordion functionality
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
    header.addEventListener("click", function () {
      const isExpanded = this.getAttribute("aria-expanded") === "true";
      this.setAttribute("aria-expanded", !isExpanded);
      if (content && content.classList.contains("accordion-content")) {
        content.setAttribute("aria-hidden", isExpanded);
      }
    });
  });

  // Repository links
  document
    .querySelectorAll('.navbar-nav a[href^="https://github.com"]')
    .forEach((link) => {
      link.setAttribute("target", "_blank");
      // rel handled by secure external links below
    });

  // Secure external links
  const currentHostname = window.location.hostname;
  document.querySelectorAll('a[href^="http"]').forEach((link) => {
    // ⚡ Bolt Optimization: Use link.hostname instead of new URL() to avoid object creation overhead
    if (link.hostname && link.hostname !== currentHostname) {
      if (!link.hasAttribute("target")) {
        link.setAttribute("target", "_blank");
      }
      const rel = link.getAttribute("rel") || "";
      const parts = rel.split(" ").filter((p) => p);
      if (!parts.includes("noopener")) parts.push("noopener");
      if (!parts.includes("noreferrer")) parts.push("noreferrer");
      link.setAttribute("rel", parts.join(" "));
      if (!link.querySelector("img, svg")) {
        link.classList.add("external-link");
      }
    }
  });

  // Log page load for analytics (optional)
  console.log("AffineDrift loaded successfully");
  console.log("Mathematical notation rendering via MathJax");

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
  initArticleHistory();

  // Copy to Clipboard
  const codeBlocks = document.querySelectorAll("pre");
  codeBlocks.forEach((pre) => {
    if (pre.parentNode.classList.contains("code-wrapper")) return;
    if (!pre.textContent.trim()) return;

    const wrapper = document.createElement("div");
    wrapper.className = "code-wrapper";
    pre.parentNode.insertBefore(wrapper, pre);
    wrapper.appendChild(pre);

    const button = document.createElement("button");
    button.className = "copy-btn";
    button.textContent = "Copy";
    button.setAttribute("aria-label", "Copy code to clipboard");
    button.type = "button";

    button.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(pre.innerText || pre.textContent);
        button.textContent = "Copied!";
        button.classList.add("copied");
        setTimeout(() => {
          button.textContent = "Copy";
          button.classList.remove("copied");
        }, 2000);
      } catch (err) {
        console.error("Failed to copy:", err);
        button.textContent = "Error";
        setTimeout(() => (button.textContent = "Copy"), 2000);
      }
    });
    wrapper.appendChild(button);
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

  // ⚡ Bolt Optimization: Reading Time Estimate
  function initReadingTime() {
    // Only run on article pages in the /articles/ subdirectory
    if (!window.location.pathname.includes("/articles/")) return;

    const articleContent = document.getElementById("quarto-document-content");
    if (!articleContent) return;

    // Use the article body text for calculation
    // ⚡ Bolt Optimization: Prefer textContent to avoid reflow (layout thrashing) from innerText
    const text = articleContent.textContent || articleContent.innerText;
    // Simple word count estimate
    const wordCount = text.trim().split(/\s+/).length;
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
    const headerDisplay = header ? getComputedStyle(header).display : "null";

    if (header && headerDisplay !== "none") {
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
  const contentImages = document.querySelectorAll(
    "#quarto-document-content img",
  );
  if (contentImages.length > 0) {
    const lightbox = document.createElement("div");
    lightbox.className = "lightbox-overlay";
    lightbox.setAttribute("aria-hidden", "true");
    lightbox.setAttribute("role", "dialog");
    lightbox.setAttribute("aria-modal", "true");

    // Close on click
    lightbox.addEventListener("click", () => {
      lightbox.classList.remove("active");
      lightbox.setAttribute("aria-hidden", "true");
      lightbox.innerHTML = ""; // Clear content
    });
    document.body.appendChild(lightbox);

    contentImages.forEach((img) => {
      // Skip if already inside a link or interactive element
      if (img.closest("a") || img.closest("button")) return;

      img.classList.add("zoomable");
      img.setAttribute("tabindex", "0"); // Keyboard focusable
      img.setAttribute("role", "button");
      img.setAttribute("aria-label", "Zoom image");

      const openFn = (e) => {
        if (e.type === "keydown" && e.key !== "Enter" && e.key !== " ") return;
        e.preventDefault();
        const clone = img.cloneNode();
        clone.className = "lightbox-img";
        clone.removeAttribute("loading"); // Ensure it loads immediately
        clone.removeAttribute("id"); // Prevent duplicate IDs
        // Remove interactive attributes from clone
        clone.removeAttribute("tabindex");
        clone.removeAttribute("role");
        clone.removeAttribute("aria-label");
        clone.classList.remove("zoomable");

        lightbox.appendChild(clone);
        lightbox.classList.add("active");
        lightbox.setAttribute("aria-hidden", "false");
      };

      img.addEventListener("click", openFn);
      img.addEventListener("keydown", openFn);
    });

    // Close on Escape
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && lightbox.classList.contains("active")) {
        lightbox.click();
      }
    });
  }

  console.log("AffineDrift loaded successfully (Optimized)");
});

// Utility function for future features
function scrollToTop() {
  window.scrollTo({
    top: 0,
    behavior: "smooth",
  });
}

// Export for potential module use
if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    scrollToTop,
  };
}
