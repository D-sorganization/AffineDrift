-- scripts/filters/summary-takeaways.lua
-- Pandoc filter for the Plain-Language Summary and Key Takeaways component (WEB-03.3 #4508).
--
-- Enforces:
-- 1. One component driven by front matter (`summary-plain` and `key-takeaways`).
-- 2. Visible without interaction (no collapse / toggle).
-- 3. Merges with legacy lay blocks to prevent double summary boxes.

function Pandoc(doc)
  local meta = doc.meta
  local summary_plain = meta['summary-plain']
  local key_takeaways = meta['key-takeaways']

  local has_summary = false
  if summary_plain ~= nil then
    local str = pandoc.utils.stringify(summary_plain)
    if str:match("%S") then
      has_summary = true
    end
  end

  local has_takeaways = false
  if key_takeaways ~= nil then
    if type(key_takeaways) == "table" and #key_takeaways > 0 then
      has_takeaways = true
    end
  end

  if not has_summary and not has_takeaways then
    return doc
  end

  -- Filter out legacy laymans-terms blocks when front matter is present
  local new_blocks = {}
  local in_legacy_raw = false
  for _, block in ipairs(doc.blocks) do
    local is_legacy = false
    if block.t == "RawBlock" and block.format == "html" then
      if block.text:find("laymans%-terms") then
        is_legacy = true
        if block.text:find("<section[^>]*class=[\"'][^\"']*laymans%-terms") and not block.text:find("</section>") then
          in_legacy_raw = true
        end
      elseif in_legacy_raw then
        is_legacy = true
        if block.text:find("</section>") then
          in_legacy_raw = false
        end
      end
    elseif block.t == "Div" and (block.classes:includes("laymans-terms") or block.identifier == "laymans-terms") then
      is_legacy = true
    elseif in_legacy_raw then
      is_legacy = true
    end

    if not is_legacy then
      table.insert(new_blocks, block)
    end
  end

  -- Build the component card
  local card_content = {}

  if has_summary then
    local summary_title = pandoc.Header(
      2,
      pandoc.Inlines("Plain-Language Summary"),
      pandoc.Attr("", {"summary-plain-title", "unlisted", "unnumbered"})
    )
    local p_inlines = {}
    if type(summary_plain) == "table" and (summary_plain.t == "MetaInlines" or summary_plain.t == "Inlines") then
      p_inlines = pandoc.Inlines(summary_plain)
    else
      p_inlines = pandoc.Inlines(pandoc.utils.stringify(summary_plain))
    end
    local summary_p = pandoc.Para(p_inlines)
    local summary_div = pandoc.Div({summary_title, summary_p}, pandoc.Attr("", {"summary-plain-block"}))
    table.insert(card_content, summary_div)
  end

  if has_takeaways then
    local takeaways_title = pandoc.Header(
      2,
      pandoc.Inlines("Key Takeaways"),
      pandoc.Attr("", {"key-takeaways-title", "unlisted", "unnumbered"})
    )
    local list_items = {}
    for _, item in ipairs(key_takeaways) do
      local item_inlines
      if type(item) == "table" and (item.t == "MetaInlines" or item.t == "Inlines") then
        item_inlines = pandoc.Inlines(item)
      else
        item_inlines = pandoc.Inlines(pandoc.utils.stringify(item))
      end
      table.insert(list_items, {pandoc.Plain(item_inlines)})
    end
    local bullet_list = pandoc.BulletList(list_items)
    local takeaways_div = pandoc.Div({takeaways_title, bullet_list}, pandoc.Attr("", {"key-takeaways-block"}))
    table.insert(card_content, takeaways_div)
  end

  local card_attr = pandoc.Attr("", {"summary-takeaways-card"}, {
    ["role"] = "region",
    ["aria-label"] = "Plain-language summary and key takeaways"
  })
  local card_div = pandoc.Div(card_content, card_attr)

  table.insert(new_blocks, 1, card_div)
  doc.blocks = new_blocks
  return doc
end
