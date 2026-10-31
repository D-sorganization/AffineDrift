(() => {
  "use strict";

  const libraryFiles = [
    "autocomplete.umd.js",
    "fuse.min.js",
    "quarto-search.js",
  ];
  const searchRoot = document.querySelector("#quarto-search");
  if (!searchRoot) return;

  let fallbackTrigger;
  if (!searchRoot.querySelector(".aa-DetachedSearchButton")) {
    const trigger = document.createElement("button");
    trigger.type = "button";
    trigger.className = "aa-DetachedSearchButton";
    trigger.setAttribute("aria-label", "Search");
    trigger.setAttribute("aria-haspopup", "dialog");
    trigger.title = "Search";
    trigger.textContent = "Search";
    fallbackTrigger = trigger;
    searchRoot.appendChild(trigger);
  }

  const offset = document.querySelector('meta[name="quarto:offset"]')?.content || "";
  const base = offset.endsWith("/") ? offset : `${offset}/`;
  let loading;
  let ready = false;
  let returnFocusTo;
  let wasDetached = false;

  function getSearchTrigger() {
    return Array.from(searchRoot.querySelectorAll(".aa-DetachedSearchButton"))
      .find((trigger) => trigger !== fallbackTrigger) || fallbackTrigger;
  }

  function removeFallbackTrigger() {
    const trigger = getSearchTrigger();
    if (trigger && trigger !== fallbackTrigger) {
      fallbackTrigger?.remove();
      fallbackTrigger = undefined;
    }
    return trigger;
  }

  function loadScript(file) {
    return new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = `${base}site_libs/quarto-search/${file}`;
      script.async = false;
      script.dataset.lazySearchAsset = file;
      script.addEventListener("load", resolve, { once: true });
      script.addEventListener(
        "error",
        () => reject(new Error(`Unable to load search asset: ${file}`)),
        { once: true },
      );
      document.head.appendChild(script);
    });
  }

  function loadQuartoSearchAfterDomReady() {
    if (document.readyState === "loading") return loadScript("quarto-search.js");

    const addEventListener = document.addEventListener;
    document.addEventListener = function (type, listener, options) {
      if (type === "DOMContentLoaded") {
        queueMicrotask(() => {
          const event = new Event("DOMContentLoaded");
          if (typeof listener === "function") listener.call(document, event);
          else listener.handleEvent(event);
        });
        return undefined;
      }
      return addEventListener.call(this, type, listener, options);
    };

    return loadScript("quarto-search.js").finally(() => {
      document.addEventListener = addEventListener;
    });
  }

  function loadSearch() {
    if (ready) return Promise.resolve();
    if (!loading) {
      loading = (async () => {
        await loadScript(libraryFiles[0]);
        await loadScript(libraryFiles[1]);
        await loadQuartoSearchAfterDomReady();
        ready = true;
      })().catch((error) => {
        loading = undefined;
        console.error(error);
        throw error;
      });
    }
    return loading;
  }

  function isFormTarget(target) {
    return target instanceof Element && Boolean(
      target.closest("input, select, textarea, button, option, [contenteditable=true]"),
    );
  }

  document.addEventListener("click", (event) => {
    const trigger = event.target instanceof Element
      ? event.target.closest("#quarto-search .aa-DetachedSearchButton")
      : null;
    if (!trigger) return;
    returnFocusTo = trigger;
    if (ready) return;

    event.preventDefault();
    event.stopImmediatePropagation();
    loadSearch().then(() => {
      returnFocusTo = removeFallbackTrigger() || trigger;
      window.quartoOpenSearch();
    });
  }, true);

  document.addEventListener("keyup", (event) => {
    if (isFormTarget(event.target)) return;
    const optionElement = document.querySelector("#quarto-search-options");
    if (!optionElement) return;

    let shortcuts = [];
    try {
      shortcuts = JSON.parse(optionElement.textContent || "{}")["keyboard-shortcut"] || [];
    } catch (_error) {
      return;
    }
    if (!shortcuts.includes(event.key)) return;

    returnFocusTo = getSearchTrigger();
    if (ready) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    loadSearch().then(() => {
      returnFocusTo = removeFallbackTrigger() || returnFocusTo;
      window.quartoOpenSearch();
    });
  }, true);

  const observer = new MutationObserver(() => {
    const isDetached = document.body?.classList.contains("aa-Detached") || false;
    if (isDetached) {
      const form = document.querySelector(".aa-DetachedFormContainer");
      if (form) {
        document.documentElement.style.setProperty(
          "--ad-search-input-height",
          `${Math.ceil(form.getBoundingClientRect().height)}px`,
        );
      }
    } else if (wasDetached && returnFocusTo?.isConnected) {
      const target = returnFocusTo;
      window.requestAnimationFrame(() => target.focus({ preventScroll: true }));
      returnFocusTo = undefined;
    }
    wasDetached = isDetached;
  });
  if (document.documentElement) {
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["class"],
      subtree: true,
    });
  }

  const loadSharedQuery = () => {
    const params = new URL(window.location.href).searchParams;
    if (params.has("q") || params.has("show-results")) loadSearch();
  };
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", loadSharedQuery, { once: true });
  } else {
    loadSharedQuery();
  }
})();
