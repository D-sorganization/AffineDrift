-- Shared, escaped HTML boundary for metadata components.
local M = {}

function M.stringify(value)
  if value == nil then return "" end
  return pandoc.utils.stringify(value):gsub("^%s+", ""):gsub("%s+$", "")
end

function M.escape_html(value)
  local escapes = { ["&"] = "&amp;", ["<"] = "&lt;", [">"] = "&gt;", ['"'] = "&quot;", ["'"] = "&#39;" }
  return (value:gsub("[&<>'\"]", escapes))
end

function M.safe_href(value)
  -- Only web URLs, fragments and root-relative routes cross this boundary.
  if value:find("[%c%s]") or value:find("\\", 1, true) then return false end
  if value:match("^https?://[%w.-]+[/#?]?") then return true end
  if value:match("^#[%w_-]+$") then return true end
  return value:match("^/[%w_-]") ~= nil and not value:find("..", 1, true)
    and not value:find("%%")
end

function M.item(key, label, content)
  assert(key:match("^[%w-]+$"), "metadata class must be a slug")
  assert(type(content) == "string" and content ~= "", "metadata item requires content")
  return '<div class="page-header-item page-header-item--' .. key .. '">' ..
    '<dt class="page-header-label">' .. M.escape_html(label) .. '</dt>' ..
    '<dd class="page-header-value">' .. content .. '</dd></div>'
end

return M
