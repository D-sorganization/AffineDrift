-- Page metadata is rendered once; prerequisites use canonical source titles.
local directory = pandoc.path.directory(PANDOC_SCRIPT_FILE)
local ui = dofile(directory .. "/page-header-utils.lua")
local prerequisites = dofile(directory .. "/page-header-prerequisites.lua")
local stringify, escape_html = ui.stringify, ui.escape_html

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


local function badge_item(meta, key, label)
  local raw = meta.audience or meta["audience-level"]
  if key == "maturity" then raw = meta.status or meta.maturity end
  local text = stringify(raw)
  if text == "" then return nil end
  local variant = text:lower():gsub("%s+", "-"):gsub("[^%w%-]", "")
  local badge = '<span class="badge badge--audience badge--' .. variant .. '">' .. escape_html(text) .. '</span>'
  if key == "maturity" then
    local state = normalize_state(text)
    badge = '<a href="/pages/how-to-read.html#publication-states" class="badge badge--maturity status-badge status-badge--' ..
      state .. ' badge--' .. variant .. '" title="Read Publication State Definition">' ..
      (ICONS[state] or "") .. '<span class="status-badge__text">' .. escape_html(text) .. '</span></a>'
  end
  return ui.item(key, label, badge)
end

local function reading_time_item(meta)
  local text = stringify(meta["reading-time"] or meta["estimated-reading-time"])
  if text == "" then return nil end
  if not text:lower():match("estimate") then
    if not text:lower():match("min") then text = text .. " min read" end
    text = text .. " (estimate)"
  end
  return ui.item("reading-time", "Reading Time", '<span class="reading-time-text">' .. escape_html(text) .. '</span>')
end

local function date_item(meta, reviewed)
  -- Quarto's title already owns `date`; retain dates supplied only to this card.
  if not reviewed and meta.date ~= nil then return nil end
  local raw = meta.published or meta["date-published"]
  if reviewed then raw = meta["last-reviewed"] or meta["date-modified"] or meta.reviewed end
  local text = stringify(raw)
  if text == "" then return nil end
  local content = '<span class="date-unverified">Publication date not verified</span>'
  local unverified = not reviewed and stringify(meta["date-source"]):lower() == "unverified"
  if not unverified and text:match("^%d%d%d%d%-%d%d%-%d%d$") then
    content = '<time datetime="' .. text .. '">' .. text .. '</time>'
  elseif reviewed then
    -- Quarto may already have formatted date-modified for human readers.
    content = '<span>' .. escape_html(text) .. '</span>'
  end
  return ui.item(reviewed and "reviewed" or "published", reviewed and "Last Reviewed" or "Published", content)
end

local function citation_link(meta)
  local raw = meta.citation or meta["cite-this-page"] or meta["cite-link"]
  if raw == nil or raw == false or stringify(raw) == "false" then return nil end
  local target = stringify(raw)
  if not ui.safe_href(target) then target = "#citation" end
  return '<a href="' .. escape_html(target) .. '" class="page-header-cite-link">Cite this page</a>'
end

local function metadata_items(meta)
  local items = {}
  local function add(value)
    if value then table.insert(items, value) end
  end
  add(badge_item(meta, "maturity", "Status"))
  add(badge_item(meta, "audience", "Audience"))
  add(reading_time_item(meta))
  add(date_item(meta, false))
  add(date_item(meta, true))
  local prereqs = prerequisites.render(meta.prerequisites, ui)
  if prereqs then add(ui.item("prerequisites", "Prerequisites", prereqs)) end
  return items
end

function Pandoc(doc)
  local items = metadata_items(doc.meta)
  local cite = citation_link(doc.meta)
  if #items == 0 then
    if cite then table.insert(doc.blocks, pandoc.RawBlock("html", '<p class="page-citation-link">' .. cite .. '</p>')) end
    return doc
  end
  if cite then table.insert(items, ui.item("citation", "Citation", cite)) end
  local html = '<header class="page-header-card" role="region" aria-label="Page metadata">' ..
    '<dl class="page-header-metadata">' .. table.concat(items, "\n") .. '</dl></header>'
  table.insert(doc.blocks, 1, pandoc.RawBlock("html", html))
  return doc
end
