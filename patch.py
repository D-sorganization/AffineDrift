import sys

with open("js/forms.js", "r") as f:
    content = f.read()

old_code = """export function initAutoGrowTextareas() {
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
        textarea.style.overflow = "hidden";
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
}"""

new_code = """export function initAutoGrowTextareas() {
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
}"""

if old_code in content:
    content = content.replace(old_code, new_code)
    with open("js/forms.js", "w") as f:
        f.write(content)
    print("Patched successfully")
else:
    print("Failed to patch")
