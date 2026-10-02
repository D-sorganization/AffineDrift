-- scripts/filters/caveats-block.lua
-- Pandoc filter for the Standard "What This Shows / What It Does Not Show" Caveat Block (WEB-03.4 #4509).
--
-- Enforces:
-- 1. Generated from front matter (`caveats`).
-- 2. Structured sections:
--    - What This Page Establishes (with explicit Evidence Level)
--    - What This Page Does Not Establish
--    - Open Critiques and Active Inquiries (optional)
--    - Next Validation Gate (optional)
-- 3. Accessible container with ARIA region role and label.
-- 4. Clean insertion after executive summary / summary-takeaways block.
-- 5. Deduplication: suppresses legacy duplicate Scope & Exclusions / Attribution Boundary blocks.

local EVIDENCE_LEVEL_MAP = {
  ["mathematical-identity"] = "Theory (Mathematical Identity)",
  ["mathematical_identity"] = "Theory (Mathematical Identity)",
  ["manufactured-fixture"] = "Simulation (Manufactured Fixture)",
  ["manufactured_synthetic"] = "Simulation (Manufactured Synthetic)",
  ["qualified-simulation"] = "Simulation (Qualified Multi-Body)",
  ["qualified_simulation"] = "Simulation (Qualified Multi-Body)",
  ["measured-participant-result"] = "Empirical (Measured Human Data)",
  ["pilot_bounded"] = "Empirical (Pilot Study)",
  ["governed_dataset"] = "Empirical (Governed Dataset)",
  ["collecting_locked"] = "Empirical (Collecting Locked)",
  ["replicated-result"] = "Replicated Result",
  ["bounded-application"] = "Bounded Application",
  ["validated_evidence"] = "Validated Evidence",
  ["published_claim"] = "Published Claim"
}

local function stringify(val)
  if val == nil then return "" end
  return pandoc.utils.stringify(val)
end

local function format_evidence_level(meta_caveats, meta_rung)
  if meta_caveats ~= nil and meta_caveats["evidence-level"] ~= nil then
    local s = stringify(meta_caveats["evidence-level"]):gsub("^%s+", ""):gsub("%s+$", "")
    if s ~= "" then return s end
  end
  if meta_rung ~= nil then
    local r = stringify(meta_rung):gsub("^%s+", ""):gsub("%s+$", ""):lower()
    if EVIDENCE_LEVEL_MAP[r] ~= nil then
      return EVIDENCE_LEVEL_MAP[r]
    end
  end
  return "Theory"
end

function Pandoc(doc)
  local meta = doc.meta
  local caveats = meta["caveats"]
  if caveats == nil or type(caveats) ~= "table" then
    return doc
  end

  local establishes = caveats["establishes"]
  local does_not = caveats["does-not-establish"]
  if establishes == nil and does_not == nil then
    return doc
  end

  -- Check if a caveats card is already in the document AST
  for _, block in ipairs(doc.blocks) do
    if block.t == "Div" and (block.classes:includes("caveats-card") or block.classes:includes("what-this-shows-card")) then
      return doc
    end
  end

  -- Filter out legacy duplicate Scope & Exclusions and Attribution Boundary blocks
  local new_blocks = {}
  for _, block in ipairs(doc.blocks) do
    local is_legacy = false
    if block.t == "Div" and (block.classes:includes("callout-note") or block.classes:includes("callout-important")) then
      local block_text = stringify(block):lower()
      if block_text:find("scope & exclusions") or block_text:find("model%-conditioned attribution boundary") then
        is_legacy = true
      end
    end
    if not is_legacy then
      table.insert(new_blocks, block)
    end
  end

  -- Build component card
  local card_content = {}

  -- Main Title
  local main_title = pandoc.Header(
    2,
    pandoc.Inlines("What This Shows / What It Does Not Show"),
    pandoc.Attr("", {"caveats-title", "unlisted", "unnumbered"})
  )
  table.insert(card_content, main_title)

  -- Section 1: Establishes
  if establishes ~= nil and type(establishes) == "table" and #establishes > 0 then
    local evidence_level = format_evidence_level(caveats, meta["evidence-rung"])
    local est_heading = pandoc.Header(
      3,
      pandoc.Inlines("What This Page Establishes (Evidence Level: " .. evidence_level .. ")"),
      pandoc.Attr("", {"caveats-subtitle", "caveats-establishes-title", "unlisted", "unnumbered"})
    )
    local est_items = {}
    for _, item in ipairs(establishes) do
      local item_inlines
      if type(item) == "table" and (item.t == "MetaInlines" or item.t == "Inlines") then
        item_inlines = pandoc.Inlines(item)
      else
        item_inlines = pandoc.Inlines(stringify(item))
      end
      table.insert(est_items, {pandoc.Plain(item_inlines)})
    end
    local est_list = pandoc.BulletList(est_items)
    local est_div = pandoc.Div({est_heading, est_list}, pandoc.Attr("", {"caveats-section", "caveats-establishes"}))
    table.insert(card_content, est_div)
  end

  -- Section 2: Does Not Establish
  if does_not ~= nil and type(does_not) == "table" and #does_not > 0 then
    local dn_heading = pandoc.Header(
      3,
      pandoc.Inlines("What This Page Does Not Establish"),
      pandoc.Attr("", {"caveats-subtitle", "caveats-does-not-establish-title", "unlisted", "unnumbered"})
    )
    local dn_items = {}
    for _, item in ipairs(does_not) do
      local item_inlines
      if type(item) == "table" and (item.t == "MetaInlines" or item.t == "Inlines") then
        item_inlines = pandoc.Inlines(item)
      else
        item_inlines = pandoc.Inlines(stringify(item))
      end
      table.insert(dn_items, {pandoc.Plain(item_inlines)})
    end
    local dn_list = pandoc.BulletList(dn_items)
    local dn_div = pandoc.Div({dn_heading, dn_list}, pandoc.Attr("", {"caveats-section", "caveats-does-not-establish"}))
    table.insert(card_content, dn_div)
  end

  -- Section 3: Open Critiques (optional)
  local critiques = caveats["open-critiques"]
  if critiques ~= nil and type(critiques) == "table" and #critiques > 0 then
    local crit_heading = pandoc.Header(
      3,
      pandoc.Inlines("Open Critiques and Active Inquiries"),
      pandoc.Attr("", {"caveats-subtitle", "caveats-critiques-title", "unlisted", "unnumbered"})
    )
    local crit_items = {}
    for _, item in ipairs(critiques) do
      local item_inlines
      if type(item) == "table" and (item.t == "MetaInlines" or item.t == "Inlines") then
        item_inlines = pandoc.Inlines(item)
      else
        item_inlines = pandoc.Inlines(stringify(item))
      end
      table.insert(crit_items, {pandoc.Plain(item_inlines)})
    end
    local crit_list = pandoc.BulletList(crit_items)
    local crit_div = pandoc.Div({crit_heading, crit_list}, pandoc.Attr("", {"caveats-section", "caveats-critiques"}))
    table.insert(card_content, crit_div)
  end

  -- Section 4: Next Validation Gate (optional)
  local next_gate = caveats["next-gate"]
  if next_gate ~= nil then
    local gate_str = stringify(next_gate):gsub("^%s+", ""):gsub("%s+$", "")
    if gate_str ~= "" then
      local gate_heading = pandoc.Header(
        3,
        pandoc.Inlines("Next Validation Gate"),
        pandoc.Attr("", {"caveats-subtitle", "caveats-gate-title", "unlisted", "unnumbered"})
      )
      local gate_p = pandoc.Para(pandoc.Inlines(gate_str))
      local gate_div = pandoc.Div({gate_heading, gate_p}, pandoc.Attr("", {"caveats-section", "caveats-next-gate"}))
      table.insert(card_content, gate_div)
    end
  end

  local card_attr = pandoc.Attr("", {
    "callout",
    "callout-style-simple",
    "callout-note",
    "no-icon",
    "caveats-card",
    "what-this-shows-card"
  }, {
    ["role"] = "region",
    ["aria-label"] = "What This Shows / What It Does Not Show"
  })
  local card_div = pandoc.Div(card_content, card_attr)

  -- Insertion position: after summary-takeaways-card if present, otherwise at index 1
  local insert_idx = 1
  for i, block in ipairs(new_blocks) do
    if block.t == "Div" and block.classes:includes("summary-takeaways-card") then
      insert_idx = i + 1
      break
    end
  end

  table.insert(new_blocks, insert_idx, card_div)
  doc.blocks = new_blocks
  return doc
end
