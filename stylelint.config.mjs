export default {
  extends: ["stylelint-config-standard"],
  ignoreFiles: ["docs/**", "_site/**", "node_modules/**"],
  rules: {
    "color-function-notation": null,
    "alpha-value-notation": null,
    "no-descending-specificity": null,
    "selector-class-pattern": [
      "^(?:[a-z0-9\\-]+|MathJax)$",
      {
        resolveNestedSelectors: true,
      },
    ],
  },
};
