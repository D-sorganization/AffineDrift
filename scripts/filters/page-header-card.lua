-- scripts/filters/page-header-card.lua
-- Pandoc filter for the Page Header Card component (WEB-03.2 #4507).
--
-- Renders metadata from front matter:
-- - maturity / status badge
-- - audience level badge
-- - estimated reading time (explicitly labelled "estimate")
-- - prerequisites
-- - first published and last reviewed dates
-- - "Cite this page" link (WEB-07.2)
--
-- All markup is accessible: a semantic <dl> with <dt> and <dd> pairs,
-- and text-carrying badges.

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
    return s:gsub("%s+", "-"):gsub("[^%w%-]", "")
  end
end

local ICONS = {
  ["available"] = '<svg class="status-badge__icon" aria-hidden="true" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>',
  ["validated"] = '<svg class="status-badge__icon" aria-hidden="true" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><polyline points="9 12 11 14 15 10"></polyline></svg>',
  ["experimental"] = '<svg class="status-badge__icon" aria-hidden="true" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 2v7.31L4.1 19.34A2 2 0 0 0 5.8 22h12.4a2 2 0 0 0 1.7-2.66L14 9.31V2"></path><path d="M8.5 2h7"></path><path d="M7 16h10"></path></svg>',
  ["planned"] = '<svg class="status-badge__icon" aria-hidden="true" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>',
  ["deprecated"] = '<svg class="status-badge__icon" aria-hidden="true" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"></line></svg>',
  ["opinion"] = '<svg class="status-badge__icon" aria-hidden="true" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>'
}

local function compute_how_to_read_path()
  local input_file = ""
  if PANDOC_STATE and PANDOC_STATE.input_files and #PANDOC_STATE.input_files > 0 then
    input_file = PANDOC_STATE.input_files[1] or ""
  end

  input_file = input_file:gsub("\\", "/")
  local repo_rel = input_file:match(".*AffineDrift/(.*)$")
  if repo_rel then
    input_file = repo_rel
  end

  local dir = input_file:match("^(.*)/[^/]+$") or ""
  if dir == "" or dir == "." then
    return "pages/how-to-read.html#publication-states"
  end
  if dir == "pages" then
    return "how-to-read.html#publication-states"
  end
  if dir:match("^pages/") then
    local _, count = dir:gsub("/", "/")
    return string.rep("../", count) .. "how-to-read.html#publication-states"
  end

  dir = dir:gsub("^[A-Za-z]:/", ""):gsub("^%./", "")
  local count = 1
  for _ in dir:gmatch("/") do
    count = count + 1
  end
  return string.rep("../", count) .. "pages/how-to-read.html#publication-states"
end

function Pandoc(doc)
  local meta = doc.meta

  -- 1. Status / Maturity
  local status_raw = meta["status"] or meta["maturity"]
  local status_str = stringify(status_raw)
  local has_status = status_str:match("%S") ~= nil

  -- 2. Audience Level
  local audience_raw = meta["audience"] or meta["audience-level"]
  local audience_str = stringify(audience_raw)
  local has_audience = audience_str:match("%S") ~= nil

  -- 3. Reading Time
  local reading_time_raw = meta["reading-time"] or meta["estimated-reading-time"]
  local reading_time_str = stringify(reading_time_raw)
  local has_reading_time = reading_time_str:match("%S") ~= nil

  -- 4. Dates
  local published_raw = meta["date"] or meta["published"] or meta["date-published"]
  local published_str = stringify(published_raw)
  local has_published = published_str:match("%S") ~= nil

  local reviewed_raw = meta["last-reviewed"] or meta["date-modified"] or meta["reviewed"]
  local reviewed_str = stringify(reviewed_raw)
  local has_reviewed = reviewed_str:match("%S") ~= nil

  -- 5. Prerequisites
  local prereqs_raw = meta["prerequisites"]
  local has_prereqs = false
  local prereqs_list = {}
  if prereqs_raw ~= nil then
    if type(prereqs_raw) == "table" and prereqs_raw.t == "MetaList" then
      for _, item in ipairs(prereqs_raw) do
        local s = stringify(item)
        if s:match("%S") then
          table.insert(prereqs_list, s)
        end
      end
      if #prereqs_list > 0 then
        has_prereqs = true
      end
    else
      local s = stringify(prereqs_raw)
      if s:match("%S") then
        table.insert(prereqs_list, s)
        has_prereqs = true
      end
    end
  end

  -- 6. Citation
  local cite_raw = meta["citation"] or meta["cite-this-page"] or meta["cite-link"]
  local has_cite = false
  local cite_href = "#citation"
  if cite_raw ~= nil then
    if type(cite_raw) == "boolean" then
      has_cite = cite_raw
    elseif type(cite_raw) == "table" then
      if cite_raw.t == "MetaBool" then
        if cite_raw[1] == true or cite_raw.value == true or tostring(cite_raw[1]) == "true" then
          has_cite = true
        end
      else
        has_cite = true
      end
    else
      local s = stringify(cite_raw)
      if s == "true" then
        has_cite = true
      elseif s:match("^#") or s:match("^https?://") or s:match("^/") then
        has_cite = true
        cite_href = s
      elseif s:match("%S") and s ~= "false" then
        has_cite = true
      end
    end
  end

  -- If no relevant front matter exists, do nothing
  if not (has_status or has_audience or has_reading_time or has_published or has_reviewed or has_prereqs or has_cite) then
    return doc
  end

  local items = {}

  if has_status then
    local variant = status_str:lower():gsub("%s+", "-"):gsub("[^%w%-]", "")
    local canonical = normalize_state(status_str) or variant
    local icon = ICONS[canonical] or ""
    local href = compute_how_to_read_path()
    local title_attr = escape_html(status_str .. " — Click to Read Publication State Definition")
    table.insert(items,
      '    <div class="page-header-item page-header-item--maturity">\n' ..
      '      <dt class="page-header-label">Status</dt>\n' ..
      '      <dd class="page-header-value">\n' ..
      '        <a href="' .. escape_html(href) .. '" class="badge badge--maturity status-badge status-badge--' .. escape_html(canonical) .. ' badge--' .. escape_html(variant) .. '" title="' .. title_attr .. '">' ..
      icon .. '<span class="status-badge__text">' .. escape_html(status_str) .. '</span></a>\n' ..
      '      </dd>\n' ..
      '    </div>'
    )
  end

  if has_audience then
    local variant = audience_str:lower():gsub("%s+", "-"):gsub("[^%w%-]", "")
    table.insert(items,
      '    <div class="page-header-item page-header-item--audience">\n' ..
      '      <dt class="page-header-label">Audience</dt>\n' ..
      '      <dd class="page-header-value">\n' ..
      '        <span class="badge badge--audience badge--' .. escape_html(variant) .. '">' ..
      escape_html(audience_str) .. '</span>\n' ..
      '      </dd>\n' ..
      '    </div>'
    )
  end

  if has_reading_time then
    local rt_display = reading_time_str
    if not rt_display:lower():match("estimate") then
      if not rt_display:lower():match("min") then
        rt_display = rt_display .. " min read (estimate)"
      else
        rt_display = rt_display .. " (estimate)"
      end
    end
    table.insert(items,
      '    <div class="page-header-item page-header-item--reading-time">\n' ..
      '      <dt class="page-header-label">Reading Time</dt>\n' ..
      '      <dd class="page-header-value">\n' ..
      '        <span class="reading-time-text">' .. escape_html(rt_display) .. '</span>\n' ..
      '      </dd>\n' ..
      '    </div>'
    )
  end

  if has_published then
    table.insert(items,
      '    <div class="page-header-item page-header-item--published">\n' ..
      '      <dt class="page-header-label">Published</dt>\n' ..
      '      <dd class="page-header-value">\n' ..
      '        <time datetime="' .. escape_html(published_str) .. '">' .. escape_html(published_str) .. '</time>\n' ..
      '      </dd>\n' ..
      '    </div>'
    )
  end

  if has_reviewed then
    table.insert(items,
      '    <div class="page-header-item page-header-item--reviewed">\n' ..
      '      <dt class="page-header-label">Last Reviewed</dt>\n' ..
      '      <dd class="page-header-value">\n' ..
      '        <time datetime="' .. escape_html(reviewed_str) .. '">' .. escape_html(reviewed_str) .. '</time>\n' ..
      '      </dd>\n' ..
      '    </div>'
    )
  end

  if has_prereqs then
    local prereq_content = ""
    if #prereqs_list == 1 then
      prereq_content = '<span class="page-header-prereq-item">' .. escape_html(prereqs_list[1]) .. '</span>'
    else
      prereq_content = '<ul class="page-header-prereq-list">\n'
      for _, p in ipairs(prereqs_list) do
        prereq_content = prereq_content .. '          <li>' .. escape_html(p) .. '</li>\n'
      end
      prereq_content = prereq_content .. '        </ul>'
    end
    table.insert(items,
      '    <div class="page-header-item page-header-item--prerequisites">\n' ..
      '      <dt class="page-header-label">Prerequisites</dt>\n' ..
      '      <dd class="page-header-value">\n' ..
      '        ' .. prereq_content .. '\n' ..
      '      </dd>\n' ..
      '    </div>'
    )
  end

  if has_cite then
    table.insert(items,
      '    <div class="page-header-item page-header-item--citation">\n' ..
      '      <dt class="page-header-label">Citation</dt>\n' ..
      '      <dd class="page-header-value">\n' ..
      '        <a href="' .. escape_html(cite_href) .. '" class="page-header-cite-link">Cite this page</a>\n' ..
      '      </dd>\n' ..
      '    </div>'
    )
  end

  local html = '<header class="page-header-card" role="region" aria-label="Page metadata">\n' ..
               '  <dl class="page-header-metadata">\n' ..
               table.concat(items, "\n") .. '\n' ..
               '  </dl>\n' ..
               '</header>'

  local card_block = pandoc.RawBlock("html", html)
  table.insert(doc.blocks, 1, card_block)
  return doc
end
