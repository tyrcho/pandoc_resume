PANDOC ?= pandoc
PDF_ENGINE ?= tectonic
DIST_DIR := dist
TEMPLATE := templates/resume.html5
RESUME_SRC := resume.md

.PHONY: all html pdf docx clean deps check-deps check-pandoc check-pdf-engine

all: check-pandoc check-pdf-engine html pdf docx $(DIST_DIR)/index.html $(DIST_DIR)/css/resume.css $(DIST_DIR)/.nojekyll $(DIST_DIR)/CNAME

html: $(DIST_DIR)/resume.html

pdf: check-pandoc check-pdf-engine $(DIST_DIR)/resume.pdf

docx: check-pandoc $(DIST_DIR)/resume.docx

deps:
	@echo "Tested local setup on macOS:"
	@echo "  brew install pandoc"
	@echo "  brew install tectonic"
	@echo ""
	@echo "Alternative: brew install --cask mactex-no-gui"
	@echo "Note: mactex-no-gui is a large download and install."
	@echo "For other platforms, see https://github.com/mszep/pandoc_resume"

check-deps:
	@$(MAKE) check-pandoc
	@$(MAKE) check-pdf-engine

check-pandoc:
	@command -v $(PANDOC) >/dev/null || (echo "Missing dependency: $(PANDOC). Run 'make deps' for install hints."; exit 1)

check-pdf-engine:
	@command -v $(PDF_ENGINE) >/dev/null || (echo "Missing PDF engine: $(PDF_ENGINE). Run 'make deps' for install hints."; exit 1)

clean:
	rm -rf $(DIST_DIR)

$(DIST_DIR):
	mkdir -p $(DIST_DIR)/css

$(DIST_DIR)/css/resume.css: css/resume.css | $(DIST_DIR)
	cp $< $@

$(DIST_DIR)/resume.html: $(RESUME_SRC) $(TEMPLATE) css/resume.css | $(DIST_DIR)/css/resume.css
	$(PANDOC) \
		--standalone \
		--template $(TEMPLATE) \
		--output $@ \
		$<

$(DIST_DIR)/resume.pdf: $(RESUME_SRC) | $(DIST_DIR)
	$(PANDOC) \
		--standalone \
		--pdf-engine=$(PDF_ENGINE) \
		--lua-filter=scripts/latex_center_blockquotes.lua \
		--variable geometry:margin="$$(python3 scripts/document_tools.py margin pdf $(RESUME_SRC))" \
		--output $@ \
		$<

$(DIST_DIR)/resume.docx: $(RESUME_SRC) | $(DIST_DIR)
	$(PANDOC) \
		--standalone \
		--output $@ \
		$<
	python3 scripts/document_tools.py set-docx-margins-from-markdown $@ $(RESUME_SRC)

$(DIST_DIR)/index.html: index.html | $(DIST_DIR)
	cp $< $@

$(DIST_DIR)/.nojekyll: | $(DIST_DIR)
	touch $@

$(DIST_DIR)/CNAME: CNAME | $(DIST_DIR)
	cp $< $@
