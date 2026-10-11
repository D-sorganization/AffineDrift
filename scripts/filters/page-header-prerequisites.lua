-- Resolve legacy repository routes from their authored titles; preserve prose.
local M = {}

local function route_title(route)
  local root = quarto and quarto.project and quarto.project.directory or "."
  local source = route:gsub("%.html$", ".qmd")
  local file = io.open(root .. "/" .. source, "r")
  if not file then return nil end
  local text = file:read("*a")
  file:close()
  local header = text:match("^(%-%-%-\r?\n.-\r?\n%-%-%-)")
  if not header then return nil end
  local document = pandoc.read(header, "markdown")
  if not document.meta.title then return nil end
  return pandoc.utils.stringify(document.meta.title)
end

local function plain_route(value, ui)
  local route = value:gsub("^/", "")
  if not route:match("^[%w_/-]+%.html$") or not ui.safe_href("/" .. route) then return nil end
  local title = route_title(route)
  if not title then return nil end
  return '<a href="/' .. ui.escape_html(route) .. '">' .. ui.escape_html(title) .. '</a>'
end

local function render_value(value, ui)
  local text = ui.stringify(value)
  if text == "" then return nil end
  local linked = plain_route(text, ui)
  if linked then return linked end
  -- Preserve Pandoc's parsed link labels instead of stringifying away targets.
  local blocks = pandoc.Blocks({pandoc.Plain(value)})
  local clean = pandoc.Pandoc(blocks):walk({
    Link = function(link)
      if not ui.safe_href(link.target) then return link.content end
      return link
    end,
    RawInline = function(raw) return pandoc.Str(raw.text) end,
    Image = function(image) return image.caption end,
  })
  return pandoc.write(clean, "html")
end

function M.render(raw, ui)
  if raw == nil then return nil end
  local values = pandoc.utils.type(raw) == "List" and raw or {raw}
  local items = {}
  for _, value in ipairs(values) do
    local content = render_value(value, ui)
    if content then table.insert(items, '<li>' .. content .. '</li>') end
  end
  if #items == 0 then return nil end
  return '<ul class="page-header-prereq-list">' .. table.concat(items, "\n") .. '</ul>'
end

return M
