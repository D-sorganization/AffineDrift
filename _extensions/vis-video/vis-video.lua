-- _extensions/vis-video/vis-video.lua
-- Quarto shortcode {{< vis-video src= poster= captions= alt= record= [caption=] >}}
-- Part of VIS-SITE-2 (#5424) - accessible local video embeds
--
-- Renders a self-hosted WebM or MP4 with a poster, an English captions track,
-- a text alternative and the VIS-EVIDENCE projection record that traces it.
-- The video lazy-loads (preload="none") and never autoplays or loops, so a
-- reader who prefers reduced motion sees only the still poster until they
-- press play. Only page-relative paths are accepted, so no third-party host
-- (and no tracker) can be embedded. Invalid input fails the render.

local VIDEO_TYPES = { webm = "video/webm", mp4 = "video/mp4" }
local POSTER_TYPES = { png = true, jpg = true, jpeg = true, webp = true }
local FORBIDDEN = { "autoplay", "loop", "muted" }

local function stringify(val)
  if val == nil then
    return ""
  end
  return (pandoc.utils.stringify(val):gsub("^%s+", ""):gsub("%s+$", ""))
end

local function escape_html(str)
  local map = {
    ["&"] = "&amp;",
    ["<"] = "&lt;",
    [">"] = "&gt;",
    ['"'] = "&quot;",
    ["'"] = "&#39;"
  }
  return (str:gsub("[&<>'\"]", map))
end

local function fail(field, value, rule)
  error("vis-video: " .. field .. " '" .. value .. "' " .. rule, 0)
end

local function required(kwargs, field)
  local value = stringify(kwargs[field])
  if value == "" then
    error("vis-video: " .. field .. " is required", 0)
  end
  return value
end

-- A page-relative path inside the site: no scheme, no leading slash, no "..".
local function local_path(kwargs, field)
  local value = required(kwargs, field)
  local safe = value:match("^[%w_][%w_./-]*$") ~= nil
  if not safe or value:find("%.%.") or value:find("//") then
    fail(field, value, "must be a page-relative local path")
  end
  return value
end

local function extension(path)
  return (path:match("%.(%w+)$") or ""):lower()
end

local function video_source(kwargs)
  local src = local_path(kwargs, "src")
  local mime = VIDEO_TYPES[extension(src)]
  if mime == nil then
    fail("src", src, "must be a .webm or .mp4 file")
  end
  return src, mime
end

local function poster_path(kwargs)
  local poster = local_path(kwargs, "poster")
  if not POSTER_TYPES[extension(poster)] then
    fail("poster", poster, "must be a .png, .jpg or .webp image")
  end
  return poster
end

local function captions_path(kwargs)
  local captions = local_path(kwargs, "captions")
  if extension(captions) ~= "vtt" then
    fail("captions", captions, "must be a WebVTT (.vtt) file")
  end
  return captions
end

local function record_path(kwargs)
  local record = required(kwargs, "record")
  local shaped = record:match("^evidence/projections/[%w_./-]+%.json$") ~= nil
  if not shaped or record:find("%.%.") then
    fail("record", record, "must be an evidence/projections/*.json record")
  end
  return record
end

local function reject_motion(kwargs)
  for _, field in ipairs(FORBIDDEN) do
    if kwargs[field] ~= nil then
      error("vis-video: " .. field .. " is not allowed (reduced-motion default)", 0)
    end
  end
end

local function figure_html(spec)
  local caption = ""
  if spec.caption ~= "" then
    caption = "\n<figcaption>" .. escape_html(spec.caption) .. "</figcaption>"
  end
  return table.concat({
    '<figure class="vis-video" data-provenance-record="' .. escape_html(spec.record) .. '">',
    '<video controls preload="none" playsinline poster="' .. escape_html(spec.poster)
      .. '" aria-label="' .. escape_html(spec.alt) .. '">',
    '<source src="' .. escape_html(spec.src) .. '" type="' .. spec.mime .. '">',
    '<track kind="captions" src="' .. escape_html(spec.captions)
      .. '" srclang="en" label="English" default>',
    '<a href="' .. escape_html(spec.src) .. '">Download the video</a>',
    "</video>" .. caption,
    "</figure>"
  }, "\n")
end

local function vis_video(_args, kwargs, _meta)
  reject_motion(kwargs)
  local src, mime = video_source(kwargs)
  local spec = {
    src = src,
    mime = mime,
    poster = poster_path(kwargs),
    captions = captions_path(kwargs),
    alt = required(kwargs, "alt"),
    record = record_path(kwargs),
    caption = stringify(kwargs["caption"])
  }
  return pandoc.RawBlock("html", figure_html(spec))
end

return {
  ["vis-video"] = vis_video
}
