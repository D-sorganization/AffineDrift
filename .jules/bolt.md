## 2024-05-23 - Property Access vs Constructor Overhead
**Learning:** In hot loops or large DOM queries (like iterating hundreds of links), accessing `link.hostname` is significantly faster than `new URL(link.href)`.
**Action:** When working with anchor elements, always prefer `HTMLHyperlinkElementUtils` properties (`hostname`, `pathname`, etc.) over creating new `URL` objects.

## 2024-05-24 - String.split() Memory Overhead
**Learning:** `String.prototype.split` allocates an array of new strings, which is O(N) memory. For large texts (like articles), this creates unnecessary GC pressure just to count items.
**Action:** Use a manual character loop or iterator for counting logic to maintain O(1) memory usage.

## 2025-02-18 - Live Collections vs QuerySelector
**Learning:** `document.images` and `document.links` provide O(1) access to live HTMLCollections, avoiding the overhead of `querySelectorAll` (O(N) traversal) for global element iteration.
**Action:** Use native collections for global iterators (images, links, forms) instead of selectors when possible.

## 2025-10-26 - MathJax Lazy Typesetting
**Learning:** For long technical articles with hundreds of equations, default MathJax typesetting blocks the main thread. The `ui/lazy` extension significantly improves TTI by only typesetting equations in the viewport.
**Action:** Always enable `ui/lazy` in MathJax v3 configuration for content-heavy pages.

## 2025-10-27 - Streamlit Matplotlib Caching
**Learning:** Matplotlib figure generation is a significant bottleneck in interactive Streamlit apps. Re-creating `Figure` objects on every script rerun causes noticeable lag.
**Action:** Use `@st.cache_resource` (with `max_entries` limit) to cache functions that return Matplotlib `Figure` objects. This keeps the live figure object in memory and avoids expensive reconstruction, dramatically improving responsiveness.

## 2025-02-19 - QuerySelectorAttribute vs Live Collection Iteration
**Learning:** Selecting elements with specific attributes via `document.querySelectorAll('img[loading="lazy"]')` requires a full DOM scan and parsing of the selector. It's often faster to iterate over a live collection like `document.images` and check the attribute manually (`img.getAttribute("loading") === "lazy"`).
**Action:** When searching for global elements like forms, images, or links that also require specific attributes, iterate over the built-in HTMLCollections and do manual filtering instead of relying on complex `querySelectorAll` selectors.

## 2025-02-19 - QuerySelector vs Live Collection Iteration for Tags
**Learning:** `document.querySelectorAll("tag")` requires a full DOM scan and parsing of the selector. It's often faster to iterate over a live collection like `document.getElementsByTagName("tag")` which is O(1) time complexity.
**Action:** When searching for global elements like standard tags (`nav`, `aside`, `main`, `textarea`, `pre`, `section`), always prefer `document.getElementsByTagName` over `document.querySelectorAll` combined with a `for...of` loop.

## 2025-10-28 - DOMTokenList vs String Manipulation
**Learning:** Manually manipulating space-separated attributes (like `rel` or `class`) using `.split(" ")` and `.join(" ")` in loops creates unnecessary arrays and string copies, causing garbage collection overhead. Using `.split("/").pop()` on URLs is similarly wasteful compared to `substring()`.
**Action:** Always use native `DOMTokenList` APIs (like `element.classList` or `element.relList`) to add, remove, or toggle tokens directly without JS memory allocation. Use `substring(lastIndexOf("/"))` for simple path extractions.

## 2025-02-19 - Safe DOM Iteration with Live Collections
**Learning:** When iterating over live HTMLCollections (e.g., `document.getElementsByTagName()`) to optimize DOM queries, changing attributes like `aria-label` is generally safe as it doesn't mutate the DOM structure or the collection itself (unlike wrapping elements or changing classes used in `getElementsByClassName`). Reusing collections for subsequent loops is also highly efficient.
**Action:** When migrating from `querySelectorAll` to live collections, evaluate whether the loop body alters the criteria of the collection. If it only modifies independent attributes, it is perfectly safe to iterate directly using `for...of` without `Array.from()`.

## 2025-02-21 - QuerySelector with Complex CSS on Links vs Live Collection Iteration
**Learning:** Complex CSS selectors on links like `document.querySelectorAll('.navbar-nav a.nav-link[href^="#"]')` or `document.querySelectorAll('.navbar-nav a[href^="https://github.com"]')` can be extremely slow on large pages. Iterating over `document.links` and checking `href` and `classList` is much faster.
**Action:** Replace `querySelectorAll` with iteration over `document.links` for operations that search for links with specific attributes or classes.

