-- Derives the page `title` metadata from the document's first level-1
-- heading when a page's front matter omits `title:` (e.g. a page that only
-- sets `pagetitle:`). Without this, Quarto's title-block-header renders an
-- empty `.title` heading -- axe `empty-heading` (issue #5168). The source
-- heading block is removed from the body once promoted, since Quarto's
-- title-block-header already renders it -- leaving it in place produced a
-- second visible H1 (axe/Playwright "visible H1 count is 2").
function Pandoc(doc)
  if doc.meta.title ~= nil then return doc end
  for i, block in ipairs(doc.blocks) do
    if block.t == "Header" and block.level == 1 then
      doc.meta.title = pandoc.MetaInlines(block.content)
      table.remove(doc.blocks, i)
      return doc
    end
  end
  return doc
end
