/**
 * AffineDrift - History Module
 * Handles browsing history sidebar and article history tracking
 */

import { runWhenIdle } from "./utils.js";

const MAX_HISTORY_TITLE_LENGTH = 40;
const MAX_HISTORY_ITEMS = 10;

function parseStoredHistory(key) {
    const raw = localStorage.getItem(key);
    if (!raw) return [];
    try {
        const parsed = JSON.parse(raw);
        return Array.isArray(parsed) ? parsed : [];
    } catch (_error) {
        localStorage.removeItem(key);
        return [];
    }
}

/**
 * Build a sanitized <li><a></a></li> entry for a history item, rejecting
 * any url whose resolved protocol isn't http(s).
 */
function createHistoryListItem(item, { truncateAt } = {}) {
    const li = document.createElement("li");
    const a = document.createElement("a");
    let safeUrl = "#";
    if (typeof item.url === "string") {
        try {
            const parsed = new URL(item.url, window.location.origin);
            if (parsed.protocol === "http:" || parsed.protocol === "https:") {
                safeUrl = parsed.href;
            }
        } catch (_error) {
            // Malformed URL: fall back to "#".
        }
    }
    a.href = safeUrl;
    a.textContent =
        truncateAt && item.title.length > truncateAt
            ? item.title.substring(0, truncateAt) + "..."
            : item.title;
    li.appendChild(a);
    return li;
}

/**
 * Build the "No recent articles yet" empty state, with a link back to the
 * articles index, shared by the global and per-article history sidebars.
 */
function createExploreArticlesEmptyState() {
    const li = document.createElement("li");
    li.className = "history-empty";
    const span = document.createElement("span");
    span.setAttribute("role", "status");
    span.setAttribute("aria-live", "polite");
    span.textContent = "No recent articles yet. ";
    li.appendChild(span);
    const a = document.createElement("a");
    a.href = "/resources/articles.html";
    a.textContent = "Explore articles";
    li.appendChild(a);
    return li;
}

/**
 * Update the history sidebar with recently visited pages
 */
export function updateHistorySidebar() {
    const historyList = document.getElementById("history-list");
    if (!historyList) return;

    let history = parseStoredHistory("affinedrift_history");

    let pageTitle = document.title;
    if (pageTitle.includes(" - AffineDrift")) {
        pageTitle = pageTitle.replace(" - AffineDrift", "");
    } else if (pageTitle.startsWith("AffineDrift - ")) {
        pageTitle = pageTitle.replace("AffineDrift - ", "");
    } else if (pageTitle === "AffineDrift") {
        pageTitle = "Home";
    }

    // ⚡ Bolt Optimization: Use lastIndexOf/substring instead of split().pop()
    // Avoids creating an array of path segments just to get the last item
    const path = window.location.pathname;
    const urlFromPath = path.substring(path.lastIndexOf("/") + 1);

    const currentPage = {
        title: pageTitle,
        url: urlFromPath || "index.html",
        fullUrl: window.location.href,
    };

    history = history.filter((item) => item.url !== currentPage.url);
    history.unshift(currentPage);
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
                /^(tools|contact|about|resources|articles|research-reviews|book-reviews|daydreams)/i
            )
    );

    historyList.textContent = "";
    if (displayHistory.length === 0) {
        historyList.appendChild(createExploreArticlesEmptyState());
    } else {
        const fragment = document.createDocumentFragment();
        for (const item of displayHistory) {
            fragment.appendChild(
                createHistoryListItem(item, { truncateAt: MAX_HISTORY_TITLE_LENGTH })
            );
        }
        historyList.appendChild(fragment);
    }
}

/**
 * Initialize article history tracking and display
 */
export function initArticleHistory() {
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
        "drift-control-ratio.html",
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
    // ⚡ Bolt Optimization: Use lastIndexOf/substring instead of split().pop()
    const currentUrl = currentPath.substring(currentPath.lastIndexOf("/") + 1) || "";
    const isArticlePage =
        currentPath.includes("/articles/") && currentUrl.endsWith(".html");

    if (isArticlePage && ARTICLE_PAGES.includes(currentUrl)) {
        let history = parseStoredHistory(STORAGE_KEY);
        const currentPage = {
            title: document.title
                .replace(" - AffineDrift", "")
                .replace("AffineDrift - ", ""),
            url: "articles/" + currentUrl,
        };

        history = history.filter((item) => item.url !== currentPage.url);
        history.unshift(currentPage);
        history = history.slice(0, 10);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
    }

    const articlesHistoryList = document.getElementById("articles-history-list");
    if (articlesHistoryList) {
        const history = parseStoredHistory(STORAGE_KEY);
        articlesHistoryList.textContent = "";
        if (!history || history.length === 0) {
            articlesHistoryList.appendChild(createExploreArticlesEmptyState());
        } else {
            const fragment = document.createDocumentFragment();
            for (const item of history) {
                fragment.appendChild(createHistoryListItem(item));
            }
            articlesHistoryList.appendChild(fragment);
        }
    }
}

/**
 * Initialize a category-scoped "recently viewed" sidebar (e.g. "Recent
 * Models"), shared by pages that track visits across a small, fixed set of
 * sibling pages within one section.
 *
 * @param {Object} options
 * @param {string} options.listElementId - id of the <ul> to populate
 * @param {string} options.storageKey - localStorage key for this category
 * @param {string} options.emptyMessage - text shown when history is empty
 * @param {string[]} options.pages - filenames tracked for this category
 * @param {string} options.fallbackUrl - url used when the pathname has no segment
 */
export function initCategoryHistory({ listElementId, storageKey, emptyMessage, pages, fallbackUrl }) {
    const listEl = document.getElementById(listElementId);
    if (!listEl) return;

    let history = parseStoredHistory(storageKey);

    const path = window.location.pathname;
    const currentPage = {
        title: document.title.replace(" - AffineDrift", "").replace("AffineDrift - ", ""),
        url: path.substring(path.lastIndexOf("/") + 1) || fallbackUrl,
    };

    if (pages.includes(currentPage.url)) {
        history = history.filter((item) => item.url !== currentPage.url);
        history.unshift(currentPage);
        history = history.slice(0, MAX_HISTORY_ITEMS);
        localStorage.setItem(storageKey, JSON.stringify(history));
    }

    listEl.textContent = "";
    if (history.length === 0) {
        const li = document.createElement("li");
        li.className = "history-empty";
        li.textContent = emptyMessage;
        listEl.appendChild(li);
        return;
    }

    const fragment = document.createDocumentFragment();
    for (const item of history) {
        fragment.appendChild(createHistoryListItem(item));
    }
    listEl.appendChild(fragment);
}
