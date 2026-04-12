## Resume build and publishing

This repository keeps the resume source in [`resume.md`](./resume.md) and generates three outputs:

- `resume.html`
- `resume.pdf`
- `resume.docx`

GitHub Pages serves the generated files from the Actions build artifact. They are not stored in git.

Live site: [cv.daviot.info](https://cv.daviot.info)

## Usage

If you fork this repository for your own resume, the usual workflow is:

1. replace the content in [`resume.md`](./resume.md) with your own resume data
2. update the `title` and optional `margin` front matter in `resume.md`
3. adjust the HTML presentation in [`css/resume.css`](./css/resume.css) if you want different styling
4. adjust the HTML shell in [`templates/resume.html5`](./templates/resume.html5) if you want a different page structure or download links
5. run `make all` locally and review the generated files in `dist/`
6. if you publish through GitHub Pages, update or remove [`CNAME`](./CNAME) to match your own domain setup

The generated outputs are:

- `dist/resume.html`
- `dist/resume.pdf`
- `dist/resume.docx`

## Local build

Requirements:

- `pandoc`
- A PDF engine:
  - `tectonic` is the default for local builds in this repository
  - `xelatex` is used in GitHub Actions because it is available from Ubuntu packages there
- `python3`
- `PyYAML` for parsing Markdown front matter in `scripts/document_tools.py`
- `ruff` for Python linting

Tested local setup on macOS:

```bash
brew install pandoc
brew install tectonic
python3 -m pip install PyYAML ruff
```

Alternative on macOS:

```bash
brew install --cask mactex-no-gui
```

`mactex-no-gui` works as the TeX distribution for `xelatex`, but it is a large download and install.

Other platforms are not documented or tested in this repository. For broader setup guidance on Linux and other environments, see the upstream project: [mszep/pandoc_resume](https://github.com/mszep/pandoc_resume).

The Makefile also prints install hints:

```bash
make deps
```

To check that the required tools are available:

```bash
make check-deps
```

Run the Python linter:

```bash
make lint
```

Build everything into `dist/`:

```bash
make all
```

Build individual formats:

```bash
make html
make pdf
make docx
```

Clean generated files:

```bash
make clean
```

If you want to use a different PDF engine temporarily, override it:

```bash
make pdf PDF_ENGINE=xelatex
```

CI note:
GitHub Actions builds the PDF with `PDF_ENGINE=xelatex` and installs `texlive-xetex`, while local builds still default to `tectonic`.

To preview the generated site locally:

```bash
python3 -m http.server --directory dist 8000
```

Then open `http://localhost:8000`.

## Design

### Building blocks

- [`resume.md`](./resume.md): the single source document for the resume content, including front matter such as `title` and `margin`
- [`css/resume.css`](./css/resume.css): the stylesheet for the generated HTML resume and the GitHub Pages site
- [`templates/resume.html5`](./templates/resume.html5): the Pandoc HTML template that wraps the generated resume body
- [`scripts/document_tools.py`](./scripts/document_tools.py): Python helper for reading Markdown front matter and post-processing DOCX margins
- [`scripts/latex_center_blockquotes.lua`](./scripts/latex_center_blockquotes.lua): Pandoc Lua filter used only for PDF generation
- [`tests/test_document_tools.py`](./tests/test_document_tools.py): unit tests for the Python document helper script
- [`Makefile`](./Makefile): local build, lint, test, and dependency-check entry point
- [`.github/workflows/deploy.yml`](./.github/workflows/deploy.yml): CI workflow that lints, tests, builds, and deploys the site to GitHub Pages
- [`index.html`](./index.html): redirect page used as the site root so `/` forwards to `/resume.html`
- [`CNAME`](./CNAME): custom domain configuration copied into the published Pages artifact
- [`dist/`](./dist): generated build output for local preview and GitHub Pages deployment; this directory is ignored by git
- [`pyproject.toml`](./pyproject.toml): minimal Ruff configuration for Python linting
- [`CHANGELOG.md`](./CHANGELOG.md): lightweight change log for repository-level updates
- [`_config.yml`](./_config.yml): legacy GitHub Pages configuration kept in the repo, but the published site is built from the Actions artifact rather than by Jekyll

## GitHub Pages deployment

The workflow in [`.github/workflows/deploy.yml`](./.github/workflows/deploy.yml) does the following on every relevant push to `master`:

1. installs `pandoc`, `python3-yaml`, `texlive-xetex`, and `ruff`
2. runs `make lint`
3. runs `make test`
4. runs `make all PDF_ENGINE=xelatex`
5. uploads `dist/` as the GitHub Pages artifact
6. deploys that artifact to GitHub Pages

The published site includes:

- `/resume.html`
- `/resume.pdf`
- `/resume.docx`

`/` redirects to `/resume.html`.

## Editing

- Update content in [`resume.md`](./resume.md).
- Adjust presentation in [`css/resume.css`](./css/resume.css).
- Adjust the generated HTML shell in [`templates/resume.html5`](./templates/resume.html5).

## Notes

- `CNAME` is copied into the built site so the custom domain continues to work.
- `.nojekyll` is added to the build output so Pages serves the artifact as static files without Jekyll processing.


### Comparison with upstream

Inspired by [The Markdown Resume](https://github.com/mszep/pandoc_resume).

The upstream project is a general-purpose pandoc resume template with broader build tooling. This repository takes a narrower approach tailored to one hosted resume site.

- Upstream uses a template-oriented project layout with `markdown/`, `styles/`, Docker, Nix, ConTeXt, and artifact-oriented Actions.
- This repo keeps a single source file at the root, preserves the existing GitHub Pages styling, and builds directly into `dist/`.
- Upstream is designed as a reusable resume starter.
- This repo is designed as a source-only publishing pipeline for one resume site.
- Upstream stores build logic for many environments.
- This repo optimizes for GitHub Pages deployment via Actions without committing generated `html`/`pdf`/`docx` files.
