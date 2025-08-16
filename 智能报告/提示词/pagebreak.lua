function HorizontalRule(el)
  if FORMAT:match("docx") then
    return pandoc.RawBlock("openxml", '<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
  else
    return el
  end
end

return {
  {HorizontalRule = HorizontalRule}
}