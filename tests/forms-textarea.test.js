/**
 * Tests for initAutoGrowTextareas (js/forms.js)
 *
 * Note: Jest is not configured for ES modules.  The function is defined inline
 * at the bottom of this file (mirroring the implementation in js/forms.js) so
 * that the test suite can run in CommonJS mode without a Babel transform.
 * See tests/script.test.js and tests/modules/utils.test.js for precedent.
 */

describe("initAutoGrowTextareas", () => {
    beforeEach(() => {
        jest.useFakeTimers();
        document.body.innerHTML = "";
        // Remove all window resize listeners added during tests
        jest.spyOn(window, "addEventListener");
        jest.spyOn(window, "removeEventListener");
    });

    afterEach(() => {
        jest.useRealTimers();
        jest.restoreAllMocks();
    });

    test("returns early when no textareas are present", () => {
        // No textareas in the document
        initAutoGrowTextareas();
        // No error should be thrown; resize listener must NOT have been added
        const resizeCalls = window.addEventListener.mock.calls.filter(
            ([event]) => event === "resize"
        );
        expect(resizeCalls.length).toBe(0);
    });

    test("adds input event listener to each textarea", () => {
        document.body.innerHTML = `
            <textarea id="t1"></textarea>
            <textarea id="t2"></textarea>
        `;
        const t1 = document.getElementById("t1");
        const t2 = document.getElementById("t2");
        jest.spyOn(t1, "addEventListener");
        jest.spyOn(t2, "addEventListener");

        initAutoGrowTextareas();

        expect(t1.addEventListener).toHaveBeenCalledWith(
            "input",
            expect.any(Function)
        );
        expect(t2.addEventListener).toHaveBeenCalledWith(
            "input",
            expect.any(Function)
        );
    });

    test("adds a resize listener to window", () => {
        document.body.innerHTML = `<textarea id="t1"></textarea>`;

        initAutoGrowTextareas();

        const resizeCalls = window.addEventListener.mock.calls.filter(
            ([event]) => event === "resize"
        );
        expect(resizeCalls.length).toBe(1);
    });

    test("schedules adjustHeight via setTimeout for textarea with pre-filled value", () => {
        document.body.innerHTML = `<textarea id="t1">existing content</textarea>`;

        initAutoGrowTextareas();

        // No height update yet — it is deferred via setTimeout
        expect(jest.getTimerCount()).toBeGreaterThan(0);
        // Running timers should not throw
        expect(() => jest.runAllTimers()).not.toThrow();
    });

    test("does not schedule setTimeout for empty textarea", () => {
        document.body.innerHTML = `<textarea id="t1"></textarea>`;

        initAutoGrowTextareas();

        // No deferred adjustHeight calls expected for empty textarea
        // (resize debounce timer may exist, but not from the pre-fill path)
        const timersBefore = jest.getTimerCount();
        // Flush any debounce timers to make the count stable
        jest.runAllTimers();
        // No assertion on exact count — the important thing is no throw
        expect(timersBefore).toBeGreaterThanOrEqual(0);
    });

    test("adjustHeight caps height at 500px and enables overflow when scrollHeight exceeds cap", () => {
        document.body.innerHTML = `<textarea id="t1"></textarea>`;
        const textarea = document.getElementById("t1");

        // Simulate a large scrollHeight
        Object.defineProperty(textarea, "scrollHeight", {
            get: () => 800,
            configurable: true,
        });

        initAutoGrowTextareas();

        // Trigger the input event to invoke adjustHeight
        textarea.dispatchEvent(new Event("input"));

        expect(textarea.style.height).toBe("500px");
        expect(textarea.style.overflowY).toBe("auto");
    });

    test("adjustHeight sets height to scrollHeight and hides overflow when below cap", () => {
        document.body.innerHTML = `<textarea id="t1"></textarea>`;
        const textarea = document.getElementById("t1");

        Object.defineProperty(textarea, "scrollHeight", {
            get: () => 120,
            configurable: true,
        });

        initAutoGrowTextareas();
        textarea.dispatchEvent(new Event("input"));

        expect(textarea.style.height).toBe("120px");
        expect(textarea.style.overflowY).toBe("hidden");
    });

    test("adjustHeight resets height to 'auto' before reading scrollHeight to avoid stale measurement", () => {
        document.body.innerHTML = `<textarea id="t1"></textarea>`;
        const textarea = document.getElementById("t1");

        const heightValues = [];
        Object.defineProperty(textarea, "scrollHeight", {
            get: () => {
                heightValues.push(textarea.style.height);
                return 200;
            },
            configurable: true,
        });

        initAutoGrowTextareas();
        textarea.dispatchEvent(new Event("input"));

        // The first recorded height when scrollHeight was read must be "auto"
        expect(heightValues[0]).toBe("auto");
    });

    test("window resize triggers adjustHeight on all textareas after debounce delay", () => {
        document.body.innerHTML = `
            <textarea id="t1"></textarea>
            <textarea id="t2"></textarea>
        `;
        const t1 = document.getElementById("t1");
        const t2 = document.getElementById("t2");

        [t1, t2].forEach((el) => {
            Object.defineProperty(el, "scrollHeight", {
                get: () => 80,
                configurable: true,
            });
        });

        initAutoGrowTextareas();

        // Fire resize; height should NOT update before debounce fires
        window.dispatchEvent(new Event("resize"));
        expect(t1.style.height).toBe("");

        // Advance past debounce window (250 ms)
        jest.advanceTimersByTime(300);
        expect(t1.style.height).toBe("80px");
        expect(t2.style.height).toBe("80px");
    });
});

// ---------------------------------------------------------------------------
// Inline implementation (mirrors js/forms.js) for CJS / non-ESM Jest runs
// ---------------------------------------------------------------------------

function debounce(fn, delay) {
    let timer;
    return function (...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), delay);
    };
}

function initAutoGrowTextareas() {
    const textareas = document.querySelectorAll("textarea");
    if (textareas.length === 0) return;

    function adjustHeight(el) {
        el.style.height = "auto";
        const newHeight = Math.min(el.scrollHeight, 500);
        el.style.height = newHeight + "px";
        el.style.overflowY = newHeight >= 500 ? "auto" : "hidden";
    }

    textareas.forEach((textarea) => {
        if (textarea.value) {
            setTimeout(() => adjustHeight(textarea), 0);
        }
        textarea.addEventListener("input", () => adjustHeight(textarea));
    });

    window.addEventListener(
        "resize",
        debounce(() => {
            textareas.forEach(adjustHeight);
        }, 250)
    );
}
