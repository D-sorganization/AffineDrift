# Notes Workspace

Issue: https://github.com/D-sorganization/AffineDrift/issues/1106

## Feature Summary

AffineDrift now includes a project notes workspace with:
- embedded drawer UI (`Project Notes` floating button)
- local persistence in browser storage
- safe delete-to-recycle-bin
- restore-from-bin action
- pop-out workspace window

## Storage Keys

- Active notes: `affinedrift_notes_workspace_v1`
- Recycle bin: `affinedrift_notes_recycle_bin_v1`

## User Flows

1. Open workspace from the `Project Notes` button.
2. Write/edit notes and click `Save`.
3. Click `Clear` to clear active workspace text.
4. Click `Delete to Bin` for reversible deletion.
5. Click `Restore Bin` to recover deleted notes.
6. Click `Pop-out` to open notes in a separate window and save back.

## Testing

Covered in:
- `tests/notes-workspace.test.js`

Validated flows:
- save/load
- clear
- delete-to-bin
- restore
- embedded UI save integration
