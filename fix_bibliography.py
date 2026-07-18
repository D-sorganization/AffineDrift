import sys

with open("js/bibliography.js", "r") as f:
    content = f.read()

search = """
      const button = event.target.closest("button[data-details-id]");
      const card = event.target.closest("article[data-entry-id]");
      if (!button && !card) return;
      const entryId = button ? button.dataset.detailsId : card.dataset.entryId;
"""
replace = """
      // ⚡ Bolt Optimization: Consolidate multiple .closest() queries to prevent excessive JS-to-C++ boundary crossings
      const targetElement = event.target.closest("button[data-details-id], article[data-entry-id]");
      if (!targetElement) return;

      const isButton = targetElement.tagName.toLowerCase() === "button";
      const entryId = isButton ? targetElement.dataset.detailsId : targetElement.dataset.entryId;
"""

if search in content:
    content = content.replace(search, replace)
    with open("js/bibliography.js", "w") as f:
        f.write(content)
    print("Replaced!")
else:
    print("Not found.")
