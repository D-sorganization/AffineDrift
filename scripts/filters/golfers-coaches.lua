-- scripts/filters/golfers-coaches.lua
-- Pandoc filter for the "What This Means for Golfers and Coaches" Box, With Guardrails (WEB-03.7 #4512).
--
-- Enforces:
-- 1. Driven by front matter (`golfers-coaches`) OR authored via `::: {.golfers-coaches}` Div.
-- 2. Carries the evidence-rung badge linking to the evidence ladder.
-- 3. Enforces the mandatory Simulation-to-Human Epistemic Guardrail.
-- 4. Accessible aside container with role="note" and aria-label="What This Means for Golfers and Coaches".
-- 5. Standard structured sections: Title, Evidence Rung, Conceptual Takeaway, Epistemic Guardrail, Questions to Explore With a Coach.

local MANDATORY_GUARDRAIL = "Simulation-to-Human Guardrail: This section translates a mathematical or multibody simulation insight into coaching concepts. It does not measure live human muscle activation (EMG) or prescribe individual swing changes."

local EVIDENCE_RUNG_MAP = {
  ["mathematical-identity"] = { category = "Theory", label = "Theory (Mathematical Identity)", badge_class = "badge-math-identity" },
  ["mathematical_identity"] = { category = "Theory", label = "Theory (Mathematical Identity)", badge_class = "badge-math-identity" },
  ["manufactured-fixture"] = { category = "Simulation", label = "Simulation (Manufactured Fixture)", badge_class = "badge-manufactured-synthetic" },
  ["manufactured_synthetic"] = { category = "Simulation", label = "Simulation (Manufactured Synthetic)", badge_class = "badge-manufactured-synthetic" },
  ["qualified-simulation"] = { category = "Simulation", label = "Simulation (Qualified Multi-Body)", badge_class = "badge-qualified-simulation" },
  ["qualified_simulation"] = { category = "Simulation", label = "Simulation (Qualified Multi-Body)", badge_class = "badge-qualified-simulation" },
  ["measured-participant-result"] = { category = "Human", label = "Empirical (Measured Human Data)", badge_class = "badge-pilot-bounded" },
  ["pilot_bounded"] = { category = "Human", label = "Empirical (Pilot Study)", badge_class = "badge-pilot-bounded" },
  ["governed_dataset"] = { category = "Bench", label = "Bench (Governed Dataset)", badge_class = "badge-governed-dataset" },
  ["collecting_locked"] = { category = "Bench", label = "Bench (Collecting Locked)", badge_class = "badge-collecting-locked" },
  ["replicated-result"] = { category = "Human", label = "Human (Replicated Result)", badge_class = "badge-validated-evidence" },
  ["bounded-application"] = { category = "Human", label = "Human (Bounded Application)", badge_class = "badge-published-claim" },
  ["validated_evidence"] = { category = "Human", label = "Validated Evidence", badge_class = "badge-validated-evidence" },
  ["published_claim"] = { category = "Human", label = "Published Claim", badge_class = "badge-published-claim" }
}

local function stringify(val)
  if val == nil then return "" end
  return pandoc.utils.stringify(val)
end

local function escape_html(str)
  if str == nil then return "" end
  local map = {
    ["&"] = "&amp;",
    ["<"] = "&lt;",
    [">"] = "&gt;",
    ['"'] = "&quot;",
    ["'"] = "&#39;"
  }
  return (str:gsub("[&<>'\"']", map))
end

local function resolve_evidence_rung(meta_rung)
  if meta_rung ~= nil then
    local r = stringify(meta_rung):gsub("^%s+", ""):gsub("%s+$", ""):lower()
    if EVIDENCE_RUNG_MAP[r] ~= nil then
      return EVIDENCE_RUNG_MAP[r]
    end
    if r:find("math") or r:find("theory") or r:find("identity") then
      return { category = "Theory", label = "Theory", badge_class = "badge-math-identity" }
    elseif r:find("sim") or r:find("fixture") then
      return { category = "Simulation", label = "Simulation", badge_class = "badge-qualified-simulation" }
    elseif r:find("bench") or r:find("dataset") then
      return { category = "Bench", label = "Bench", badge_class = "badge-governed-dataset" }
    elseif r:find("human") or r:find("participant") or r:find("pilot") or r:find("replicated") then
      return { category = "Human", label = "Human", badge_class = "badge-pilot-bounded" }
    end
  end
  return { category = "Theory", label = "Theory", badge_class = "badge-math-identity" }
end

local function card_insert_index(blocks)
  for i, block in ipairs(blocks) do
    if block.t == "Div" and (block.classes:includes("caveats-card") or block.classes:includes("what-this-shows-card")) then
      return i + 1
    end
  end
  for i, block in ipairs(blocks) do
    if block.t == "Div" and block.classes:includes("summary-takeaways-card") then
      return i + 1
    end
  end
  for i, block in ipairs(blocks) do
    if block.t == "RawBlock" and block.format == "html" and block.text:find("<h1[%s>]") then
      return i + 1
    end
  end
  return 1
end

local function build_box_blocks(box_data, meta)
  local blocks = {}

  -- Accessible container open
  table.insert(blocks, pandoc.RawBlock(
    "html",
    '<aside class="golfers-coaches-box" role="note" aria-label="What This Means for Golfers and Coaches">'
  ))

  -- Title Case Heading
  local main_title = pandoc.Header(
    2,
    pandoc.Inlines("What This Means for Golfers and Coaches"),
    pandoc.Attr("", {"golfers-coaches-title", "unlisted", "unnumbered"})
  )
  table.insert(blocks, main_title)

  -- Evidence Rung Badge
  local rung_info = resolve_evidence_rung(meta and meta["evidence-rung"] or nil)
  local badge_html = string.format(
    '<div class="golfers-coaches-badge">' ..
    '<a href="/pages/how-to-read.html#evidence-ladder" class="badge evidence-badge %s" title="Read Evidence Ladder Definition">' ..
    '<span class="evidence-badge__category">%s</span>: <span class="evidence-badge__label">%s</span>' ..
    '</a></div>',
    escape_html(rung_info.badge_class),
    escape_html(rung_info.category),
    escape_html(rung_info.label)
  )
  table.insert(blocks, pandoc.RawBlock("html", badge_html))

  -- Conceptual Takeaway
  local takeaway_title = pandoc.Header(
    3,
    pandoc.Inlines("Conceptual Takeaway"),
    pandoc.Attr("", {"golfers-coaches-takeaway-title", "unlisted", "unnumbered"})
  )
  table.insert(blocks, takeaway_title)

  if box_data.takeaway_blocks and #box_data.takeaway_blocks > 0 then
    for _, b in ipairs(box_data.takeaway_blocks) do
      table.insert(blocks, b)
    end
  elseif box_data.takeaway ~= nil then
    local inlines
    if type(box_data.takeaway) == "table" and (box_data.takeaway.t == "MetaInlines" or box_data.takeaway.t == "Inlines") then
      inlines = pandoc.Inlines(box_data.takeaway)
    else
      inlines = pandoc.Inlines(stringify(box_data.takeaway))
    end
    table.insert(blocks, pandoc.Para(inlines))
  end

  -- Simulation-to-Human Epistemic Guardrail
  local guardrail_title = pandoc.Header(
    3,
    pandoc.Inlines("Simulation-to-Human Guardrail"),
    pandoc.Attr("", {"golfers-coaches-guardrail-title", "unlisted", "unnumbered"})
  )
  table.insert(blocks, guardrail_title)

  local guardrail_text = MANDATORY_GUARDRAIL
  if box_data.guardrail ~= nil then
    local custom = stringify(box_data.guardrail):gsub("^%s+", ""):gsub("%s+$", "")
    if custom ~= "" and not custom:find("Simulation%-to%-Human Guardrail") then
      guardrail_text = MANDATORY_GUARDRAIL .. " " .. custom
    elseif custom ~= "" then
      guardrail_text = custom
    end
  end
  table.insert(blocks, pandoc.Para(pandoc.Inlines(guardrail_text)))

  -- Questions to Explore with a Coach
  if box_data.questions ~= nil and #box_data.questions > 0 then
    local questions_title = pandoc.Header(
      3,
      pandoc.Inlines("Questions to Explore With a Coach"),
      pandoc.Attr("", {"golfers-coaches-questions-title", "unlisted", "unnumbered"})
    )
    table.insert(blocks, questions_title)

    local q_items = {}
    for _, q in ipairs(box_data.questions) do
      local q_inlines
      if type(q) == "table" and (q.t == "MetaInlines" or q.t == "Inlines") then
        q_inlines = pandoc.Inlines(q)
      elseif type(q) == "table" and (q.t == "Plain" or q.t == "Para") then
        q_inlines = q.content
      else
        q_inlines = pandoc.Inlines(stringify(q))
      end
      table.insert(q_items, {pandoc.Plain(q_inlines)})
    end
    table.insert(blocks, pandoc.BulletList(q_items))
  end

  -- Accessible container close
  table.insert(blocks, pandoc.RawBlock("html", '</aside>'))

  return blocks
end

function Pandoc(doc)
  local meta = doc.meta
  local meta_gc = meta["golfers-coaches"]
  local meta_data = nil

  if meta_gc ~= nil and type(meta_gc) == "table" then
    meta_data = {
      takeaway = meta_gc["takeaway"] or meta_gc["summary"],
      guardrail = meta_gc["guardrail"],
      questions = meta_gc["questions"]
    }
  end

  -- First, check if there is an explicit ::: {.golfers-coaches} Div in the AST
  local has_div = false
  local new_blocks = {}
  for _, block in ipairs(doc.blocks) do
    if block.t == "Div" and block.classes:includes("golfers-coaches") then
      has_div = true
      local div_data = {
        takeaway_blocks = {},
        questions = {},
        guardrail = nil
      }

      -- Attributes on Div take priority if present
      if block.attributes["takeaway"] then
        div_data.takeaway = block.attributes["takeaway"]
      end
      if block.attributes["guardrail"] then
        div_data.guardrail = block.attributes["guardrail"]
      end

      -- Scan child blocks
      for _, child in ipairs(block.content) do
        if child.t == "BulletList" then
          for _, item in ipairs(child.content) do
            if #item > 0 then
              table.insert(div_data.questions, item[1])
            end
          end
        elseif child.t == "Para" or child.t == "Plain" then
          local p_text = stringify(child)
          if p_text:find("Guardrail:") then
            div_data.guardrail = p_text
          else
            table.insert(div_data.takeaway_blocks, child)
          end
        else
          table.insert(div_data.takeaway_blocks, child)
        end
      end

      -- If Div had no takeaway or questions, fall back to front matter if present
      if #div_data.takeaway_blocks == 0 and not div_data.takeaway and meta_data and meta_data.takeaway then
        div_data.takeaway = meta_data.takeaway
      end
      if #div_data.questions == 0 and meta_data and meta_data.questions then
        div_data.questions = meta_data.questions
      end
      if not div_data.guardrail and meta_data and meta_data.guardrail then
        div_data.guardrail = meta_data.guardrail
      end

      local box_elements = build_box_blocks(div_data, meta)
      for _, elem in ipairs(box_elements) do
        table.insert(new_blocks, elem)
      end
    else
      table.insert(new_blocks, block)
    end
  end

  if has_div then
    doc.blocks = new_blocks
    return doc
  end

  -- If no Div, but front matter is present, insert box from front matter
  if meta_data ~= nil and (meta_data.takeaway ~= nil or meta_data.questions ~= nil) then
    -- Check if box is already present to prevent duplicate
    for _, block in ipairs(new_blocks) do
      if block.t == "RawBlock" and block.format == "html" and block.text:find("golfers%-coaches%-box") then
        return doc
      end
      if block.t == "Div" and block.classes:includes("golfers-coaches-box") then
        return doc
      end
    end

    local box_elements = build_box_blocks(meta_data, meta)
    local idx = card_insert_index(new_blocks)
    for i, elem in ipairs(box_elements) do
      table.insert(new_blocks, idx + i - 1, elem)
    end
    doc.blocks = new_blocks
    return doc
  end

  return doc
end
