(function () {
  "use strict";

  const STORAGE_KEYS = Object.freeze({
    active: "affinedrift_notes_workspace_v1",
    recycleBin: "affinedrift_notes_recycle_bin_v1",
  });
  const RECYCLE_BIN_RETENTION_MS = 30 * 24 * 60 * 60 * 1000;

  function nowIso() {
    return new Date().toISOString();
  }

  function safeParseJson(raw, fallback) {
    if (!raw) return fallback;
    try {
      return JSON.parse(raw);
    } catch (_error) {
      return fallback;
    }
  }

  function readJsonFromStorage(storage, key, fallback) {
    const raw = storage.getItem(key);
    if (!raw) return fallback;
    const parsed = safeParseJson(raw, null);
    if (parsed === null) {
      storage.removeItem(key);
      return fallback;
    }
    return parsed;
  }

  function isExpiredIsoTimestamp(timestamp, retentionMs) {
    if (typeof timestamp !== "string") return false;
    const parsed = Date.parse(timestamp);
    if (Number.isNaN(parsed)) return false;
    return Date.now() - parsed > retentionMs;
  }

  function debounce(fn, delayMs) {
    let timer = null;
    return function (...args) {
      clearTimeout(timer);
      timer = setTimeout(() => {
        timer = null;
        fn.apply(this, args);
      }, delayMs);
    };
  }

  class NotesWorkspaceStore {
    constructor(storage) {
      if (!storage || typeof storage.getItem !== "function" || typeof storage.setItem !== "function") {
        throw new Error("NotesWorkspaceStore requires a storage implementation");
      }
      this.storage = storage;
    }

    loadActive() {
      const parsed = readJsonFromStorage(this.storage, STORAGE_KEYS.active, null);
      if (!parsed || typeof parsed.content !== "string") {
        return { content: "", updatedAt: null };
      }
      return { content: parsed.content, updatedAt: parsed.updatedAt || null };
    }

    saveActive(content) {
      if (typeof content !== "string") {
        throw new Error("Notes content must be a string");
      }
      const payload = { content, updatedAt: nowIso() };
      this.storage.setItem(STORAGE_KEYS.active, JSON.stringify(payload));
      return payload;
    }

    clearActive() {
      this.storage.removeItem(STORAGE_KEYS.active);
    }

    loadRecycleBin() {
      const parsed = readJsonFromStorage(this.storage, STORAGE_KEYS.recycleBin, null);
      if (!parsed) {
        return { snapshots: [], content: "", deletedAt: null };
      }
      // Handle legacy single-object format
      const snapshots = Array.isArray(parsed) ? parsed : [parsed];
      // Prune expired entries
      const fresh = snapshots.filter(
        (s) => !isExpiredIsoTimestamp(s.deletedAt, RECYCLE_BIN_RETENTION_MS),
      );
      if (fresh.length !== snapshots.length) {
        if (fresh.length === 0) {
          this.storage.removeItem(STORAGE_KEYS.recycleBin);
          return { snapshots: [], content: "", deletedAt: null };
        }
        this.storage.setItem(STORAGE_KEYS.recycleBin, JSON.stringify(fresh));
      }
      const latest = fresh[fresh.length - 1];
      return { snapshots: fresh, content: latest.content, deletedAt: latest.deletedAt || null };
    }

    moveActiveToRecycleBin() {
      const active = this.loadActive();
      if (!active.content.trim()) return false;
      const newSnapshot = { content: active.content, deletedAt: nowIso() };
      // Read existing bin, normalise to array
      const existing = readJsonFromStorage(this.storage, STORAGE_KEYS.recycleBin, null);
      let snapshots = [];
      if (existing) {
        snapshots = Array.isArray(existing) ? existing : [existing];
      }
      snapshots.push(newSnapshot);
      // Prune old entries
      snapshots = snapshots.filter(
        (s) => !isExpiredIsoTimestamp(s.deletedAt, RECYCLE_BIN_RETENTION_MS),
      );
      this.storage.setItem(STORAGE_KEYS.recycleBin, JSON.stringify(snapshots));
      this.clearActive();
      return true;
    }

    restoreFromRecycleBin() {
      const bin = this.loadRecycleBin();
      if (!bin.content.trim()) return false;
      this.saveActive(bin.content);
      // Remove the last snapshot we just restored
      const remaining = bin.snapshots.slice(0, -1);
      if (remaining.length === 0) {
        this.storage.removeItem(STORAGE_KEYS.recycleBin);
      } else {
        this.storage.setItem(STORAGE_KEYS.recycleBin, JSON.stringify(remaining));
      }
      return true;
    }
  }

  function injectNotesStyles() {
    if (document.getElementById("ad-notes-workspace-style")) return;
    const style = document.createElement("style");
    style.id = "ad-notes-workspace-style";
    style.textContent = `
      .ad-notes-toggle {
        position: fixed; bottom: 1.25rem; left: 1.25rem; z-index: 1200;
        border: 1px solid #194870; border-radius: 999px; background: #0f4c75; color: #fff;
        padding: 0.65rem 0.95rem; font-size: 0.9rem; cursor: pointer;
      }
      .ad-notes-panel {
        position: fixed; left: 1.25rem; bottom: 4.5rem; width: min(92vw, 420px);
        background: var(--bg-primary, #fff); border: 1px solid var(--border-color, #d9e1e8); border-radius: 12px; box-shadow: 0 14px 30px rgba(15, 76, 117, 0.18);
        z-index: 1200; padding: 0.8rem; display: none;
      }
      .ad-notes-panel.open { display: block; }
      .ad-notes-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
      .ad-notes-header h3 { margin: 0; font-size: 1rem; color: #0f4c75; }
      .ad-notes-area {
        width: 100%; min-height: 210px; border: 1px solid var(--border-color, #d9e1e8); border-radius: 8px;
        padding: 0.65rem; font-size: 0.92rem; resize: vertical; line-height: 1.45;
        background: var(--bg-primary, #fff); color: var(--text-dark, #243746);
      }
      .ad-notes-actions { display: flex; flex-wrap: wrap; gap: 0.45rem; margin-top: 0.6rem; }
      .ad-notes-actions button {
        border: 1px solid var(--border-color, #d1dbe4); background: var(--bg-secondary, #f7fafc); color: var(--text-dark, #243746); border-radius: 6px;
        padding: 0.38rem 0.6rem; font-size: 0.82rem; cursor: pointer;
      }
      .ad-notes-actions .danger { border-color: #f0b9b9; background: #fff3f3; color: #8c2323; }
      .ad-notes-status { font-size: 0.78rem; color: var(--text-muted, #5e6d7a); margin-top: 0.45rem; min-height: 1.1rem; }
    `;
    document.head.appendChild(style);
  }

  function initNotesWorkspace(options = {}) {
    if (typeof window === "undefined" || typeof document === "undefined") return null;

    const store = options.store || new NotesWorkspaceStore(window.localStorage);
    if (document.getElementById("ad-notes-workspace-toggle")) {
      return { store };
    }

    injectNotesStyles();

    const toggleBtn = document.createElement("button");
    toggleBtn.id = "ad-notes-workspace-toggle";
    toggleBtn.className = "ad-notes-toggle";
    toggleBtn.type = "button";
    toggleBtn.setAttribute("aria-expanded", "false");
    toggleBtn.setAttribute("aria-controls", "ad-notes-workspace-panel");
    toggleBtn.setAttribute("aria-label", "Expand Project Notes");
    toggleBtn.setAttribute("title", "Expand Project Notes");
    toggleBtn.textContent = "Project Notes";

    const panel = document.createElement("section");
    panel.id = "ad-notes-workspace-panel";
    panel.className = "ad-notes-panel";
    panel.setAttribute("aria-label", "Project notes workspace");
    panel.setAttribute("aria-hidden", "true");
    panel.setAttribute("role", "dialog");
    panel.setAttribute("aria-modal", "true");
    const header = document.createElement("div");
    header.className = "ad-notes-header";
    const h3 = document.createElement("h3");
    h3.textContent = "Project Notes";
    const closeBtn = document.createElement("button");
    closeBtn.type = "button";
    closeBtn.dataset.action = "close";
    closeBtn.setAttribute("aria-label", "Close notes workspace");
    closeBtn.title = "Close notes workspace";
    closeBtn.textContent = "x";
    header.appendChild(h3);
    header.appendChild(closeBtn);

    const textarea = document.createElement("textarea");
    textarea.id = "ad-notes-workspace-area";
    textarea.className = "ad-notes-area";
    textarea.placeholder = "Capture research notes, ideas, and follow-ups...";

    const actions = document.createElement("div");
    actions.className = "ad-notes-actions";

    const btnSave = document.createElement("button");
    btnSave.type = "button"; btnSave.dataset.action = "save"; btnSave.title = "Save notes"; btnSave.textContent = "Save";

    const btnClear = document.createElement("button");
    btnClear.type = "button"; btnClear.dataset.action = "clear"; btnClear.title = "Clear notes"; btnClear.textContent = "Clear";

    const btnDelete = document.createElement("button");
    btnDelete.type = "button"; btnDelete.dataset.action = "delete"; btnDelete.className = "danger"; btnDelete.title = "Delete notes to bin"; btnDelete.textContent = "Delete to Bin";

    const btnRestore = document.createElement("button");
    btnRestore.type = "button"; btnRestore.dataset.action = "restore"; btnRestore.title = "Restore notes from bin"; btnRestore.textContent = "Restore Bin";

    const btnPopout = document.createElement("button");
    btnPopout.type = "button"; btnPopout.dataset.action = "popout"; btnPopout.title = "Open notes in new window"; btnPopout.textContent = "Pop-out";

    actions.append(btnSave, btnClear, btnDelete, btnRestore, btnPopout);

    const statusDiv = document.createElement("div");
    statusDiv.className = "ad-notes-status";
    statusDiv.id = "ad-notes-status";
    statusDiv.setAttribute("aria-live", "polite");
    statusDiv.setAttribute("aria-atomic", "true");

    panel.append(header, textarea, actions, statusDiv);

    document.body.appendChild(toggleBtn);
    document.body.appendChild(panel);

    const textArea = panel.querySelector("#ad-notes-workspace-area");
    const status = panel.querySelector("#ad-notes-status");

    function setStatus(message) {
      status.textContent = message;
    }

    function loadIntoTextArea() {
      const active = store.loadActive();
      textArea.value = active.content;
      if (active.updatedAt) {
        setStatus(`Loaded saved notes (${active.updatedAt})`);
      } else {
        setStatus("No saved notes yet.");
      }
    }

    function openPanel() {
      panel.classList.add("open");
      toggleBtn.setAttribute("aria-expanded", "true");
      toggleBtn.setAttribute("aria-label", "Collapse Project Notes");
      toggleBtn.setAttribute("title", "Collapse Project Notes");
      panel.setAttribute("aria-hidden", "false");
      textArea.focus();
    }

    function closePanel() {
      panel.classList.remove("open");
      toggleBtn.setAttribute("aria-expanded", "false");
      toggleBtn.setAttribute("aria-label", "Expand Project Notes");
      toggleBtn.setAttribute("title", "Expand Project Notes");
      panel.setAttribute("aria-hidden", "true");
      toggleBtn.focus();
    }

    function openPopout() {
      const pop = window.open("", "AffineDriftNotesWorkspace", "width=650,height=520,resizable=yes,scrollbars=yes");
      if (!pop) {
        setStatus("Pop-out blocked by browser.");
        return;
      }
      pop.document.write(
        '<!doctype html>' +
        '<html><head><title>AffineDrift Project Notes</title></head>' +
        '<body style="font-family: sans-serif; margin: 1rem;">' +
          '<h2 style="margin-top:0;">AffineDrift Project Notes</h2>' +
          '<textarea id="notes" style="width:100%; min-height:360px;"></textarea>' +
          '<div style="margin-top:0.75rem;">' +
            '<button type="button" id="save" aria-label="Save notes" title="Save notes">Save</button>' +
            '<button type="button" id="close" aria-label="Close notes workspace" title="Close notes workspace">Close</button>' +
          '</div>' +
          '<scr' + 'ipt>' +
            'const area = document.getElementById("notes");' +
            'document.getElementById("save").addEventListener("click", function () {' +
              'window.opener.postMessage({ type: "AD_NOTES_SAVE", content: area.value }, window.opener.location.origin);' +
            '});' +
            'document.getElementById("close").addEventListener("click", function () { window.close(); });' +
          '</scr' + 'ipt>' +
        '</body></html>'
      );
      pop.document.close();
      // Securely set the value without XSS risk from document.write
      pop.document.getElementById("notes").value = textArea.value;
      setStatus("Opened pop-out workspace.");
    }

    // Debounced autosave on input
    textArea.addEventListener("input", debounce(function () {
      store.saveActive(textArea.value);
      setStatus("Autosaved.");
    }, 500));

    // Flush pending save when tab is hidden (e.g. user closes/switches tab)
    document.addEventListener("visibilitychange", function () {
      if (document.visibilityState === "hidden") {
        store.saveActive(textArea.value);
      }
    });

    window.addEventListener("message", function (event) {
      // Security: only accept messages from our own origin (pop-out window)
      if (event.origin !== window.location.origin) return;
      if (!event || !event.data || event.data.type !== "AD_NOTES_SAVE") return;
      if (typeof event.data.content !== "string") return;
      store.saveActive(event.data.content);
      textArea.value = event.data.content;
      setStatus("Saved from pop-out.");
    });

    toggleBtn.addEventListener("click", function () {
      if (panel.classList.contains("open")) {
        closePanel();
      } else {
        openPanel();
      }
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && panel.classList.contains("open")) {
        closePanel();
      }
    });

    panel.addEventListener("keydown", function (event) {
      if (event.key !== "Tab") return;

      const elements = panel.getElementsByTagName('*');
      const focusableContent = [];
      for (const el of elements) {
          const tag = el.tagName;
          if (tag === 'BUTTON' || tag === 'INPUT' || tag === 'SELECT' || tag === 'TEXTAREA') {
              if (!el.disabled && el.tabIndex >= 0) focusableContent.push(el);
          } else if (tag === 'A' && el.hasAttribute('href')) {
              if (el.tabIndex >= 0) focusableContent.push(el);
          } else if (el.hasAttribute('tabindex') && el.getAttribute('tabindex') !== '-1') {
              focusableContent.push(el);
          }
      }

      if (focusableContent.length === 0) return;

      const firstFocusable = focusableContent[0];
      const lastFocusable = focusableContent[focusableContent.length - 1];

      if (event.shiftKey) {
        if (document.activeElement === firstFocusable) {
          lastFocusable.focus();
          event.preventDefault();
        }
      } else {
        if (document.activeElement === lastFocusable) {
          firstFocusable.focus();
          event.preventDefault();
        }
      }
    });

    panel.addEventListener("click", function (event) {
      const button = event.target.closest("button[data-action]");
      if (!button) return;
      const action = button.getAttribute("data-action");

      if (action === "close") {
        closePanel();
      } else if (action === "save") {
        store.saveActive(textArea.value);
        setStatus("Notes saved.");
      } else if (action === "clear") {
        if (!textArea.value.trim() || window.confirm("Clear notes? Saved copy will be moved to bin.")) {
          store.moveActiveToRecycleBin();
          textArea.value = "";
          setStatus("Cleared — recoverable from bin.");
        }
      } else if (action === "delete") {
        store.saveActive(textArea.value);
        const moved = store.moveActiveToRecycleBin();
        textArea.value = "";
        setStatus(moved ? "Deleted to recycle bin." : "Nothing to delete.");
      } else if (action === "restore") {
        const restored = store.restoreFromRecycleBin();
        if (restored) {
          textArea.value = store.loadActive().content;
          setStatus("Restored from recycle bin.");
        } else {
          setStatus("Recycle bin is empty.");
        }
      } else if (action === "popout") {
        openPopout();
      }
    });

    loadIntoTextArea();
    return { store };
  }

  function initOnDomReady() {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", function () {
        initNotesWorkspace();
      });
    } else {
      initNotesWorkspace();
    }
  }

  if (typeof window !== "undefined") {
    window.AffineDriftNotesWorkspace = { initNotesWorkspace, NotesWorkspaceStore, STORAGE_KEYS };
    if (!window.__AFFINEDRIFT_NOTES_NO_AUTO_INIT__) {
      initOnDomReady();
    }
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = { initNotesWorkspace, NotesWorkspaceStore, STORAGE_KEYS };
  }
})();
