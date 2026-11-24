-- _extensions/provenance/provenance.lua
-- Quarto shortcode {{< provenance [kwargs] >}}
-- Part of VIS-EVIDENCE-2 (#5420) - figure provenance captions
--
-- Renders a caption naming the UpstreamDrift model, run_id, commit and claim
-- class behind a figure. Fields come from kwargs, falling back to a
-- `provenance:` front-matter map shaped like the #5419 run-identity record.
-- Every value is validated, and links are built only from the public
-- UpstreamDrift repository URL, so no host detail can reach the page.
-- Invalid input fails the render rather than publishing a wrong caption.

local UD_REPO = "https://github.com/D-sorganization/UpstreamDrift"

local CLAIM_LABELS = {
  ["derived"] = "Derived",
  ["model_scenario"] = "Model scenario",
  ["observed"] = "Observed"
}

local function stringify(val)
  if val == nil then
    return ""
  end
  return (pandoc.utils.stringify(val):gsub("^%s+", ""):gsub("%s+$", ""))
end

local function escape_html(str)
  local map = {
    ["&"] = "&amp;",
    ["<"] = "&lt;",
    [">"] = "&gt;",
    ['"'] = "&quot;",
    ["'"] = "&#39;"
  }
  return (str:gsub("[&<>'\"]", map))
end

local function fail(field, value, rule)
  error("provenance: " .. field .. " '" .. value .. "' " .. rule, 0)
end

local function is_hex(value, min_len, max_len)
  return #value >= min_len and #value <= max_len and value:match("^[0-9a-f]+$") ~= nil
end

-- Identifier tokens: no ':' '@' or whitespace, so no URL, user@host or IP:port.
local function is_token(value)
  return value:match("^[%w][%w%._%-/]*$") ~= nil and not value:find("..", 1, true)
end

local VALIDATORS = {
  model_id = {
    check = is_token,
    rule = "must be a model identifier (letters, digits, . _ - /)"
  },
  run_id = {
    check = function(v) return v:match("^[%w][%w%._%-]*$") ~= nil end,
    rule = "must be a run identifier (letters, digits, . _ -)"
  },
  ud_commit = {
    check = function(v) return is_hex(v, 7, 40) end,
    rule = "must be a lowercase hex commit SHA (7-40 chars)"
  },
  claim_class = {
    check = function(v) return CLAIM_LABELS[v] ~= nil end,
    rule = "must be one of derived, model_scenario, observed"
  },
  model_path = {
    check = function(v) return is_token(v) and v:sub(1, 1) ~= "/" end,
    rule = "must be a repository-relative path without '..'"
  }
}

local REQUIRED = { "model_id", "run_id", "ud_commit", "claim_class" }

-- kwargs win over the front-matter `provenance:` map; Quarto passes absent
-- kwargs as empty strings.
local function field(name, kwargs, record)
  local value = kwargs and stringify(kwargs[name]) or ""
  if value == "" and record then
    value = stringify(record[name])
  end
  return value
end

local function read_fields(kwargs, meta)
  local record = meta and meta["provenance"] or nil
  local fields = {}
  for _, name in ipairs(REQUIRED) do
    local value = field(name, kwargs, record)
    if value == "" then
      error("provenance: missing required field " .. name, 0)
    end
    fields[name] = value
  end
  local path = field("model_path", kwargs, record)
  fields.model_path = path ~= "" and path or nil
  for name, value in pairs(fields) do
    if not VALIDATORS[name].check(value) then
      fail(name, value, VALIDATORS[name].rule)
    end
  end
  return fields
end

local function render_html(f)
  local commit = escape_html(f.ud_commit)
  local model = "<code>" .. escape_html(f.model_id) .. "</code>"
  if f.model_path then
    model = model .. ' (<a href="' .. UD_REPO .. "/blob/" .. commit .. "/"
      .. escape_html(f.model_path) .. '">source</a>)'
  end
  return '<div class="provenance-note figure-provenance" data-claim-class="'
    .. escape_html(f.claim_class) .. '">'
    .. "<strong>Provenance:</strong> "
    .. "UpstreamDrift model " .. model
    .. ", run <code>" .. escape_html(f.run_id) .. "</code>"
    .. ', commit <a href="' .. UD_REPO .. "/commit/" .. commit .. '"><code>'
    .. commit:sub(1, 7) .. "</code></a>"
    .. ", claim class " .. CLAIM_LABELS[f.claim_class] .. "."
    .. "</div>"
end

local function render_text(f)
  return "Provenance: UpstreamDrift model " .. f.model_id .. ", run " .. f.run_id
    .. ", commit " .. f.ud_commit:sub(1, 7) .. ", claim class "
    .. CLAIM_LABELS[f.claim_class] .. "."
end

return {
  ["provenance"] = function(args, kwargs, meta)
    local fields = read_fields(kwargs, meta)
    if quarto and not quarto.doc.is_format("html") then
      return pandoc.Para({ pandoc.Str(render_text(fields)) })
    end
    return pandoc.RawBlock("html", render_html(fields))
  end
}
