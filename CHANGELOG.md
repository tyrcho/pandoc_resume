# Changelog

## 2026-04-12

- add a local `Makefile` build pipeline for `html`, `pdf`, and `docx` outputs
- add GitHub Actions deployment for GitHub Pages
- move document title metadata into `resume.md` front matter
- reduce PDF margins via Pandoc `geometry`
- reduce DOCX margins with a post-processing script
- center the intro block in PDF output with a Pandoc Lua filter