## 2025-02-19 - QuerySelector Descendant Check vs HTMLCollection
**Learning:** Checking for specific descendants (like images or SVGs inside a link) using `element.querySelector("img, svg")` requires parsing a CSS selector and traversing the subtree. Using `element.getElementsByTagName("img").length` is significantly faster as it utilizes live, cached collections.
**Action:** When replacing expensive CSS selectors within descendant checks, prefer direct tag lookups using `getElementsByTagName()` and evaluating the `.length` property to avoid the overhead of parsing CSS selectors for every iterated element.

## 2024-05-25 - Live Collections for ARIA Initialization
**Learning:** Initializing ARIA labels globally using `querySelectorAll` causes excessive layout thrashing and CSS parsing overhead. Using live HTMLCollections (`getElementsByTagName` and `getElementsByClassName`) and manually checking properties is significantly faster.
**Action:** When applying attributes like ARIA labels globally across elements (e.g., inputs, lists, cards), retrieve elements via `getElementsByTagName` or `getElementsByClassName` and use `for...of` loops, manually filtering attributes rather than relying on complex `querySelectorAll` selectors.

## 2026-04-03 - Pre-computing Strings for Frontend Search
**Learning:** Calculating `.toLowerCase()` and `.join()` inside a search loop runs on every keystroke, causing O(N*M) string allocations. This creates massive GC pressure.
**Action:** Pre-compute and cache expensive string operations (like lowercasing and joining arrays) on the data objects at load time, rather than calling them dynamically during the search filter function.

## 2024-05-26 - DOM Creation vs Regex String Replacement for Escaping
**Learning:** Using `document.createElement("div")` to escape HTML strings incurs significant memory allocation and layout thrashing, especially in hot loops generating large lists. This is incredibly slow compared to native string operations.
**Action:** When escaping HTML in JavaScript, especially in loops, use regular expression string replacements (e.g., `.replace(/&/g, "&amp;")`) instead of creating dummy DOM elements to avoid layout thrashing and severe memory allocation overhead.

## 2024-05-27 - Input Labels O(1) Property
**Learning:** Using `document.querySelector('label[for="..."]')` to find a label for an input is an O(N) operation that requires parsing a CSS selector and traversing the DOM. However, standard inputs have an O(1) built-in property `input.labels` that returns a `NodeList` of associated labels (both explicit via `for` and implicit via wrapping).
**Action:** When finding the `<label>` associated with an `<input>` element, always use the `input.labels` property instead of querying the DOM.

## 2024-05-28 - Global Input Iteration Fallbacks
**Learning:** While iterating over `document.forms` and `form.elements` seems like a clean way to find all inputs without `querySelectorAll`, it ignores standalone inputs that are not wrapped in a `<form>` tag.
**Action:** When optimizing global DOM queries for form inputs, prefer iterating over live collections like `document.getElementsByTagName('input')`, `textarea`, and `select` rather than nested `document.forms` loops to ensure no elements are missed.

## 2026-04-07 - Layout Thrashing in DOM Initialization
**Learning:** Interleaving layout reads (like `getComputedStyle`) and DOM mutations (`insertBefore`, `appendChild`) inside a loop causes forced synchronous layout (Layout Thrashing), severely impacting the main thread during initialization.
**Action:** When iterating over elements that require layout checks before DOM modification, always batch the reads into a separate array or phase before performing the writes.

## 2025-02-19 - Replace forEach with for...of loops
**Learning:** In modern JS engines (V8/SpiderMonkey), `for...of` loops execute significantly faster than `.forEach()` for array/iterable traversals because they avoid the overhead of function calls and lexical scope creation on every iteration.
**Action:** Use `for...of` instead of `.forEach` for high-iteration code or critical start-up paths.

## 2025-02-19 - Safe Refactoring to for...of loops
**Learning:** When refactoring `forEach` loops to `for...of`, `continue` statements should be used to simulate returning from the `forEach` callback. `return` in a `for...of` loop will prematurely exit the entire enclosing function.
**Action:** Pay close attention to early exits when refactoring to `for...of` loops and change them from `return` to `continue`.
## 2026-05-18 - Replacing querySelectorAll with getElementsByClassName
**Learning:** `querySelectorAll` parses a CSS selector string and returns a static `NodeList`, which takes O(N) where N is the number of all nodes scanned. `getElementsByClassName` returns a live `HTMLCollection` and is highly optimized in browsers for simple class lookups (taking effectively O(1) time to create the collection). When iterating over elements that don't add or remove the queried classes (which avoids infinite loops with live collections), `getElementsByClassName` provides a measureable performance improvement for global DOM lookups.
**Action:** When finding multiple elements solely by their class name and subsequently iterating over them without modifying their class attributes, always prefer `document.getElementsByClassName("class-name")` over `document.querySelectorAll(".class-name")`.

