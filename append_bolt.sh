cat << 'INNER_EOF' >> .jules/bolt.md

## 2024-06-15 - Live Collection Arrays vs NodeLists
**Learning:** Using `document.getElementsByTagName` returns a live `HTMLCollection`, unlike `querySelectorAll` which returns a static `NodeList`. Modifying the DOM during iteration over a live collection can cause elements to be skipped or reprocessed unexpectedly. In a \`for...of\` loop on an array formed by \`Array.from(collection)\`, \`return\` stops the entire function while \`continue\` skips to the next item; do not substitute one for the other when translating from a \`forEach\` callback.
**Action:** When converting global DOM queries to `getElementsByTagName` to improve performance, ensure that iterations modifying the DOM (like adding wrapper divs) either iterate backwards or copy the collection to a static array first using `Array.from()`. When replacing \`forEach\` with \`for...of\`, remember to translate \`return\` statements into \`continue\`.
INNER_EOF
