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
        button.innerHTML = copyIcon;
        button.title = "Copy email address";

        button.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();

            navigator.clipboard
                .writeText(email)
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

/**
 * Initialize responsive table wrappers
 */
export function initResponsiveTables() {
    const tables = document.querySelectorAll("#quarto-document-content table");
    const tableUsedIds = new Set();

    tables.forEach((table) => {
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
    });
}

/**
 * Initialize copy to clipboard for code blocks
 */
export function initCodeCopy() {
    // ⚡ Bolt Optimization: Use getElementsByTagName (O(1) live collection) instead of querySelectorAll (O(N))
    const codeBlocks = document.getElementsByTagName("pre");

    // Convert to Array to avoid issues with live collections when mutating DOM
    Array.from(codeBlocks).forEach((pre) => {
        if (pre.parentNode.classList.contains("code-wrapper")) return;
        if (!pre.textContent.trim()) return;

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
        button.dataset.action = "copy-code";

        wrapper.appendChild(button);
    });

    document.addEventListener("click", async (e) => {
        const button = e.target.closest('button[data-action="copy-code"]');
        if (!button) return;

        if (!button.classList.contains("copy-btn")) return;

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

    function adjustHeight(el) {
        el.style.height = "auto";
        const newHeight = Math.min(el.scrollHeight, 500);
        el.style.height = newHeight + "px";
        el.style.overflowY = newHeight >= 500 ? "auto" : "hidden";
    }

    for (const textarea of textareas) {
        textarea.style.resize = "none";
        setTimeout(() => adjustHeight(textarea), 0);
        textarea.addEventListener("input", () => adjustHeight(textarea));
    }

    window.addEventListener(
        "resize",
        debounce(() => {
            for (const textarea of textareas) {
                adjustHeight(textarea);
            }
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

            if (!button.dataset.originalHtml) {
                button.dataset.originalHtml = button.innerHTML;
            }

            button.innerHTML = "Opening Email Client...";
            button.classList.add("success");
            button.disabled = true;

            setTimeout(() => {
                button.innerHTML = button.dataset.originalHtml;
                button.classList.remove("success");
                button.disabled = false;
            }, 3000);
        });
    }
}
