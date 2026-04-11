# script.js Decomposition Plan

## Issue
#2358/#2330: script.js is 1753 LOC - a monolithic duplicate of the modular JS project.

## Status
Found at: script.js

## Proposed Module Layout

```
js/
  modules/
    ui.js          - DOM manipulation, event listeners
    physics.js     - Physics calculations (ball flight, putting)
    charts.js      - Chart.js wrappers and data formatting  
    api.js         - Fetch/AJAX API calls
    utils.js       - Shared utility functions
  main.js          - Entry point, module orchestration
```

## Migration Strategy
1. Create js/modules/ directory
2. Identify top-level functions by category (UI/Physics/Charts/API/Utils)
3. Extract each category to its own module with ES6 exports
4. Replace script.js imports with module imports in HTML templates
5. Delete legacy script.js once all consumers updated

## CI Gate
Add a check to CI that fails if any .js file exceeds 500 LOC.
