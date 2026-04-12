PANDOC ?= pandoc
PDF_ENGINE ?= xelatex
DIST_DIR := dist
TEMPLATE := templates/resume.html5
RESUME_SRC := resume.md
TITLE ?= Michel Daviot

.PHONY: all html pdf docx clean deps check-deps

all: check-deps html pdf docx $(DIST_DIR)/index.html $(DIST_DIR)/css/resume.css $(DIST_DIR)/.nojekyll $(DIST_DIR)/CNAME

html: $(DIST_DIR)/resume.html

pdf: check-deps $(DIST_DIR)/resume.pdf

docx: check-deps $(DIST_DIR)/resume.docx

deps:
	@echo "Install dependencies with one of the following:"
	@echo "  macOS (Homebrew): brew install pandoc && brew install --cask mactex-no-gui"
	@echo "  Ubuntu/Debian:    sudo apt-get update && sudo apt-get install -y pandoc texlive-xetex"
	@echo "  Fedora:           sudo dnf install -y pandoc texlive-xetex"

check-deps:
	@command -v $(PANDOC) >/dev/null || (echo "Missing dependency: $(PANDOC). Run 'make deps' for install hints."; exit 1)
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
		--metadata title="$(TITLE)" \
		--output $@ \
		$<

$(DIST_DIR)/resume.pdf: $(RESUME_SRC) | $(DIST_DIR)
	$(PANDOC) \
		--standalone \
		--pdf-engine=$(PDF_ENGINE) \
		--metadata title="$(TITLE)" \
		--output $@ \
		$<

$(DIST_DIR)/resume.docx: $(RESUME_SRC) | $(DIST_DIR)
	$(PANDOC) \
		--standalone \
		--output $@ \
		$<

$(DIST_DIR)/index.html: index.html | $(DIST_DIR)
	cp $< $@

$(DIST_DIR)/.nojekyll: | $(DIST_DIR)
	touch $@

$(DIST_DIR)/CNAME: CNAME | $(DIST_DIR)
	cp $< $@
