/**
 * AffineDrift - Page Feedback Module
 * Per-page "Was this helpful? / Report a problem" footer control (#4605).
 *
 * "Was this helpful?" is a local, unsent UI toggle — no analytics call is
 * made. "Report a problem" opens a prefilled GitHub issue from the
 * content-correction template with the page URL and build revision; a
 * mailto fallback covers readers without a GitHub account. The only
 * network request this module makes is a same-origin fetch for the build
 * revision, so no third-party tracking is involved.
 */

import { announce } from "./accessibility.js";

const GITHUB_REPO = "D-sorganization/AffineDrift";
const FALLBACK_EMAIL = "dieterolson@gmail.com";
const MANIFEST_URL = "/public-site-manifest.json";
const UNKNOWN_REVISION = "unknown";

function buildIssueBody(pageUrl, revision) {
    return [
        "## Page Context (auto-filled)",
        `- Page URL: ${pageUrl}`,
        `- Revision: ${revision}`,
        "",
        "## What is wrong",
        "**Quote the exact text and equation**:",
        "(Please quote the claim exactly as written)",
        "",
        "**Location**:",
        "- File and line number (`file:line`):",
        "- Is this in the LaTeX (`.tex`) tree, the Quarto (`.qmd`) tree, or both?",
        "",
        "## What it should say",
        "(Provide the corrected derivation, text, or equation here)",
        "",
        "## How did you verify this?",
        "**Method of verification**:",
        "(Did you run a script, recompute the matrix, or derive it by hand? " +
            "Please provide the steps or script to reproduce your finding)",
    ].join("\n");
}

function buildIssueUrl(pageUrl, revision) {
    const params = new URLSearchParams({
        template: "content-correction.md",
        title: "correction: ",
        labels: "content-correction,needs-verification",
        body: buildIssueBody(pageUrl, revision),
    });
    return `https://github.com/${GITHUB_REPO}/issues/new?${params.toString()}`;
}

function buildMailtoUrl(pageUrl, revision) {
    const subject = encodeURIComponent(`AffineDrift content correction: ${pageUrl}`);
    const body = encodeURIComponent(buildIssueBody(pageUrl, revision));
    return `mailto:${FALLBACK_EMAIL}?subject=${subject}&body=${body}`;
}

async function fetchRevision() {
    try {
        const response = await fetch(MANIFEST_URL, { credentials: "omit" });
        if (!response.ok) return UNKNOWN_REVISION;
        const data = await response.json();
        return data && typeof data.source_revision === "string" && data.source_revision
            ? data.source_revision
            : UNKNOWN_REVISION;
    } catch {
        return UNKNOWN_REVISION;
    }
}

function createVoteButton(vote, label) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "page-feedback__vote";
    button.dataset.vote = vote;
    button.setAttribute("aria-label", label);
    button.textContent = vote === "yes" ? "Yes" : "No";
    return button;
}

function attachVoteHandlers(prompt, yesButton, noButton) {
    const onVote = () => {
        prompt.textContent = "Thanks for the feedback!";
        yesButton.disabled = true;
        noButton.disabled = true;
        announce("Thanks for the feedback!");
    };
    yesButton.addEventListener("click", onVote);
    noButton.addEventListener("click", onVote);
}

function createHelpfulSection() {
    const section = document.createElement("div");
    section.className = "page-feedback__helpful";

    const prompt = document.createElement("span");
    prompt.className = "page-feedback__prompt";
    prompt.textContent = "Was this page helpful?";

    const yesButton = createVoteButton("yes", "Yes, this page was helpful");
    const noButton = createVoteButton("no", "No, this page was not helpful");
    attachVoteHandlers(prompt, yesButton, noButton);

    section.append(prompt, yesButton, noButton);
    return section;
}

function createReportSection(pageUrl) {
    const section = document.createElement("div");
    section.className = "page-feedback__report";

    const reportLink = document.createElement("a");
    reportLink.className = "page-feedback__report-link site-button site-button--ghost";
    reportLink.href = buildIssueUrl(pageUrl, UNKNOWN_REVISION);
    reportLink.target = "_blank";
    reportLink.rel = "noopener";
    reportLink.textContent = "Report a problem";

    const emailLink = document.createElement("a");
    emailLink.className = "page-feedback__email-link";
    emailLink.href = buildMailtoUrl(pageUrl, UNKNOWN_REVISION);
    emailLink.textContent = "No GitHub account? Email us instead";

    section.append(reportLink, emailLink);
    return section;
}

/**
 * Initialize the per-page "Was this helpful? / Report a problem" control.
 */
export function initPageFeedback() {
    const container = document.getElementById("quarto-document-content");
    if (!container) return;
    if (container.querySelector(".page-feedback")) return;

    const pageUrl = window.location.href;
    const widget = document.createElement("section");
    widget.className = "page-feedback";
    widget.setAttribute("aria-label", "Page feedback");
    widget.append(createHelpfulSection(), createReportSection(pageUrl));
    container.appendChild(widget);

    fetchRevision().then((revision) => {
        const reportLink = widget.querySelector(".page-feedback__report-link");
        const emailLink = widget.querySelector(".page-feedback__email-link");
        reportLink.href = buildIssueUrl(pageUrl, revision);
        emailLink.href = buildMailtoUrl(pageUrl, revision);
    });
}
