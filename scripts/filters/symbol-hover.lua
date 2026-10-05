-- scripts/filters/symbol-hover.lua
-- Symbol hover references (WEB-11.6 / Issue #4584).
--
-- Authors mark a symbol in TeX as \symref{key}{tex}. On HTML pages whose front
-- matter sets `symbol-hover: true`, the marker becomes MathJax
-- \class{symref symref--key}{tex} (a hook for js/symbol-hover.js) and each
-- block that uses markers is followed by a native <details> list of its
-- symbols. MathJax hides its visual output from assistive technology, so the
-- list, not the hover, is the keyboard and screen-reader path. Everywhere
-- else the marker is replaced by its plain tex. Definitions come from
-- data/symbol_references.json, generated from NOTATION.md.

local SCRIPT_TAG = '<script src="/js/symbol-hover.js" defer></script>'
local MARKER = "\\symref{"

local function registry_path()
  local candidates = { "data/symbol_references.json" }
  if PANDOC_SCRIPT_FILE then
    local here = pandoc.path.directory(PANDOC_SCRIPT_FILE)
    table.insert(candidates, 1, pandoc.path.join({ here, "..", "..", "data", "symbol_references.json" }))
  end
  for _, path in ipairs(candidates) do
    local f = io.open(path, "r")
    if f then
      f:close()
      return path
    end
  end
  return nil
end

local function load_registry()
  local registry = { anchor = "", symbols = {} }
  local path = registry_path()
  if not path then
    io.stderr:write("symbol-hover: data/symbol_references.json not found\n")
    return registry
  end
  local f = io.open(path, "r")
  local data = pandoc.json.decode(f:read("*a"), false)
  f:close()
  registry.anchor = data.anchor
  for _, entry in ipairs(data.symbols) do
    registry.symbols[entry.key] = entry
  end
  return registry
end

local function escape_html(str)
  local map = { ["&"] = "&amp;", ["<"] = "&lt;", [">"] = "&gt;", ['"'] = "&quot;", ["'"] = "&#39;" }
  return (str:gsub("[&<>\"']", map))
end

-- Index of the brace closing the group that opens at `open`, or nil.
local function closing_brace(text, open)
  local depth, i = 0, open
  while i <= #text do
    local c = text:sub(i, i)
    if c == "\\" then
      i = i + 1
    elseif c == "{" then
      depth = depth + 1
    elseif c == "}" then
      depth = depth - 1
      if depth == 0 then
        return i
      end
    end
    i = i + 1
  end
  return nil
end

-- Rewrite every \symref{key}{tex} in `text`; record used keys in `used`.
local function rewrite(text, ctx, used)
  local out, pos = {}, 1
  while true do
    local start = text:find(MARKER, pos, true)
    if not start then
      break
    end
    local key_end = text:find("}", start + #MARKER, true)
    local arg_open = key_end and key_end + 1
    local arg_close = arg_open and text:sub(arg_open, arg_open) == "{" and closing_brace(text, arg_open)
    if not arg_close then
      io.stderr:write("symbol-hover: malformed \\symref; expected \\symref{key}{tex}\n")
      break
    end
    local key = text:sub(start + #MARKER, key_end - 1)
    local inner = rewrite(text:sub(arg_open + 1, arg_close - 1), ctx, used)
    table.insert(out, text:sub(pos, start - 1))
    if ctx.enabled and ctx.registry.symbols[key] then
      table.insert(out, "\\class{symref symref--" .. key .. "}{" .. inner .. "}")
      used[#used + 1] = key
    else
      if not ctx.registry.symbols[key] then
        io.stderr:write("symbol-hover: unknown symbol key '" .. key .. "'\n")
      end
      table.insert(out, "{" .. inner .. "}")
    end
    pos = arg_close + 1
  end
  table.insert(out, text:sub(pos))
  return table.concat(out)
end

local function symbol_list(keys, registry)
  local seen, items = {}, {}
  for _, key in ipairs(keys) do
    if not seen[key] then
      seen[key] = true
      local entry = registry.symbols[key]
      table.insert(items, string.format(
        '<div class="symbol-refs__item" data-symref="%s"><dt>%s</dt><dd>%s</dd></div>',
        escape_html(key), escape_html(entry.name), escape_html(entry.definition)))
    end
  end
  return pandoc.RawBlock("html",
    '<details class="symbol-refs"><summary>Symbols in this equation</summary>' ..
    '<dl class="symbol-refs__list">' .. table.concat(items) .. '</dl>' ..
    '<p class="symbol-refs__source"><a href="' .. escape_html(registry.anchor) ..
    '">Notation reference</a></p></details>')
end

local function is_html()
  if quarto and quarto.doc and quarto.doc.is_format then
    return quarto.doc.is_format("html")
  end
  return FORMAT:match("html") ~= nil
end

local function opted_in(meta)
  local flag = meta["symbol-hover"]
  return flag == true or (flag ~= nil and pandoc.utils.stringify(flag) == "true")
end

function Pandoc(doc)
  local ctx = { enabled = is_html() and opted_in(doc.meta), registry = load_registry() }
  local script_emitted = false

  local function mark(block)
    local used = {}
    local rewritten = block:walk({
      Math = function(math)
        if math.text:find(MARKER, 1, true) then
          math.text = rewrite(math.text, ctx, used)
          return math
        end
      end,
    })
    if #used == 0 then
      return rewritten
    end
    local blocks = { rewritten, symbol_list(used, ctx.registry) }
    -- Emitted beside the first list: the site's later filters rebuild the page
    -- body and drop document-level includes, but keep these content blocks.
    if not script_emitted then
      script_emitted = true
      table.insert(blocks, pandoc.RawBlock("html", SCRIPT_TAG))
    end
    return blocks
  end

  return doc:walk({ Para = mark, Plain = mark })
end
