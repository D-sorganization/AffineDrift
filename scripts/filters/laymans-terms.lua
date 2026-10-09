-- scripts/filters/laymans-terms.lua
-- Pandoc filter for the shared "In Layman's Terms" component (WEB-01.9 #4494).
--
-- Authoring form (the block's wording lives in a raw HTML fence, unchanged):
--
--   ::: {.laymans-terms}
--   ```{=html}
--   <p class="laymans-terms-intro">...</p>
--   <div class="laymans-item">...</div>
--   ```
--   :::
--
-- Enforces:
-- 1. One component: every page gets the same wrapper, heading and toggle.
-- 2. Open by default: the toggle starts at aria-expanded="true" and the panel
--    at aria-hidden="false", so the block is readable without JavaScript.
--    js/ui-components.js (initLaymansTermsToggle) wires the native <button>,
--    which keeps Enter/Space keyboard activation.
-- 3. Placement: a block authored after the page's "Abstract" heading is moved
--    directly above it.
-- 4. Must run after summary-takeaways.lua, which removes `.laymans-terms`
--    Divs on pages whose front matter supplies a plain-language summary.

local OPEN_HTML = [[<section class="laymans-terms">
<h2><button type="button" class="laymans-terms-header" aria-expanded="true"><span class="laymans-terms-header-title">In Layman's Terms</span><span class="laymans-terms-icon" aria-hidden="true">▼</span></button></h2>
<div class="laymans-terms-content" aria-hidden="false"><div class="laymans-terms-inner">]]

local CLOSE_HTML = [[</div></div>
</section>]]

local function is_lay_div(block)
  return block.t == "Div" and block.classes:includes("laymans-terms")
end

local function is_abstract_header(block)
  return block.t == "Header" and pandoc.utils.stringify(block.content) == "Abstract"
end

-- Return the component's blocks: wrapper open, authored content, wrapper close.
local function render(div)
  local out = { pandoc.RawBlock("html", OPEN_HTML) }
  for _, child in ipairs(div.content) do
    table.insert(out, child)
  end
  table.insert(out, pandoc.RawBlock("html", CLOSE_HTML))
  return out
end

function Pandoc(doc)
  local abstract_idx = nil
  local found = false
  for i, block in ipairs(doc.blocks) do
    if abstract_idx == nil and is_abstract_header(block) then
      abstract_idx = i
    end
    if is_lay_div(block) then
      found = true
    end
  end
  if not found then
    return doc
  end

  local moved = {}
  local blocks = {}
  local abstract_pos = nil
  for i, block in ipairs(doc.blocks) do
    if is_lay_div(block) then
      local target = (abstract_idx ~= nil and i > abstract_idx) and moved or blocks
      for _, b in ipairs(render(block)) do
        table.insert(target, b)
      end
    else
      if i == abstract_idx then
        abstract_pos = #blocks + 1
      end
      table.insert(blocks, block)
    end
  end

  assert(#moved == 0 or abstract_pos ~= nil, "moved lay blocks need an Abstract anchor")
  -- Splice blocks authored below the Abstract heading in directly above it.
  for offset, b in ipairs(moved) do
    table.insert(blocks, abstract_pos + offset - 1, b)
  end
  doc.blocks = blocks
  return doc
end
