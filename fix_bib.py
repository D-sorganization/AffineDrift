import sys

with open("js/bibliography.js", "r") as f:
    content = f.read()

search1 = """    listEl.textContent = "";

    state.filtered.forEach((entry) => {"""

replace1 = """    listEl.textContent = "";

    const fragment = document.createDocumentFragment();

    for (const entry of state.filtered) {"""

content = content.replace(search1, replace1)

search2 = """            entry.concepts.slice(0, 4).forEach(c => {
                const span = document.createElement("span");
                span.className = "concept-tag";
                span.textContent = c;
                conceptsDiv.appendChild(span);
            });"""

replace2 = """            for (const c of entry.concepts.slice(0, 4)) {
                const span = document.createElement("span");
                span.className = "concept-tag";
                span.textContent = c;
                conceptsDiv.appendChild(span);
            }"""

content = content.replace(search2, replace2)

search3 = """        btn.textContent = "View details";
        article.appendChild(btn);

        listEl.appendChild(article);
    });
  };"""

replace3 = """        btn.textContent = "View details";
        article.appendChild(btn);

        fragment.appendChild(article);
    }

    listEl.appendChild(fragment);
  };"""

print("Searching for:")
print(repr(search1))
print("Found:", search1 in content)

print("Searching for 2:")
print(repr(search2))
print("Found 2:", search2 in content)

print("Searching for 3:")
print(repr(search3))
print("Found 3:", search3 in content)
