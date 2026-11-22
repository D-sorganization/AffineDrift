-- Emit per-page Schema.org JSON-LD into <head> for pages that opt in with a
-- `schema-type` frontmatter field. Pages without it are left untouched, so
-- this filter is safe to register project-wide. Supersedes
-- _includes/article-schema.html, which was dead (referenced by no page) and
-- broken (`{{< meta >}}` shortcodes do not expand inside raw HTML includes);
-- resolving metadata here, in Lua, avoids that failure mode.
-- Technical references can link sources with schema-citations; DefinedTermSet
-- exports the canonical glossary-entry blocks rather than a second term catalog.
local SUPPORTED_TYPES = {
  ScholarlyArticle = true,
  Book = true,
  Chapter = true,
  Dataset = true,
  SoftwareSourceCode = true,
  TechArticle = true,
  DefinedTermSet = true,
}

local PUBLISHER_JSON = '{"@type": "Organization", "name": "AffineDrift", '
  .. '"logo": {"@type": "ImageObject", "url": "https://affinedrift.com/logo/og-card.png"}}'

local function json_escape(value)
  value = value:gsub("\\", "\\\\")
  value = value:gsub('"', '\\"')
  value = value:gsub("\r\n", "\\n")
  value = value:gsub("[\r\n]", "\\n")
  value = value:gsub("<", "\\u003c")
  value = value:gsub("[%z\1-\31]", function(char)
    return string.format("\\u%04x", string.byte(char))
  end)
  return value
end

-- Quarto's HTML format reformats `date` into a display string (e.g. "January
-- 15, 2026") before Lua filters run, so only pass it through when it is
-- still ISO 8601 -- an unrecognized shape is omitted rather than emitted as
-- a wrong-format `datePublished`.
local function iso_date(value)
  if value == nil then
    return nil
  end
  if value:match("^%d%d%d%d%-%d%d%-%d%d$") then
    return value
  end
  return nil
end

local function meta_string(value)
  if value == nil then
    return nil
  end
  local text = pandoc.utils.stringify(value)
  if text == "" then
    return nil
  end
  return text
end

local function first_author(meta)
  local author = meta.author
  if author == nil then
    return nil
  end
  if author.t == "MetaList" then
    author = author[1]
  end
  if author ~= nil and author.t == "MetaMap" and author.name ~= nil then
    author = author.name
  end
  return meta_string(author)
end

local function person_json(name)
  if name == nil then
    return nil
  end
  return '{"@type": "Person", "name": "' .. json_escape(name) .. '"}'
end

local function str_field(key, text)
  if text == nil then
    return nil
  end
  return '"' .. key .. '": "' .. json_escape(text) .. '"'
end

local function raw_field(key, json_text)
  if json_text == nil then
    return nil
  end
  return '"' .. key .. '": ' .. json_text
end

local function push(fields, field)
  if field ~= nil then
    table.insert(fields, field)
  end
end

local function citation_json(meta)
  if meta == nil then
    return nil
  end
  local citations = {}
  for _, item in ipairs(meta) do
    local value = meta_string(item)
    assert(value ~= nil and value:match("^https://"),
      "schema-citations must contain absolute HTTPS references")
    table.insert(citations, '"' .. json_escape(value) .. '"')
  end
  return "[" .. table.concat(citations, ", ") .. "]"
end

local glossary_entries = {}
local glossary_heading = nil

local function remember_term(block, identifier)
  table.insert(glossary_entries, {
    name = glossary_heading,
    description = pandoc.write(pandoc.Pandoc(block.content), "plain",
      pandoc.WriterOptions({wrap_text = "none"})),
    identifier = identifier,
  })
end

