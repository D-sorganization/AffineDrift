-- scripts/filters/revision-history.lua
-- Pandoc filter for the Per-Article Revision History component (WEB-07.3 #4545).
--
-- Renders front-matter `changes` as an accessible <div id="revision-history"> block
-- before references or at the end of the document.

function Pandoc(doc)
  local changes = doc.meta.changes
  if not changes then
    return doc
  end

  if type(changes) ~= "table" or #changes == 0 then
    return doc
  end

  -- Build list of changes
  local items = {}
  for _, item in ipairs(changes) do
    local date_str = ""
    local desc_inlines = {}

    if type(item) == "table" then
      if item.date then
        date_str = pandoc.utils.stringify(item.date)
      end
      local desc_val = item.description or item.summary
      if desc_val then
        if type(desc_val) == "table" and (desc_val.t == "MetaInlines" or desc_val.t == "Inlines") then
          desc_inlines = pandoc.Inlines(desc_val)
        else
          desc_inlines = pandoc.Inlines(pandoc.utils.stringify(desc_val))
        end
      end
    else
      desc_inlines = pandoc.Inlines(pandoc.utils.stringify(item))
    end

    local item_content = {}
    if date_str ~= "" then
      local date_span = pandoc.Span(pandoc.Inlines(date_str), pandoc.Attr("", {"revision-history-date"}))
      local strong_date = pandoc.Strong({date_span})
      table.insert(item_content, strong_date)
      table.insert(item_content, pandoc.Str(": "))
    end
    for _, inline in ipairs(desc_inlines) do
      table.insert(item_content, inline)
    end

    local li_para = pandoc.Para(item_content)
    table.insert(items, {li_para})
  end

  local bullet_list = pandoc.BulletList(items)
  local header = pandoc.Header(2, pandoc.Inlines("Revision History"), pandoc.Attr("revision-history-heading", {"revision-history-title", "unlisted"}))
  local section = pandoc.Div({header, bullet_list}, pandoc.Attr("revision-history", {"revision-history", "level2"}))

  -- Insert section: before references / critics-corner if present, else at the end
  local insert_idx = #doc.blocks + 1
  for idx, block in ipairs(doc.blocks) do
    if block.t == "Div" and (block.identifier == "references" or block.classes:includes("references-section") or block.identifier == "critics-corner" or block.classes:includes("critics-corner")) then
      insert_idx = idx
      break
    elseif block.t == "Header" and block.identifier == "references" then
      insert_idx = idx
      break
    end
  end

  table.insert(doc.blocks, insert_idx, section)
  return doc
end
