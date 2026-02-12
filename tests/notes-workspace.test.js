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
    document.body.innerHTML = "";
    window.__AFFINEDRIFT_NOTES_NO_AUTO_INIT__ = true;

    const mod = require("../src/js/notes-workspace.js");
    NotesWorkspaceStore = mod.NotesWorkspaceStore;
    initNotesWorkspace = mod.initNotesWorkspace;
    STORAGE_KEYS = mod.STORAGE_KEYS;
  });

  afterEach(() => {
    delete window.__AFFINEDRIFT_NOTES_NO_AUTO_INIT__;
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

  test("delete to recycle bin and restore", () => {
    const store = new NotesWorkspaceStore(localStorage);
    store.saveActive("Important note");

    const moved = store.moveActiveToRecycleBin();
    expect(moved).toBe(true);
    expect(store.loadActive().content).toBe("");

    const recycled = store.loadRecycleBin();
    expect(recycled.content).toBe("Important note");

    const restored = store.restoreFromRecycleBin();
    expect(restored).toBe(true);
    expect(store.loadActive().content).toBe("Important note");
    expect(store.loadRecycleBin().content).toBe("");
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
