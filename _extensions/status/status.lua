-- _extensions/status/status.lua
-- Quarto shortcode {{< status [state] [text] [kwargs] >}}
-- Part of WEB-04.2 (#4516) - Unified Status Badge Component

local function stringify(val)
  if val == nil then
    return ""
  end
  return pandoc.utils.stringify(val)
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

-- Normalize state strings and aliases to canonical state
local function normalize_state(raw)
  if raw == nil then return nil end
  local s = stringify(raw):lower():gsub("^%s+", ""):gsub("%s+$", "")
  if s == "" then return nil end

  if s == "available" or s == "avail" or s == "canonical" then
    return "available"
  elseif s == "validated" or s == "valid" or s == "verified" or s == "reviewed" then
    return "validated"
  elseif s == "experimental" or s == "experiment" or s == "exploratory" or s == "draft" then
    return "experimental"
  elseif s == "planned" or s == "scaffold" or s == "scaffolding" or s:match("^in%s*progress") then
    return "planned"
  elseif s == "deprecated" or s == "retired" or s == "archived" or s == "obsolete" then
    return "deprecated"
  elseif s == "opinion" or s == "editorial" or s == "speculative" then
    return "opinion"
  else
    local slug = s:gsub("%s+", "-"):gsub("[^%w%-]", "")
    return slug
  end
end

-- Default labels for canonical states
local CANONICAL_LABELS = {
  ["available"] = "Available",
  ["validated"] = "Validated",
  ["experimental"] = "Experimental",
  ["planned"] = "Planned",
  ["deprecated"] = "Deprecated",
  ["opinion"] = "Opinion"
}

-- Accessible SVG icons (Lucide / Feather style: 24x24 viewBox, stroke=currentColor)
local ICONS = {
  -- checkmark
  ["available"] = '<svg class="status-badge__icon" aria-hidden="true" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>',
  -- shield-check
  ["validated"] = '<svg class="status-badge__icon" aria-hidden="true" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><polyline points="9 12 11 14 15 10"></polyline></svg>',
  -- beaker / flask
  ["experimental"] = '<svg class="status-badge__icon" aria-hidden="true" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 2v7.31L4.1 19.34A2 2 0 0 0 5.8 22h12.4a2 2 0 0 0 1.7-2.66L14 9.31V2"></path><path d="M8.5 2h7"></path><path d="M7 16h10"></path></svg>',
  -- clock
  ["planned"] = '<svg class="status-badge__icon" aria-hidden="true" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>',
  -- ban circle-slash
  ["deprecated"] = '<svg class="status-badge__icon" aria-hidden="true" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"></line></svg>',
  -- message-circle
  ["opinion"] = '<svg class="status-badge__icon" aria-hidden="true" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>'
}

-- Generic fallback icon (info circle)
local FALLBACK_ICON = '<svg class="status-badge__icon" aria-hidden="true" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>'

local function compute_how_to_read_path()
  local input_file = ""
  if quarto and quarto.doc and quarto.doc.input_file then
    input_file = quarto.doc.input_file:gsub("\\", "/")
  elseif PANDOC_STATE and PANDOC_STATE.input_files and #PANDOC_STATE.input_files > 0 then
    input_file = PANDOC_STATE.input_files[1]:gsub("\\", "/")
  end

  -- Check if current file is directly in pages/ directory
  if input_file:match("/pages/[^/]+$") or input_file:match("^pages/[^/]+$") then
    return "how-to-read.html#publication-states"
  end

  -- Check if current file is in a subdirectory of pages/ (e.g. pages/sub/)
  local pages_sub = input_file:match("/pages/(.+)/[^/]+$") or input_file:match("^pages/(.+)/[^/]+$")
  if pages_sub then
    local _, depth = pages_sub:gsub("/", "/")
    return string.rep("../", depth + 1) .. "how-to-read.html#publication-states"
  end

  -- If quarto.project.offset is provided:
  if quarto and quarto.project and quarto.project.offset then
    local off = quarto.project.offset
    if off == "." or off == "" then
      return "pages/how-to-read.html#publication-states"
    else
      return off .. "/pages/how-to-read.html#publication-states"
    end
  end

  -- Fallback if no project offset
  local repo_rel = input_file:match(".*AffineDrift/(.*)$")
  local dir = ""
  if repo_rel then
    dir = repo_rel:match("^(.*)/[^/]+$") or ""
  end
  if dir == "" or dir == "." then
    return "pages/how-to-read.html#publication-states"
  elseif dir == "pages" then
    return "how-to-read.html#publication-states"
  else
    local count = 1
    for _ in dir:gmatch("/") do
      count = count + 1
    end
    return string.rep("../", count) .. "pages/how-to-read.html#publication-states"
  end
end

local function render_badge(state, custom_text, kwargs)
  local canonical = normalize_state(state)
  if not canonical or canonical == "" then
    return ""
  end

  local label = custom_text
  if not label or label == "" then
    label = CANONICAL_LABELS[canonical] or (canonical:sub(1,1):upper() .. canonical:sub(2))
  end

  local icon = ICONS[canonical] or FALLBACK_ICON
  local link_disabled = false
  if kwargs then
    if kwargs.link == false or kwargs.link == "false" or kwargs.href == "none" or kwargs.href == "" then
      link_disabled = true
    end
  end

  local title_attr = escape_html(label) .. " &#8212; Click to Read Publication State Definition"
  local state_class = "status-badge status-badge--" .. escape_html(canonical)
  
  local extra_class = ""
  if kwargs and kwargs["class"] then
    extra_class = stringify(kwargs["class"]):gsub("^%s+", ""):gsub("%s+$", "")
  end
  if extra_class ~= "" then
    state_class = state_class .. " " .. escape_html(extra_class)
  end

  local inner_html = icon .. '<span class="status-badge__text">' .. escape_html(label) .. '</span>'

  if link_disabled then
    return '<span class="' .. state_class .. '" title="' .. title_attr .. '">' .. inner_html .. '</span>'
  end

  local href = nil
  if kwargs and kwargs.href and kwargs.href ~= "" and kwargs.href ~= "true" then
    href = stringify(kwargs.href)
  elseif kwargs and kwargs.link and kwargs.link ~= "" and kwargs.link ~= "true" and kwargs.link ~= true then
    href = stringify(kwargs.link)
  end

  if not href or href == "" then
    href = compute_how_to_read_path()
  end

  return '<a href="' .. escape_html(href) .. '" class="' .. state_class .. '" title="' .. title_attr .. '">' .. inner_html .. '</a>'
end

return {
  ["status"] = function(args, kwargs, meta)
    local state = nil
    local custom_text = nil

    if args and #args > 0 then
      state = stringify(args[1])
      if #args > 1 then
        local arg2 = stringify(args[2]):gsub("^%s+", ""):gsub("%s+$", "")
        if arg2 ~= "" then
          custom_text = arg2
        end
      end
    end

    if not state or state == "" then
      if kwargs and (kwargs.state or kwargs.status or kwargs.maturity) then
        state = stringify(kwargs.state or kwargs.status or kwargs.maturity)
      end
    end

    if (not state or state == "") and meta then
      local meta_status = meta["status"] or meta["maturity"] or meta["publication-state"]
      if meta_status then
        state = stringify(meta_status)
      end
    end

    if kwargs and kwargs.text then
      local kw_text = stringify(kwargs.text):gsub("^%s+", ""):gsub("%s+$", "")
      if kw_text ~= "" then
        custom_text = kw_text
      end
    end

    if not state or state == "" then
      return pandoc.Null()
    end

    local html = render_badge(state, custom_text, kwargs)
    return pandoc.RawInline("html", html)
  end
}