## 2026-04-27 - Synchronizing modular code optimizations
**Learning:** Performance optimizations applied to modular codebase files might exist in duplicate forms inside monolithic files like `script.js`.
**Action:** When working on modular optimizations or after observing them in memory, always `grep` through older monolithic entry points to ensure identical logic was not overlooked.

## 2026-05-04 - QuerySelector Attribute Selector vs Live Collection Filtering
**Learning:** `document.querySelectorAll('[id$="-history-list"]')` performs a full DOM scan and parses a complex attribute substring selector which is notoriously slow in V8 when DOM nodes are plentiful. Using `document.getElementsByTagName('ul')` returns an O(1) live collection almost instantly, and manually checking `.endsWith("-history-list")` avoids the CSS engine overhead entirely.
**Action:** Replace `querySelectorAll` with attribute suffix matching (`[id$="..."]`) by fetching the tags via `getElementsByTagName` and manually performing JavaScript string filtering like `element.id.endsWith("...")`.

## 2026-05-06 - querySelectorAll with :not() vs getElementsByTagName
**Learning:** Complex CSS selectors using `:not()` pseudo-classes (e.g., `querySelectorAll("section:not(.page-header):not(.article-section)")`) require the browser's CSS selector engine to perform a full DOM scan and evaluate multiple rule exclusions on every node. Retrieving all sections via the O(1) live collection `getElementsByTagName("section")` and filtering excluded classes directly in JavaScript using `element.classList.contains` is significantly faster, reducing initialization overhead and main-thread blocking.
**Action:** When filtering out elements based on classes while querying by tag, prefer using `getElementsByTagName` combined with manual JavaScript `classList` filtering over complex `:not()` CSS selectors.

## 2026-05-08 - Fast Heading Lookups
**Learning:** Replaced querySelectorAll('.main-content-area h2, h3') with targeted getElementsByTagName to avoid scanning the entire DOM for anchor links.
**Action:** Use getElementsByTagName combined with array spreading for high-performance localized queries.

## 2026-05-18 - Replacing Multi-Selector querySelectorAll with Live Collections
**Learning:** Using `querySelectorAll(".class, tag, #id")` forces the CSS engine to perform a full DOM traversal matching against a complex union of rules, which blocks the main thread during startup/layout initialization.
**Action:** When gathering known elements across multiple criteria (like `.main-content-area`, `.home-content`, and `#quarto-document-content`), fetch each set using native O(1) live collections (`getElementsByClassName`, `getElementsByTagName`, `getElementById`) and manually merge them into a single Array or Set in JavaScript instead.

## 2026-05-18 - Replacing Multi-Selector querySelectorAll with Live Collections for Tab Focus
**Learning:** Calling `querySelectorAll` with a complex union selector like `'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'` on every Tab key press creates immense overhead due to CSS parsing and full subtree traversal.
**Action:** Replace dynamic focusable element queries in keydown handlers with a manual iteration over the `getElementsByTagName('*')` live collection, checking for the `el.tabIndex >= 0` property to efficiently collect focusable elements.

## 2026-05-18 - QuerySelector Descendant Check vs HTMLCollection
**Learning:** Checking for specific descendants using `element.querySelector(".class")` or `element.querySelector("tag")` inside loops requires the browser's CSS selector engine to re-parse the string and traverse the subtree on every iteration, causing significant overhead during initialization.
**Action:** When replacing expensive CSS selectors within descendant checks, prefer direct lookups using `getElementsByTagName()[0]` or `getElementsByClassName()[0]` to avoid the overhead of parsing CSS selectors for every iterated element.

## 2026-05-20 - Replace Descendant querySelector with Native Lookup
**Learning:** Checking for a specific descendant node via `element.querySelector("tag")` inside highly interactive paths (like copy-to-clipboard clicks) invokes the browser's CSS selector engine, which is slower than native DOM lookups. Accessing index `[0]` on an `HTMLCollection` returned by `getElementsByTagName` performs an equivalent falsy evaluation (`undefined` instead of `null`) while avoiding CSS parsing overhead entirely.
**Action:** Safely replace simple descendant `querySelector` calls with `getElementsByTagName("tag")[0]` or `getElementsByClassName("class")[0]` to eliminate CSS parsing overhead in interactive DOM event handlers.

## 2024-05-19 - Single Scroll Listener
**Learning:** Found two separate `window.addEventListener("scroll", ...)` attachments on the main page (one for back-to-top progress, one for export-to-PDF button visibility), causing duplicate DOM reads and writes on every frame. Batching DOM mutations in a scroll event is crucial to avoid layout thrashing.
**Action:** Consolidate scroll-dependent logic into a single debounced/requestAnimationFrame scroll listener that batches all scroll-dependent UI updates, preventing layout thrashing and improving overall scrolling performance.
