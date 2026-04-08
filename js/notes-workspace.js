(function () {
  "use strict";

  const STORAGE_KEYS = Object.freeze({
    active: "affinedrift_notes_workspace_v1",
    recycleBin: "affinedrift_notes_recycle_bin_v1",
  });

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

  class NotesWorkspaceStore {
    constructor(storage) {
      if (!storage || typeof storage.getItem !== "function" || typeof storage.setItem !== "function") {
        throw new Error("NotesWorkspaceStore requires a storage implementation");
      }
      this.storage = storage;
    }

    loadActive() {
      const parsed = safeParseJson(this.storage.getItem(STORAGE_KEYS.active), null);
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
      const parsed = safeParseJson(this.storage.getItem(STORAGE_KEYS.recycleBin), null);
      if (!parsed || typeof parsed.content !== "string") {
        return { content: "", deletedAt: null };
      }
      return { content: parsed.content, deletedAt: parsed.deletedAt || null };
    }

    moveActiveToRecycleBin() {
      const active = this.loadActive();
      if (!active.content.trim()) return false;
      const payload = { content: active.content, deletedAt: nowIso() };
      this.storage.setItem(STORAGE_KEYS.recycleBin, JSON.stringify(payload));
      this.clearActive();
      return true;
    }

    restoreFromRecycleBin() {
      const recycled = this.loadRecycleBin();
      if (!recycled.content.trim()) return false;
      this.saveActive(recycled.content);
      this.storage.removeItem(STORAGE_KEYS.recycleBin);
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
        background: #fff; border: 1px solid #d9e1e8; border-radius: 12px; box-shadow: 0 14px 30px rgba(15, 76, 117, 0.18);
        z-index: 1200; padding: 0.8rem; display: none;
      }
      .ad-notes-panel.open { display: block; }
      .ad-notes-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
      .ad-notes-header h3 { margin: 0; font-size: 1rem; color: #0f4c75; }
      .ad-notes-area {
        width: 100%; min-height: 210px; border: 1px solid #cad4de; border-radius: 8px;
        padding: 0.65rem; font-size: 0.92rem; resize: none; overflow: hidden; line-height: 1.45;
      }
      .ad-notes-actions { display: flex; flex-wrap: wrap; gap: 0.45rem; margin-top: 0.6rem; }
      .ad-notes-actions button {
        border: 1px solid #d1dbe4; background: #f7fafc; color: #243746; border-radius: 6px;
        padding: 0.38rem 0.6rem; font-size: 0.82rem; cursor: pointer;
      }
      .ad-notes-actions .danger { border-color: #f0b9b9; background: #fff3f3; color: #8c2323; }
      .ad-notes-status { font-size: 0.78rem; color: #5e6d7a; margin-top: 0.45rem; min-height: 1.1rem; }
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
    toggleBtn.textContent = "Project Notes";

    const panel = document.createElement("section");
    panel.id = "ad-notes-workspace-panel";
    panel.className = "ad-notes-panel";
    panel.setAttribute("aria-label", "Project notes workspace");
    panel.innerHTML = `
      <div class="ad-notes-header">
        <h3>Project Notes</h3>
        <button type="button" data-action="close" aria-label="Close notes workspace">x</button>
      </div>
      <textarea id="ad-notes-workspace-area" class="ad-notes-area" placeholder="Capture research notes, ideas, and follow-ups..."></textarea>
      <div class="ad-notes-actions">
        <button type="button" data-action="save">Save</button>
        <button type="button" data-action="clear">Clear</button>
        <button type="button" data-action="delete" class="danger">Delete to Bin</button>
        <button type="button" data-action="restore">Restore Bin</button>
        <button type="button" data-action="popout">Pop-out</button>
      </div>
      <div class="ad-notes-status" id="ad-notes-status" aria-live="polite" aria-atomic="true"></div>
    `;

    document.body.appendChild(toggleBtn);
    document.body.appendChild(panel);

    const textArea = panel.querySelector("#ad-notes-workspace-area");
    const status = panel.querySelector("#ad-notes-status");

    function autoGrow() {
      textArea.style.height = 'auto';
      textArea.style.height = textArea.scrollHeight + 'px';
    }

    textArea.addEventListener("input", autoGrow);

    function setStatus(message) {
      status.textContent = message;
    }

    function loadIntoTextArea() {
      const active = store.loadActive();
      textArea.value = active.content;
      autoGrow();
      if (active.updatedAt) {
        setStatus(`Loaded saved notes (${active.updatedAt})`);
      } else {
        setStatus("No saved notes yet.");
      }
    }

    function openPanel() {
      panel.classList.add("open");
      toggleBtn.setAttribute("aria-expanded", "true");
      textArea.focus();
    }

    function closePanel() {
      panel.classList.remove("open");
      toggleBtn.setAttribute("aria-expanded", "false");
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
            '<button id="save">Save</button>' +
            '<button id="close">Close</button>' +
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

    window.addEventListener("message", function (event) {
      // Security: only accept messages from our own origin (pop-out window)
      if (event.origin !== window.location.origin) return;
      if (!event || !event.data || event.data.type !== "AD_NOTES_SAVE") return;
      if (typeof event.data.content !== "string") return;
      store.saveActive(event.data.content);
      textArea.value = event.data.content;
      autoGrow();
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
        textArea.value = "";
        autoGrow();
        store.clearActive();
        setStatus("Workspace cleared.");
      } else if (action === "delete") {
        store.saveActive(textArea.value);
        const moved = store.moveActiveToRecycleBin();
        textArea.value = "";
        autoGrow();
        setStatus(moved ? "Deleted to recycle bin." : "Nothing to delete.");
      } else if (action === "restore") {
        const restored = store.restoreFromRecycleBin();
        if (restored) {
          textArea.value = store.loadActive().content;
          autoGrow();
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
