-- Derives the page `title` metadata from the document's first level-1
-- heading when a page's front matter omits `title:` (e.g. a page that only
-- sets `pagetitle:`). Without this, Quarto's title-block-header renders an
-- empty `.title` heading -- axe `empty-heading` (issue #5168). Presentation
-- only: no article content changes, since the heading text already exists
-- in the authored body.
function Pandoc(doc)
  if doc.meta.title ~= nil then return doc end
  for _, block in ipairs(doc.blocks) do
    if block.t == "Header" and block.level == 1 then
      doc.meta.title = pandoc.MetaInlines(block.content)
      return doc
    end
  end
  return doc
end
