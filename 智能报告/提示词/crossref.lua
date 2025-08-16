-- crossref.lua

-- Tables to store counters and mappings by prefix.
local crossrefs = {}      -- crossrefs[prefix][label] = assigned number
local nextNumbers = {}    -- nextNumbers[prefix] = next available number for that prefix

-- Helper function to split an id into prefix and label.
-- If no colon is found, it defaults to using "default" as the prefix.
local function splitId(id)
  local prefix, label = string.match(id, "^(.-):(.*)$")
  if not prefix or prefix == "" then
    prefix = "default"
    label = id
  end
  return prefix, label
end

-- The Cite function is called for every citation element.
function Cite(elem)
  -- Process each citation in the Cite element.
  for _, citation in ipairs(elem.citations) do
    local id = citation.id
    local prefix, label = splitId(id)

    -- Initialize the tables for this prefix if necessary.
    if not crossrefs[prefix] then
      crossrefs[prefix] = {}
      nextNumbers[prefix] = 1
    end

    -- If this label hasn't been seen for this prefix, assign the next number.
    if not crossrefs[prefix][label] then
      crossrefs[prefix][label] = nextNumbers[prefix]
      nextNumbers[prefix] = nextNumbers[prefix] + 1
    end
  end

  -- For this Cite element, return the number assigned to the first citation.
  local firstCitationId = elem.citations[1].id
  local prefix, label = splitId(firstCitationId)
  return pandoc.Str(tostring(crossrefs[prefix][label]))
end
