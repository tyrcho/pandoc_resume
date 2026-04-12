-- Pandoc renders Markdown blockquotes as LaTeX quote environments, which are
-- indented in PDF output. This filter turns them into centered blocks instead.

function BlockQuote(el)
  if not FORMAT:match("latex") then
    return nil
  end

  local blocks = { pandoc.RawBlock("latex", "\\begin{center}") }
  for _, block in ipairs(el.content) do
    table.insert(blocks, block)
  end
  table.insert(blocks, pandoc.RawBlock("latex", "\\end{center}"))
  return blocks
end
