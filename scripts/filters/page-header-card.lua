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
    table.insert(items,
      '    <div class="page-header-item page-header-item--maturity">\n' ..
      '      <dt class="page-header-label">Status</dt>\n' ..
      '      <dd class="page-header-value">\n' ..
      '        <span class="badge badge--maturity badge--' .. escape_html(variant) .. '">' ..
      escape_html(status_str) .. '</span>\n' ..
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