local function glossary_json(base_url)
  assert(base_url ~= nil and base_url:match("^https://"),
    "DefinedTermSet requires an absolute HTTPS schema-url")
  local terms = {}
  for _, term in ipairs(glossary_entries) do
    assert(term.name ~= nil and term.identifier:match("^def%-%S+$"),
      "glossary-entry requires a heading and stable def-* identifier")
    local fields = {'"@type": "DefinedTerm"'}
    push(fields, str_field("name", term.name))
    push(fields, str_field("description", term.description))
    push(fields, str_field("termCode", term.identifier))
    push(fields, str_field("url", base_url .. "#" .. term.identifier))
    push(fields, str_field("inDefinedTermSet", base_url))
    table.insert(terms, "{" .. table.concat(fields, ", ") .. "}")
  end
  assert(#terms > 0, "DefinedTermSet requires glossary-entry definitions")
  return "[" .. table.concat(terms, ", ") .. "]"
end

local function reset_glossary()
  glossary_entries = {}
  glossary_heading = nil
end

function Pandoc(doc)
  local schema_type = meta_string(doc.meta["schema-type"])
  if schema_type == nil or not SUPPORTED_TYPES[schema_type] then
    reset_glossary()
    return doc
  end

  local title = meta_string(doc.meta.title)
  local description = meta_string(doc.meta.description)
  local date = iso_date(meta_string(doc.meta.date))
  local author_json = person_json(first_author(doc.meta) or "Dieter Olson")

  local fields = {
    '"@context": "https://schema.org"',
    '"@type": "' .. schema_type .. '"',
  }

  if schema_type == "ScholarlyArticle" or schema_type == "TechArticle" or schema_type == "Chapter" then
    push(fields, str_field("headline", title))
  else
    push(fields, str_field("name", title))
  end
  push(fields, str_field("description", description))
  push(fields, raw_field("publisher", PUBLISHER_JSON))
  push(fields, str_field("url", meta_string(doc.meta["schema-url"])))
  push(fields, raw_field("citation", citation_json(doc.meta["schema-citations"])))

  if schema_type == "ScholarlyArticle" or schema_type == "TechArticle" then
    push(fields, raw_field("author", author_json))
    push(fields, str_field("datePublished", date))
    push(fields, raw_field("isAccessibleForFree", "true"))
  elseif schema_type == "Book" then
    push(fields, raw_field("author", author_json))
    push(fields, str_field("datePublished", date))
    push(fields, str_field("isbn", meta_string(doc.meta.isbn)))
  elseif schema_type == "Chapter" then
    push(fields, raw_field("author", author_json))
    local part_of_title = meta_string(doc.meta["part-of-title"])
    if part_of_title ~= nil then
      push(
        fields,
        raw_field("isPartOf", '{"@type": "CreativeWork", "name": "' .. json_escape(part_of_title) .. '"}')
      )
    end
    push(fields, str_field("position", meta_string(doc.meta["chapter-number"])))
  elseif schema_type == "Dataset" then
    push(fields, raw_field("creator", author_json))
    push(fields, str_field("datePublished", date))
    push(fields, str_field("license", meta_string(doc.meta.license)))
  elseif schema_type == "SoftwareSourceCode" then
    push(fields, raw_field("author", author_json))
    push(fields, str_field(
      "codeRepository",
      meta_string(doc.meta["code-repository"]) or "https://github.com/D-sorganization/AffineDrift"
    ))
    push(fields, str_field("programmingLanguage", meta_string(doc.meta["programming-language"])))
  elseif schema_type == "DefinedTermSet" then
    push(fields, raw_field("hasDefinedTerm", glossary_json(meta_string(doc.meta["schema-url"]))))
  end

  local json = "{\n  " .. table.concat(fields, ",\n  ") .. "\n}"
  quarto.doc.include_text("in-header", '<script type="application/ld+json">\n' .. json .. "\n</script>")

  reset_glossary()
  return doc
end

-- Quarto exposes def-* entries as Theorem nodes, with the ID moved off the Div.
-- Block callbacks run in reading order before Pandoc emits the collected metadata.
return {{
  Header = function(block)
    glossary_heading = pandoc.utils.stringify(block.content)
  end,
  Theorem = function(node)
    local div = node.div
    if div.classes:includes("glossary-entry") then
      remember_term(div, node.identifier)
    end
  end,
  Div = function(block)
    if block.identifier ~= "" and block.classes:includes("glossary-entry") then
      remember_term(block, block.identifier)
    end
  end,
  Pandoc = Pandoc,
}}
