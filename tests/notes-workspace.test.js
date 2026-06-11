/**
 * Tests for src/js/notes-workspace.js
 */

describe("Notes Workspace", () => {
  let NotesWorkspaceStore;
  let initNotesWorkspace;
  let STORAGE_KEYS;

  beforeEach(() => {
    jest.resetModules();
    localStorage.clear();
    sessionStorage.clear();
    document.body.innerHTML = "";
    window.__AFFINEDRIFT_NOTES_NO_AUTO_INIT__ = true;

    const mod = require("../js/notes-workspace.js");
    NotesWorkspaceStore = mod.NotesWorkspaceStore;
    initNotesWorkspace = mod.initNotesWorkspace;
    STORAGE_KEYS = mod.STORAGE_KEYS;
  });

  afterEach(() => {
    delete window.__AFFINEDRIFT_NOTES_NO_AUTO_INIT__;
    jest.useRealTimers();
  });

  test("save and load active notes", () => {
    const store = new NotesWorkspaceStore(localStorage);
    store.saveActive("Research notes");
    const loaded = store.loadActive();

    expect(loaded.content).toBe("Research notes");
    expect(typeof loaded.updatedAt).toBe("string");
  });

  test("clear removes active notes", () => {
    const store = new NotesWorkspaceStore(localStorage);
    store.saveActive("Temp note");
    store.clearActive();

    expect(store.loadActive().content).toBe("");
  });

  test("corrupt active notes are discarded during recovery", () => {
    localStorage.setItem(STORAGE_KEYS.active, "{not-json");
    const store = new NotesWorkspaceStore(localStorage);

    expect(store.loadActive().content).toBe("");
    expect(localStorage.getItem(STORAGE_KEYS.active)).toBeNull();
  });

  test("expired recycle bin notes are removed", () => {
    const oldDate = new Date(Date.now() - 31 * 24 * 60 * 60 * 1000).toISOString();
    localStorage.setItem(
      STORAGE_KEYS.recycleBin,
      JSON.stringify([{ content: "Old note", deletedAt: oldDate }]),
    );
    const store = new NotesWorkspaceStore(localStorage);

    expect(store.loadRecycleBin().content).toBe("");
    expect(localStorage.getItem(STORAGE_KEYS.recycleBin)).toBeNull();
  });

  test("legacy single-object recycle bin is normalised to array on load", () => {
    const deletedAt = new Date().toISOString();
    localStorage.setItem(
      STORAGE_KEYS.recycleBin,
      JSON.stringify({ content: "Legacy note", deletedAt }),
    );
    const store = new NotesWorkspaceStore(localStorage);
    const bin = store.loadRecycleBin();

    expect(bin.content).toBe("Legacy note");
    expect(Array.isArray(bin.snapshots)).toBe(true);
    expect(bin.snapshots).toHaveLength(1);
  });

  test("delete to recycle bin and restore", () => {
    const store = new NotesWorkspaceStore(localStorage);
    store.saveActive("Important note");

    const moved = store.moveActiveToRecycleBin();
    expect(moved).toBe(true);
    expect(store.loadActive().content).toBe("");

    const bin = store.loadRecycleBin();
    expect(bin.content).toBe("Important note");
    expect(Array.isArray(bin.snapshots)).toBe(true);

    const restored = store.restoreFromRecycleBin();
    expect(restored).toBe(true);
    expect(store.loadActive().content).toBe("Important note");
    expect(store.loadRecycleBin().content).toBe("");
  });

  test("bin accumulates multiple snapshots", () => {
    const store = new NotesWorkspaceStore(localStorage);

    store.saveActive("First note");
    store.moveActiveToRecycleBin();

    store.saveActive("Second note");
    store.moveActiveToRecycleBin();

    const bin = store.loadRecycleBin();
    expect(bin.snapshots).toHaveLength(2);
    expect(bin.content).toBe("Second note");
  });

  test("restore removes only the latest snapshot, leaving earlier ones", () => {
    const store = new NotesWorkspaceStore(localStorage);

    store.saveActive("First note");
    store.moveActiveToRecycleBin();

    store.saveActive("Second note");
    store.moveActiveToRecycleBin();

    store.restoreFromRecycleBin();

    const bin = store.loadRecycleBin();
    expect(bin.snapshots).toHaveLength(1);
    expect(bin.content).toBe("First note");
  });

  test("clear button routes through bin and requires confirmation", () => {
    const store = new NotesWorkspaceStore(localStorage);
    store.saveActive("Do not lose me");
    initNotesWorkspace({ store });

    const toggle = document.getElementById("ad-notes-workspace-toggle");
    toggle.click();

    const textarea = document.getElementById("ad-notes-workspace-area");
    textarea.value = "Do not lose me";

    window.confirm = jest.fn(() => true);

    const clearBtn = document.querySelector('[data-action="clear"]');
    clearBtn.click();

    expect(window.confirm).toHaveBeenCalled();
    expect(textarea.value).toBe("");
    const bin = store.loadRecycleBin();
    expect(bin.snapshots.length).toBeGreaterThan(0);
  });

  test("clear button does nothing when textarea is empty", () => {
    const store = new NotesWorkspaceStore(localStorage);
    initNotesWorkspace({ store });

    const toggle = document.getElementById("ad-notes-workspace-toggle");
    toggle.click();

    window.confirm = jest.fn(() => false);

    const clearBtn = document.querySelector('[data-action="clear"]');
    clearBtn.click();

    expect(window.confirm).not.toHaveBeenCalled();
  });

  test("autosave fires after input event with fake timers", () => {
    jest.useFakeTimers();
    const store = new NotesWorkspaceStore(localStorage);
    initNotesWorkspace({ store });

    const toggle = document.getElementById("ad-notes-workspace-toggle");
    toggle.click();

    const textarea = document.getElementById("ad-notes-workspace-area");
    textarea.value = "Autosave me";

    textarea.dispatchEvent(new Event("input"));

    jest.advanceTimersByTime(600);

    const payload = JSON.parse(localStorage.getItem(STORAGE_KEYS.active));
    expect(payload).not.toBeNull();
    expect(payload.content).toBe("Autosave me");
  });

  test("init renders embedded workspace and saves via UI", () => {
    const store = new NotesWorkspaceStore(localStorage);
    initNotesWorkspace({ store });

    const toggle = document.getElementById("ad-notes-workspace-toggle");
    expect(toggle).toBeTruthy();

    toggle.click();
    const textarea = document.getElementById("ad-notes-workspace-area");
    textarea.value = "UI-saved notes";

    const saveBtn = document.querySelector('[data-action="save"]');
    saveBtn.click();

    const payload = JSON.parse(localStorage.getItem(STORAGE_KEYS.active));
    expect(payload.content).toBe("UI-saved notes");
  });
});
