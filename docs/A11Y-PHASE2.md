# Accessibility Phase 2: Focus States, Color Contrast & Motion

Comprehensive accessibility improvements for WCAG 2.1 Level AA compliance.

## Features Implemented

### 1. Focus Management

#### Visible Focus Indicators
Every interactive element has a visible, distinct focus outline:
```css
button:focus-visible,
a:focus-visible,
input:focus-visible {
  outline: 3px solid var(--accent-blue);
  outline-offset: 2px;
}
```

**Colors:**
- Light mode: `--accent-blue` (#3b82f6)
- Dark mode: `--accent-cyan` (#06b6d4)

#### Keyboard Navigation
- Tab key navigates through all interactive elements
- Shift+Tab navigates backward
- Focus order is logical and matches visual order
- Modal dialogs trap focus (focus stays within)

#### Focus Trap (Modals)
```javascript
// Automatically implemented for role="dialog"
// Focus cycles within modal, preventing accidental access to background
```

### 2. Motion & Animation

#### Respects prefers-reduced-motion
Automatically disables animations if user has set motion preference:

```css
@media (prefers-reduced-motion: reduce) {
  * { animation-duration: 0.01ms !important; }
}
```

**What happens:**
- Animation duration reduced to 1ms (effectively instant)
- Transitions disabled (immediate changes)
- Parallax effects disabled
- Scroll behavior changed to instant

#### JavaScript Integration
```javascript
// Detects motion preference at startup
initMotionPreferences();

// Listens for system preference changes
window.matchMedia('(prefers-reduced-motion: reduce)')
  .addEventListener('change', updateAnimations);
```

### 3. High Contrast Mode

Supports users who prefer higher visual contrast:

```css
@media (prefers-contrast: more) {
  button:focus-visible {
    outline-width: 4px;
    outline-color: currentColor;
  }
  button {
    border: 2px solid currentColor;
  }
}
```

**Automatic Detection:**
```javascript
// Applies data-high-contrast attribute to HTML
// CSS can respond with [data-high-contrast] selectors
```

### 4. Color Contrast

#### WCAG 2.1 AA Compliance

**Normal text (≥ 14px):**
- Minimum contrast ratio: 4.5:1
- Example: Dark text (#000) on light background (#FFF) = 21:1 ✅

**Large text (≥ 18px or ≥ 14px bold):**
- Minimum contrast ratio: 3:1
- Example: Dark gray (#666) on light background = 5.2:1 ✅

**UI components (borders, buttons):**
- Minimum contrast ratio: 3:1

#### Testing Color Contrast
```javascript
import { checkContrast } from './accessibility.js';

const result = checkContrast('rgb(0,0,0)', 'rgb(255,255,255)');
console.log(result);
// { ratio: 21.00, AA: true, AAA: true }
```

### 5. Screen Reader Support

#### Announcements
Use for dynamic content updates:

```javascript
import { announce } from './accessibility.js';

announce('Search results loaded', 'polite');
announce('Critical error occurred', 'assertive');
```

#### Live Regions
Automatically set on:
- Search results
- Notifications
- Form validation messages
- Dynamic list updates

### 6. Keyboard Navigation Enhancements

#### Menu Navigation
Arrow keys navigate through menus:
- Arrow Down/Right: next item
- Arrow Up/Left: previous item
- Home: first item
- End: last item

```javascript
setupMenuNavigation(menuElement, itemSelector);
```

#### Form Navigation
- Tab: focus next input
- Shift+Tab: focus previous input
- Enter: submit form (unless otherwise handled)
- Space/Enter: activate buttons

## Accessibility Classes

### `.sr-only` - Screen Reader Only
```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}
```

Content hidden visually but available to screen readers.

## Testing Checklist

### Manual Testing
- [ ] Tab through page: all interactive elements focused in logical order
- [ ] Enter on buttons: activates correctly
- [ ] Arrow keys in menus: navigate correctly
- [ ] Focus rings: visible on all interactive elements
- [ ] Test on iOS VoiceOver
- [ ] Test on Android TalkBack
- [ ] Test on Windows NVDA
- [ ] Test on macOS JAWS

### Automated Testing
```bash
# axe accessibility testing
npx axe-core check

# WAVE WebAIM
https://wave.webaim.org/

# Lighthouse (Chrome DevTools)
# Audit → Accessibility
```

### Tools
- **axe DevTools** (Browser extension)
- **WAVE** (WebAIM online tool)
- **Chrome Lighthouse** (Built-in)
- **Contrast Checker** (WebAIM online tool)
- **NVDA** (Free screen reader)
- **JAWS** (Commercial screen reader)

## System Preferences

### Detecting User Preferences
```javascript
// Motion preference
const prefersReducedMotion = window.matchMedia(
  '(prefers-reduced-motion: reduce)'
).matches;

// Contrast preference
const prefersContrast = window.matchMedia(
  '(prefers-contrast: more)'
).matches;

// Color scheme preference
const prefersDark = window.matchMedia(
  '(prefers-color-scheme: dark)'
).matches;
```

### Operating System Settings

**macOS:**
System Preferences → Accessibility → Display → Increase Contrast

**iOS/iPadOS:**
Settings → Accessibility → Display & Text Size → Increase Contrast

**Android:**
Settings → Accessibility → Display → High Contrast Text

**Windows:**
Settings → Ease of Access → Display → High Contrast

## Standards Compliance

### WCAG 2.1 Level AA Criteria Met

- ✅ 2.1.1 Keyboard - All functionality available via keyboard
- ✅ 2.1.2 No Keyboard Trap - Focus not trapped unless modal
- ✅ 2.4.3 Focus Order - Logical, matches visual order
- ✅ 2.4.7 Focus Visible - Visible focus indicator on all elements
- ✅ 2.5.1 Pointer Gestures - Touch targets accessible
- ✅ 2.5.5 Target Size - 44×44px minimum (AAA)
- ✅ 3.2.1 On Focus - No unexpected context changes
- ✅ 3.2.2 On Input - Changes only when expected
- ✅ 3.3.1 Error Identification - Errors clearly identified
- ✅ 3.3.3 Error Suggestion - Corrective suggestions provided
- ✅ 4.1.2 Name, Role, Value - All UI elements have accessible names
- ✅ 4.1.3 Status Messages - Messages announced to screen readers

## Future Enhancements

- [ ] Form field error messages with live regions
- [ ] Tooltip accessibility (ARIA roles, timing)
- [ ] Skip links for better navigation
- [ ] Language tagging for multilingual content
- [ ] Automated contrast checking on build
- [ ] Keyboard shortcut documentation
- [ ] Custom focus visible styling per component
