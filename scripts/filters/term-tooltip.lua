-- scripts/filters/term-tooltip.lua
-- Pandoc / Quarto Lua filter for site-wide glossary tooltips (WEB-01.5 / Issue #4490).
--
-- Transforms {{< term key >}} and {{< term key "label" >}} shortcodes
-- into accessible WAI-ARIA tooltip markup linked to /pages/glossary.html#key.

local cached_glossary = nil

local function find_glossary_file()
  local candidates = {}

  if PANDOC_SCRIPT_FILE then
    local script_dir = PANDOC_SCRIPT_FILE:match("(.*)[/\\]")
    if script_dir then
      local base = script_dir:match("(.*)[/\\]filters") or script_dir:match("(.*)[/\\]scripts")
      if base then
        table.insert(candidates, base .. "/data/glossary.yml")
      end
      table.insert(candidates, script_dir .. "/../../data/glossary.yml")
    end
  end

  table.insert(candidates, "data/glossary.yml")
  table.insert(candidates, "../data/glossary.yml")
  table.insert(candidates, "../../data/glossary.yml")

  for _, path in ipairs(candidates) do
    local f = io.open(path, "r")
    if f then
      f:close()
      return path
    end
  end
  return nil
end

local function load_glossary()
  if cached_glossary ~= nil then
    return cached_glossary
  end

  cached_glossary = {}
  local path = find_glossary_file()
  if not path then
    return cached_glossary
  end

  local f = io.open(path, "r")
  if not f then
    return cached_glossary
  end

  local content = f:read("*a")
  f:close()

  local dummy = "---\n" .. content .. "\n---"
  local doc = pandoc.read(dummy, "markdown")
  if doc and doc.meta then
    for k, v in pairs(doc.meta) do
      local item = {}
      if type(v) == "table" then
        if v.name then
          item.name = pandoc.utils.stringify(v.name)
        end
        if v.plain then
          item.plain = pandoc.utils.stringify(v.plain)
        end
        if v.technical then
          item.technical = pandoc.utils.stringify(v.technical)
        end
        if v.canonical_page then
          item.canonical_page = pandoc.utils.stringify(v.canonical_page)
        end
      end
      cached_glossary[k] = item
    end
  end

  return cached_glossary
end

local function escape_html(str)
  local map = {
    ["&"] = "&amp;",
    ["<"] = "&lt;",
    [">"] = "&gt;",
    ['"'] = "&quot;",
    ["'"] = "&#39;"
  }
  return (str:gsub("[&<>'\"']", map))
end

local function make_tooltip_html(key, label)
  local glossary = load_glossary()
  local entry = glossary[key]

  local plain_def = ""
  if entry and entry.plain and entry.plain ~= "" then
    plain_def = entry.plain
  else
    plain_def = label .. " (definition)"
  end

  local safe_key = escape_html(key)
  local safe_label = escape_html(label)
  local safe_plain = escape_html(plain_def)

  return string.format(
    '<a href="/pages/glossary.html#%s" class="glossary-term" data-term="%s" aria-describedby="tt-%s" tabindex="0">' ..
    '<span class="glossary-term__label">%s</span>' ..
    '<span class="glossary-tooltip" id="tt-%s" role="tooltip">%s</span>' ..
    '</a>',
    safe_key, safe_key, safe_key, safe_label, safe_key, safe_plain
  )
end

function Pandoc(doc)
  local glossary = load_glossary()

  return doc:walk({
    Span = function(span)
      if span.attributes["__quarto_custom"] == "true" and quarto and quarto._quarto and quarto._quarto.ast then
        local custom_data, t, kind = quarto._quarto.ast.resolve_custom_data(span)
        if t == "Shortcode" and custom_data and custom_data.name == "term" then
          local key = ""
          local label = nil

          if custom_data.params and #custom_data.params >= 1 then
            key = custom_data.params[1].value or ""
          end
          if custom_data.params and #custom_data.params >= 2 then
            label = custom_data.params[2].value
          end

          if not label or label == "" then
            local entry = glossary[key]
            if entry and entry.name then
              label = entry.name
            else
              label = key
            end
          end

          local html = make_tooltip_html(key, label)
          return pandoc.RawInline("html", html)
        end
      end
      return span
    end,

    RawInline = function(raw)
      if raw.format == "html" then
        -- Handle potential fallback unparsed raw shortcode {{< term ... >}}
        local key, label = raw.text:match('^{{<%s*term%s+([%w%-_]+)%s*"([^"]+)"%s*>}}$')
        if not key then
          key = raw.text:match("^{{<%s*term%s+([%w%-_]+)%s*>}}$")
        end
        if key then
          if not label or label == "" then
            local entry = glossary[key]
            if entry and entry.name then
              label = entry.name
            else
              label = key
            end
          end
          local html = make_tooltip_html(key, label)
          return pandoc.RawInline("html", html)
        end
      end
      return raw
    end
  })
end
