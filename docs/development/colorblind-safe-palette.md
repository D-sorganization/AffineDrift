# Colorblind-Safe Color Palette

## Okabe-Ito Color Palette

The Okabe-Ito palette is specifically designed to be distinguishable by people with all forms of color blindness.

### Primary Colors

```css
/* Okabe-Ito Colorblind-Safe Palette */
--color-orange: #E69F00;      /* Orange - Primary accent */
--color-sky-blue: #56B4E9;    /* Sky Blue - Secondary accent */
--color-green: #009E73;        /* Bluish Green - Success/positive */
--color-yellow: #F0E442;       /* Yellow - Warning/highlight */
--color-blue: #0072B2;         /* Blue - Links/interactive */
--color-vermillion: #D55E00;   /* Vermillion - Error/danger */
--color-purple: #CC79A7;       /* Reddish Purple - Special */
--color-black: #000000;        /* Black - Text */
--color-gray: #999999;         /* Gray - Secondary text */
```

### Usage Guidelines

#### For Graphs and Charts
- Use colors in order: Orange, Sky Blue, Green, Yellow, Blue, Vermillion, Purple
- Avoid using only color to convey information (use patterns, labels, or shapes)
- Ensure sufficient contrast between adjacent colors

#### For UI Elements
- **Links:** Blue (#0072B2)
- **Success/Positive:** Green (#009E73)
- **Warning:** Yellow (#F0E442) with dark text
- **Error/Danger:** Vermillion (#D55E00)
- **Primary Actions:** Orange (#E69F00)
- **Secondary Actions:** Sky Blue (#56B4E9)

#### For Data Visualization
```python
# Matplotlib style
colors = ["#E69F00", "#56B4E9", "#009E73", "#F0E442", 
          "#0072B2", "#D55E00", "#CC79A7"]
```

### Contrast Ratios (WCAG AA Compliance)

All colors meet WCAG AA contrast requirements when used appropriately:

| Color | On White BG | On Black BG | Use Case |
|-------|-------------|-------------|----------|
| Orange (#E69F00) | 3.4:1 | 6.2:1 | Accent, buttons (with dark text on white) |
| Sky Blue (#56B4E9) | 2.9:1 | 7.2:1 | Secondary accent (with dark text) |
| Green (#009E73) | 3.9:1 | 5.4:1 | Success messages |
| Yellow (#F0E442) | 1.4:1 | 15:1 | Highlights (requires dark text) |
| Blue (#0072B2) | 5.1:1 | 4.1:1 | Links, primary actions |
| Vermillion (#D55E00) | 4.8:1 | 4.4:1 | Errors, warnings |
| Purple (#CC79A7) | 3.2:1 | 6.6:1 | Special elements |

### Implementation Checklist

- [ ] Update CSS variables in custom.scss
- [ ] Update matplotlib style files
- [ ] Update chart colors in JavaScript
- [ ] Test with colorblind simulators
- [ ] Verify WCAG AA contrast compliance
- [ ] Update design system documentation

### Testing Tools

- **Coblis** - Color Blindness Simulator: https://www.color-blindness.com/coblis-color-blindness-simulator/
- **Colorblind Web Page Filter**: https://www.toptal.com/designers/colorfilter
- **Chrome DevTools** - Built-in vision deficiency emulator

### References

- Okabe, M. and Ito, K. (2008). "Color Universal Design (CUD): How to make figures and presentations that are friendly to Colorblind people"
- Wong, B. (2011). "Points of view: Color blindness." Nature Methods 8, 441.
