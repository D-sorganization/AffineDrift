-- scripts/filters/where-next.lua
-- Pandoc filter for the Standard "Where Next" Footer component (WEB-03.5 #4510).
--
-- Acceptance criteria:
-- 1. No page links to itself (strictly enforced and filtered).
-- 2. Each core page has at least one "simpler" and one "deeper" link.
-- 3. Accessible markup: <nav class="where-next-card" aria-label="Where to go next">, semantic headings, ARIA attributes.
-- 4. Merges with or cleanly supersedes legacy Related Articles sections.

local where_next_cache = nil

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

local function get_filename(p)
  return p:match("([^/\\]+)$") or p
end

local function get_stem(p)
  local fn = get_filename(p)
  return fn:match("^(.-)%.[^%.]+$") or fn
end

local function normalize_path(path_str)
  if path_str == nil then return "" end
  local p = path_str:gsub("\\", "/"):gsub("^%s+", ""):gsub("%s+$", "")
  local project_rel = p:match(".*AffineDrift/(.*)$")
  if project_rel then
    return project_rel:gsub("^/+", "")
  end
  local sub = p:match(".*(articles/.*)$")
    or p:match(".*(pages/.*)$")
    or p:match(".*(books/.*)$")
    or p:match(".*(resources/.*)$")
    or p:match(".*(reports/.*)$")
  if sub then
    return sub
  end
  if p:match("^[A-Za-z]:/") or p:match("^/") then
    return get_filename(p)
  end
  return p:gsub("^%./", ""):gsub("^/+", "")
end

local function get_current_page_rel()
  local input_file = ""
  if PANDOC_STATE and PANDOC_STATE.input_files and #PANDOC_STATE.input_files > 0 then
    input_file = PANDOC_STATE.input_files[1] or ""
  end
  local norm = normalize_path(input_file)
  if norm == "" then
    norm = "index.qmd"
  end
  return norm
end

local function is_self_link(current_norm, target_href)
  if target_href:match("^https?://") or target_href:match("^#") or target_href:match("^mailto:") then
    return false
  end
  local target_clean = target_href:match("^([^#]+)") or target_href
  target_clean = normalize_path(target_clean)

  local target_stem = get_stem(target_clean)
  local curr_stem = get_stem(current_norm)
  local out_stem = ""
  if PANDOC_STATE and PANDOC_STATE.output_file then
    out_stem = get_stem(PANDOC_STATE.output_file)
  end

  if target_stem ~= "" then
    if target_stem == curr_stem or (out_stem ~= "" and target_stem == out_stem) then
      local curr_dir = current_norm:match("^(.*)/[^/]+$") or ""
      local target_dir = target_clean:match("^(.*)/[^/]+$") or ""
      if curr_dir == target_dir or target_dir == "" or curr_dir == "" then
        return true
      end
    end
  end
  return false
end

local function compute_relative_href(from_page, target_href)
  if target_href:match("^https?://") or target_href:match("^#") or target_href:match("^mailto:") then
    return target_href
  end

  if not target_href:match("/") or target_href:match("^%.%./") or target_href:match("^%./") then
    return target_href
  end

  local target_clean = target_href:match("^([^#]+)") or target_href
  local fragment = target_href:match("(#.*)$") or ""
  target_clean = normalize_path(target_clean)

  local from_dir = from_page:match("^(.*)/[^/]+$") or ""
  if from_dir == "" or from_dir == "." then
    return target_clean .. fragment
  end

  local target_dir = target_clean:match("^(.*)/[^/]+$") or ""
  if from_dir == target_dir then
    return get_filename(target_clean) .. fragment
  end

  if target_clean:find(from_dir .. "/", 1, true) == 1 then
    local rel = target_clean:sub(#from_dir + 2)
    return rel .. fragment
  end

  local count = 0
  for _ in from_dir:gmatch("/") do
    count = count + 1
  end
  count = count + 1

  return string.rep("../", count) .. target_clean .. fragment
end

local function load_config_data()
  if where_next_cache ~= nil then
    return where_next_cache
  end

  local f = io.open("config/where_next.yml", "r")
  if not f then
    f = io.open("../config/where_next.yml", "r")
  end
  if not f then
    f = io.open("../../config/where_next.yml", "r")
  end

  if not f then
    where_next_cache = {}
    return where_next_cache
  end

  local content = f:read("*all")
  f:close()

  local parsed = pandoc.read("---\n" .. content .. "\n---\n", "markdown")
  if parsed and parsed.meta then
    where_next_cache = parsed.meta
  else
    where_next_cache = {}
  end
  return where_next_cache
end

function Pandoc(doc)
  local meta = doc.meta
  local current_page = get_current_page_rel()

  -- Check if where-next is explicitly disabled in front matter
  local front_where_next = meta["where-next"]
  if front_where_next == false then
    return doc
  end

  local page_data = nil
  if type(front_where_next) == "table" and front_where_next.t ~= "MetaBool" then
    page_data = front_where_next
  else
    local cfg = load_config_data()
    page_data = cfg[current_page]
    if page_data == nil then
      if current_page:sub(-5) == ".html" then
        page_data = cfg[current_page:sub(1, -6) .. ".qmd"]
      elseif current_page:sub(-4) == ".qmd" then
        page_data = cfg[current_page:sub(1, -5) .. ".html"]
      end
    end
  end

  if page_data == nil or type(page_data) ~= "table" then
    return doc
  end

  local sections_html = {}

  -- 1. Series progression
  local series_prev = page_data["series-prev"]
  local series_next = page_data["series-next"]
  if series_prev or series_next then
    local series_links = {}
    if series_prev and type(series_prev) == "table" then
      local href = stringify(series_prev.href)
      local title = stringify(series_prev.title)
      if href ~= "" and not is_self_link(current_page, href) then
        local rel_href = compute_relative_href(current_page, href)
        table.insert(series_links,
          '<a href="' .. escape_html(rel_href) .. '" class="where-next-link where-next-link--prev">' ..
          '<span class="where-next-direction">&larr; Previous in Series</span>' ..
          '<span class="where-next-link-title">' .. escape_html(title) .. '</span></a>'
        )
      end
    end
    if series_next and type(series_next) == "table" then
      local href = stringify(series_next.href)
      local title = stringify(series_next.title)
      if href ~= "" and not is_self_link(current_page, href) then
        local rel_href = compute_relative_href(current_page, href)
        table.insert(series_links,
          '<a href="' .. escape_html(rel_href) .. '" class="where-next-link where-next-link--next">' ..
          '<span class="where-next-direction">Next in Series &rarr;</span>' ..
          '<span class="where-next-link-title">' .. escape_html(title) .. '</span></a>'
        )
      end
    end
    if #series_links > 0 then
      table.insert(sections_html,
        '<div class="where-next-series" role="group" aria-label="Series progression">\n' ..
        table.concat(series_links, "\n") .. '\n</div>'
      )
    end
  end

  local grid_columns = {}

  local function render_column(column_class, title, icon_entity, items_raw)
    if not items_raw or type(items_raw) ~= "table" then
      return
    end
    local items = items_raw
    if items_raw.t ~= "MetaList" and #items_raw == 0 and items_raw.href then
      items = {items_raw}
    end

    local list_items = {}
    for _, item in ipairs(items) do
      if type(item) == "table" then
        local href = stringify(item.href)
        local item_title = stringify(item.title)
        local blurb = stringify(item.blurb)
        if href ~= "" and not is_self_link(current_page, href) then
          local rel_href = compute_relative_href(current_page, href)
          local blurb_html = ""
          if blurb ~= "" then
            blurb_html = '<p class="where-next-blurb">' .. escape_html(blurb) .. '</p>'
          end
          table.insert(list_items,
            '<li class="where-next-item">' ..
            '<a href="' .. escape_html(rel_href) .. '" class="where-next-item-link">' .. escape_html(item_title) .. '</a>' ..
            blurb_html .. '</li>'
          )
        end
      end
    end

    if #list_items > 0 then
      table.insert(grid_columns,
        '<div class="where-next-column where-next-column--' .. column_class .. '">\n' ..
        '<h3 class="where-next-subtitle"><span class="where-next-icon" aria-hidden="true">' .. icon_entity .. '</span> ' .. escape_html(title) .. '</h3>\n' ..
        '<ul class="where-next-list">\n' .. table.concat(list_items, "\n") .. '\n</ul>\n</div>'
      )
    end
  end

  -- 2. Go Simpler
  render_column("simpler", "Go Simpler", "&#9662;", page_data["simpler"])

  -- 3. Go Deeper
  render_column("deeper", "Go Deeper", "&#9652;", page_data["deeper"])

  -- 4. See the Evidence
  render_column("evidence", "See the Evidence", "&#9745;", page_data["evidence"])

  -- 5. Try It
  render_column("try-it", "Try It", "&#9881;", page_data["try-it"])

  if #grid_columns > 0 then
    table.insert(sections_html,
      '<div class="where-next-grid">\n' .. table.concat(grid_columns, "\n") .. '\n</div>'
    )
  end

  if #sections_html == 0 then
    return doc
  end

  local full_html =
    '<nav class="where-next-card" aria-label="Where to go next">\n' ..
    '  <h2 class="where-next-title unlisted unnumbered">Where Next</h2>\n' ..
    table.concat(sections_html, "\n") .. '\n' ..
    '</nav>'

  -- Suppress legacy ## Related Articles block if present
  local new_blocks = {}
  local skip_legacy = false
  for _, block in ipairs(doc.blocks) do
    if block.t == "Header" and block.level == 2 then
      local h_text = stringify(block.content):lower()
      if h_text:find("related articles") or h_text:find("related theoretical sections") then
        skip_legacy = true
      else
        skip_legacy = false
      end
    elseif block.t == "Header" and block.level <= 2 then
      skip_legacy = false
    end

    if not skip_legacy then
      table.insert(new_blocks, block)
    end
  end

  table.insert(new_blocks, pandoc.RawBlock("html", full_html))
  doc.blocks = new_blocks
  return doc
end
