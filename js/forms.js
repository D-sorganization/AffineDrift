/**
 * AffineDrift - Forms and Clipboard Module
 * Handles form interactions, copy functionality, and email copy
 */

import { debounce, generateUniqueId, runWhenIdle } from "./utils.js";

/**
 * Initialize copy email functionality for mailto links
 */
export function initEmailCopy() {
    const links = document.links;
    if (links.length === 0) return;

    const copyIcon =
        '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>';
    const checkIcon =
        '<svg viewBox="0 0 24 24" aria-hidden="true"><polyline points="20 6 9 17 4 12"></polyline></svg>';

    for (const link of links) {
        if (link.protocol !== "mailto:") continue;

        if (
            link.nextElementSibling &&
            link.nextElementSibling.classList.contains("copy-email-btn")
        )
            continue;

        const href = link.getAttribute("href");
        const email = href.replace(/^mailto:/, "").split("?")[0];
        if (!email) continue;

        const button = document.createElement("button");
        button.className = "copy-email-btn";
        button.setAttribute("aria-label", "Copy email address");
        button.setAttribute("type", "button");
        button.title = "Copy email address";

        function setCopyIcon() {
            button.textContent = "";
            const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
            svg.setAttribute("viewBox", "0 0 24 24"); svg.setAttribute("fill", "none");
            svg.setAttribute("stroke", "currentColor"); svg.setAttribute("stroke-width", "2");
            svg.setAttribute("stroke-linecap", "round"); svg.setAttribute("stroke-linejoin", "round");
            svg.setAttribute("aria-hidden", "true");
            const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
            rect.setAttribute("x", "9"); rect.setAttribute("y", "9"); rect.setAttribute("width", "13"); rect.setAttribute("height", "13"); rect.setAttribute("rx", "2"); rect.setAttribute("ry", "2");
            const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
            path.setAttribute("d", "M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1");
            svg.append(rect, path);
            button.appendChild(svg);
        }

        function setCheckIcon() {
            button.textContent = "";
            const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
            svg.setAttribute("viewBox", "0 0 24 24"); svg.setAttribute("fill", "none");
            svg.setAttribute("stroke", "currentColor"); svg.setAttribute("stroke-width", "2");
            svg.setAttribute("stroke-linecap", "round"); svg.setAttribute("stroke-linejoin", "round");
            svg.setAttribute("aria-hidden", "true");
            const polyline = document.createElementNS("http://www.w3.org/2000/svg", "polyline");
            polyline.setAttribute("points", "20 6 9 17 4 12");
            svg.appendChild(polyline);
            button.appendChild(svg);
        }

        setCopyIcon();

        button.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();

            navigator.clipboard
                .writeText(email)
                .then(() => {
                    setCheckIcon();
                    button.classList.add("success");
                    button.setAttribute("aria-label", "Email copied");

                    setTimeout(() => {
                        setCopyIcon();
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

/**
 * Initialize responsive table wrappers
 */
export function initResponsiveTables() {
    const container = document.getElementById("quarto-document-content");
    if (!container) return;

    // ⚡ Bolt Optimization: Scope tag lookup to specific container instead of global querySelectorAll (O(N))
    const tables = container.getElementsByTagName("table");
    const tableUsedIds = new Set();

    // ⚡ Bolt Optimization: Batch DOM reads (getComputedStyle) and writes (insertBefore/appendChild) separately to eliminate forced synchronous layout (Layout Thrashing)
    const tablesToWrap = [];

    // Phase 1: Read Layout
    for (const table of Array.from(tables)) {
        const parent = table.parentElement;
        if (
            parent.classList.contains("table-wrapper") ||
            parent.style.overflowX === "auto" ||
            window.getComputedStyle(parent).overflowX === "auto"
        ) {
            continue;
        }
        tablesToWrap.push(table);
    }

    // Phase 2: Mutate DOM
    for (const table of tablesToWrap) {
        const wrapper = document.createElement("div");
        wrapper.className = "table-wrapper";
        wrapper.setAttribute("tabindex", "0");
        wrapper.setAttribute("role", "region");

        const caption = table.getElementsByTagName("caption")[0];
        if (caption) {
            if (!caption.id) {
                caption.id = generateUniqueId(
                    caption.textContent || "table",
                    tableUsedIds
                );
            }
            tableUsedIds.add(caption.id);
            wrapper.setAttribute("aria-labelledby", caption.id);
        } else {
            wrapper.setAttribute("aria-label", "Table content");
        }

        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
    }
}

/**
 * Initialize copy to clipboard for code blocks
 */
export function initCodeCopy() {
    // ⚡ Bolt Optimization: Use getElementsByTagName (O(1) live collection) instead of querySelectorAll (O(N))
    const codeBlocks = document.getElementsByTagName("pre");

    // Convert to Array to avoid issues with live collections when mutating DOM
    for (const pre of Array.from(codeBlocks)) {
        if (pre.parentNode.classList.contains("code-wrapper")) continue;
        if (!pre.textContent.trim()) continue;

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
                button.setAttribute("title", "Copy code to clipboard");
        button.type = "button";
        button.dataset.action = "copy-code";

        wrapper.appendChild(button);
    }

    document.addEventListener("click", async (e) => {
        const button = e.target.closest('button[data-action="copy-code"]');
        if (!button) return;

        if (!button.classList.contains("copy-btn")) return;

        const wrapper = button.closest(".code-wrapper");
        if (!wrapper) return;

        // ⚡ Bolt Optimization: Replace descendant querySelector with native getElementsByTagName lookup for O(1) evaluation without CSS parsing overhead in interactive path
        const pre = wrapper.getElementsByTagName("pre")[0];
        if (!pre) return;

        try {
            await navigator.clipboard.writeText(pre.innerText || pre.textContent);
            button.textContent = "Copied!";
            button.setAttribute("aria-label", "Code copied to clipboard");
            button.setAttribute("title", "Code copied to clipboard");
            button.classList.add("copied");
            setTimeout(() => {
                button.textContent = "Copy";
                button.setAttribute("aria-label", "Copy code to clipboard");
                button.setAttribute("title", "Copy code to clipboard");
                button.classList.remove("copied");
            }, 2000);
        } catch (err) {
            console.error("Failed to copy:", err);
            button.textContent = "Error";
            setTimeout(() => (button.textContent = "Copy"), 2000);
        }
    });
}

/**
 * Initialize form accessibility features
 */
export function initFormAccessibility() {
    // ⚡ Bolt Optimization: Use getElementsByTagName and input.labels instead of querySelectorAll for O(1) live collection iteration and label access
    const processInput = (input) => {
        if (!input.required) return;

        let label = null;
        if (input.labels && input.labels.length > 0) {
            label = input.labels[0];
        } else if (input.id) {
            label = document.querySelector(`label[for="${input.id}"]`);
        }

        if (label && !label.getElementsByClassName("required-indicator")[0]) {
            const indicator = document.createElement("span");
            indicator.className = "required-indicator";
            indicator.textContent = " *";
            indicator.style.color = "var(--accent-blue)";
            indicator.style.fontWeight = "bold";
            indicator.setAttribute("aria-hidden", "true");
            indicator.title = "Required field";
            label.appendChild(indicator);
        }
    };

    for (const input of document.getElementsByTagName("input")) processInput(input);
    for (const textarea of document.getElementsByTagName("textarea")) processInput(textarea);
    for (const select of document.getElementsByTagName("select")) processInput(select);
}

/**
 * Initialize auto-growing textareas
 */
export function initAutoGrowTextareas() {
    // ⚡ Bolt Optimization: Use getElementsByTagName (O(1) live collection) instead of querySelectorAll (O(N))
    const textareas = document.getElementsByTagName("textarea");
    if (textareas.length === 0) return;

    // ⚡ Bolt Optimization: Batch DOM reads and writes to avoid forced synchronous layout (Layout Thrashing)
    function batchAdjustHeights() {
        const heights = [];

        // Phase 1: Write (reset heights to compute scrollHeight accurately)
        for (const textarea of textareas) {
            textarea.style.height = "auto";
        }

        // Phase 2: Read (get scrollHeights)
        for (let i = 0; i < textareas.length; i++) {
            heights.push(Math.min(textareas[i].scrollHeight, 500));
        }

        // Phase 3: Write (apply new heights and overflows)
        for (let i = 0; i < textareas.length; i++) {
            textareas[i].style.height = heights[i] + "px";
            textareas[i].style.overflowY = heights[i] >= 500 ? "auto" : "hidden";
        }
    }

    // Initialize all textareas statically
    for (const textarea of textareas) {
        textarea.style.resize = "none";
        textarea.style.overflow = "hidden";
        // Handle individual input events (single element adjust doesn't cause O(N) thrashing loop, but batching is safe)
        textarea.addEventListener("input", () => {
            textarea.style.height = "auto";
            const newHeight = Math.min(textarea.scrollHeight, 500);
            textarea.style.height = newHeight + "px";
            textarea.style.overflowY = newHeight >= 500 ? "auto" : "hidden";
        });
    }

    setTimeout(() => batchAdjustHeights(), 0);

    window.addEventListener(
        "resize",
        debounce(() => {
            batchAdjustHeights();
        }, 250)
    );
}

/**
 * Initialize contact form feedback
 */
export function initContactFormFeedback() {
    for (const form of document.forms) {
        if (!form.action || !form.action.startsWith("mailto:")) continue;

        form.addEventListener("submit", (e) => {
            const button = form.querySelector('button[type="submit"]');
            if (!button) return;

            if (!button.dataset.originalText) {
                // To avoid XSS, we store original textContent and assume this is a simple text button
                button.dataset.originalText = button.textContent;
            }

            button.textContent = "";

            const spinner = document.createElementNS("http://www.w3.org/2000/svg", "svg");
            spinner.setAttribute("width", "16");
            spinner.setAttribute("height", "16");
            spinner.setAttribute("viewBox", "0 0 24 24");
            spinner.setAttribute("fill", "none");
            spinner.setAttribute("stroke", "currentColor");
            spinner.setAttribute("stroke-width", "2");
            spinner.setAttribute("stroke-linecap", "round");
            spinner.setAttribute("stroke-linejoin", "round");
            spinner.setAttribute("aria-hidden", "true");
            spinner.style.marginRight = "8px";
            spinner.style.verticalAlign = "text-bottom";

            const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            circle.setAttribute("cx", "12");
            circle.setAttribute("cy", "12");
            circle.setAttribute("r", "10");
            circle.setAttribute("stroke-opacity", "0.25");
            spinner.appendChild(circle);

            const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
            path.setAttribute("d", "M12 2a10 10 0 0 1 10 10");

            const animate = document.createElementNS("http://www.w3.org/2000/svg", "animateTransform");
            animate.setAttribute("attributeName", "transform");
            animate.setAttribute("type", "rotate");
            animate.setAttribute("from", "0 12 12");
            animate.setAttribute("to", "360 12 12");
            animate.setAttribute("dur", "1s");
            animate.setAttribute("repeatCount", "indefinite");
            path.appendChild(animate);

            spinner.appendChild(path);

            button.appendChild(spinner);
            button.appendChild(document.createTextNode("Opening Email Client..."));
            button.classList.add("success");
            button.disabled = true;

            setTimeout(() => {
                button.textContent = button.dataset.originalText;
                button.classList.remove("success");
                button.disabled = false;
            }, 3000);
        });
    }
}
