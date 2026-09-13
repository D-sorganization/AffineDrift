-- Chapter titles were normalized to H2 for the website's single-H1 contract.
-- Restore their subordinate hierarchy before Quarto numbers sections, while
-- preserving the existing Pandoc IDs used by incoming links. Scoped to the
-- companion wrapper: scientific chapter files and their prose are unchanged.
function Pandoc(document)
  local inside_chapter = false
  for _, block in ipairs(document.blocks) do
    if block.t == "Header" then
      if block.identifier:match("^sec%-lay%-ch%d%d$") then
        inside_chapter = true
      elseif block.identifier == "glossary" or block.identifier == "references" then
        inside_chapter = false
      elseif inside_chapter then
        block.level = block.level + 1
      end
    end
  end
  return document
end
