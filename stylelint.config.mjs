export default {
  extends: ["stylelint-config-standard"],
  ignoreFiles: ["docs/**", "_site/**", "node_modules/**", "playwright-report/**", "test-results/**"],
  rules: {
    "color-function-notation": null,
    "alpha-value-notation": null,
    "color-function-alias-notation": null,
    "no-descending-specificity": null,
    "comment-empty-line-before": null,
    "declaration-block-no-redundant-longhand-properties": null,
    "declaration-property-value-keyword-no-deprecated": null,
    "declaration-property-value-no-unknown": null,
    "import-notation": null,
    "media-feature-range-notation": null,
    "media-query-no-invalid": null,
    "no-duplicate-selectors": null,
    "rule-empty-line-before": null,
    "value-keyword-case": null,
    "selector-class-pattern": [
      "^(?:[a-z0-9\\-_]+|MathJax|MathJax_Display)$",
      {
        resolveNestedSelectors: true,
      },
    ],
  },
};
