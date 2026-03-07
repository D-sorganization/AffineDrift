/**
 * AffineDrift - History Module
 * Handles browsing history sidebar and article history tracking
 */

import { runWhenIdle } from "./utils.js";

const MAX_HISTORY_TITLE_LENGTH = 40;
const MAX_HISTORY_ITEMS = 10;

/**
 * Update the history sidebar with recently visited pages
 */
export function updateHistorySidebar() {
    const historyList = document.getElementById("history-list");
    if (!historyList) return;

    let history = JSON.parse(
        localStorage.getItem("affinedrift_history") || "[]"
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

    if (isArticlePage && ARTICLE_PAGES.includes(currentUrl)) {
        let history = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
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
        const history = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
        articlesHistoryList.textContent = "";
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
