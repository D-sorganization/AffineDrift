/**
 * AffineDrift - Accessibility Module
 * Handles all accessibility features and ARIA labels
 */

import { runOnDomReady } from "./utils.js";

/**
 * Secure external links with proper attributes
 */
export function initSecureExternalLinks() {
    const currentHostname = window.location.hostname;
    for (const link of document.links) {
        if (
            link.hostname &&
            link.hostname !== currentHostname &&
            link.protocol.startsWith("http")
        ) {
            // ⚡ Bolt Optimization: Use property access and DOMTokenList
            // Avoids O(N) memory allocation from string split/join for every external link
            if (!link.target) {
                link.target = "_blank";
            }

            if (link.relList) {
                link.relList.add("noopener", "noreferrer");
            } else {
                const rel = link.getAttribute("rel") || "";
                const parts = rel.split(" ").filter((p) => p);
                if (!parts.includes("noopener")) parts.push("noopener");
                if (!parts.includes("noreferrer")) parts.push("noreferrer");
                link.setAttribute("rel", parts.join(" "));
            }

            if (
                link.getElementsByTagName("img").length === 0 &&
                link.getElementsByTagName("svg").length === 0 &&
                !link.classList.contains("external-link")
            ) {
                link.classList.add("external-link");
                const icon = document.createElement("span");
                icon.className = "external-link-icon";
                icon.setAttribute("aria-hidden", "true");
                icon.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>`;
                link.appendChild(icon);
            }
        }
    }
}

/**
 * Set external links on GitHub repos
 */
export function initRepoLinks() {
    // ⚡ Bolt Optimization: Use document.links (O(1)) instead of querySelectorAll (O(N))
    for (const link of document.links) {
        if (
            link.href.startsWith("https://github.com") &&
            link.closest(".navbar-nav")
        ) {
            link.setAttribute("target", "_blank");
        }
    }
}

/**
 * Initialize all ARIA labels for accessibility
 */
export function initAriaLabels() {
    // Navigation elements
    const navElements = document.getElementsByTagName("nav");
    for (const nav of navElements) {
        if (!nav.hasAttribute("aria-label")) {
            if (nav.classList.contains("toc-nav")) {
                nav.setAttribute("aria-label", "Table of contents navigation");
            } else if (nav.classList.contains("history-nav")) {
                nav.setAttribute("aria-label", "Recent history navigation");
            } else if (nav.classList.contains("resources-nav")) {
                nav.setAttribute("aria-label", "Resources navigation");
            } else {
                nav.setAttribute("aria-label", "Navigation");
            }
        }
    }

    // Sidebar elements
    const sidebars = document.getElementsByTagName("aside");
    for (const sidebar of sidebars) {
        if (!sidebar.hasAttribute("aria-label")) {
            if (sidebar.classList.contains("left-sidebar")) {
                sidebar.setAttribute("aria-label", "Left sidebar navigation");
            } else if (sidebar.classList.contains("right-sidebar")) {
                sidebar.setAttribute("aria-label", "Right sidebar navigation");
            } else if (sidebar.classList.contains("home-sidebar")) {
                sidebar.setAttribute("aria-label", "Main navigation sidebar");
            } else {
                sidebar.setAttribute("aria-label", "Sidebar");
            }
        }
    }

    // Main content areas
    const mainElements = document.getElementsByTagName("main");
    for (const main of mainElements) {
        if (!main.hasAttribute("aria-label") && !main.hasAttribute("role")) {
            main.setAttribute("role", "main");
            main.setAttribute("aria-label", "Main content");
        }
    }

    // Social links
    const socialLinks = document.getElementsByClassName("social-link");
    for (const link of socialLinks) {
        if (!link.hasAttribute("aria-label")) {
            const text = link.textContent.trim();
            link.setAttribute("aria-label", `Visit ${text}`);
        }
    }

    // Resource cards
    const resourceCards = document.getElementsByClassName("resource-card");
    for (const card of resourceCards) {
        if (!card.hasAttribute("aria-label")) {
            const heading = card.querySelector("h3");
            if (heading) {
                card.setAttribute(
                    "aria-label",
                    `Resource: ${heading.textContent.trim()}`
                );
            }
        }
    }

    // Article cards
    const articleCards = document.getElementsByClassName("article-card");
    for (const card of articleCards) {
        if (!card.hasAttribute("aria-label")) {
            const heading = card.querySelector("h3");
            if (heading) {
                card.setAttribute(
                    "aria-label",
                    `Article: ${heading.textContent.trim()}`
                );
            }
        }
    }

    // History lists - live regions
    const historyLists = document.querySelectorAll('[id$="-history-list"]');
    for (const list of historyLists) {
        if (!list.hasAttribute("aria-live")) {
            list.setAttribute("aria-live", "polite");
            list.setAttribute("aria-atomic", "false");
        }
    }

    // Input elements (Search and generic forms)
    const inputs = document.getElementsByTagName("input");
    for (const input of inputs) {
        if (!input.hasAttribute("aria-label") && !input.id) {
            if (input.type === "search") {
                input.setAttribute("aria-label", "Search");
            } else {
                const placeholder = input.getAttribute("placeholder");
                if (placeholder) {
                    input.setAttribute("aria-label", placeholder);
                }
            }
        }
    }
}

/**
 * Initialize reading time estimate for articles
 */
export function initReadingTime() {
    if (!window.location.pathname.includes("/articles/")) return;

    const articleContent = document.getElementById("quarto-document-content");
    if (!articleContent) return;

    const text = articleContent.textContent || articleContent.innerText;

    let wordCount = 0;
    let inWord = false;
    const len = text.length;
    for (let i = 0; i < len; i++) {
        const c = text.charCodeAt(i);
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

    const wordsPerMinute = 225;
    const minutes = Math.ceil(wordCount / wordsPerMinute);

    const timeDiv = document.createElement("div");
    timeDiv.className = "reading-time-estimate";
    timeDiv.innerHTML = `
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-clock" viewBox="0 0 16 16" style="vertical-align: text-bottom; margin-right: 5px; opacity: 0.8;" aria-hidden="true">
      <path d="M8 3.5a.5.5 0 0 0-1 0V9a.5.5 0 0 0 .252.434l3.5 2a.5.5 0 0 0 .496-.868L8 8.71V3.5z"/>
      <path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm7-8A7 7 0 1 1 1 8a7 7 0 0 1 14 0z"/>
    </svg>
    <span>${minutes} min read</span>
  `;

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
        `Estimated reading time: ${minutes} minutes`
    );

    const header = document.getElementById("title-block-header");
    const isHeaderVisible = header && header.offsetParent !== null;

    if (isHeaderVisible) {
        const meta = header.querySelector(".quarto-title-meta");
        if (meta) {
            meta.appendChild(timeDiv);
        } else {
            header.appendChild(timeDiv);
        }
    } else {
        articleContent.insertBefore(timeDiv, articleContent.firstChild);
    }
}
