## Resume build and publishing

This repository keeps the resume source in [`resume.md`](./resume.md) and generates three outputs:

- `resume.html`
- `resume.pdf`
- `resume.docx`

GitHub Pages serves the generated files from the Actions build artifact. They are not stored in git.

Inspired by [The Markdown Resume](https://github.com/mszep/pandoc_resume).

## How this differs from `mszep/pandoc_resume`

The upstream project is a general-purpose pandoc resume template with broader build tooling. This repository takes a narrower approach tailored to one hosted resume site.

- Upstream uses a template-oriented project layout with `markdown/`, `styles/`, Docker, Nix, ConTeXt, and artifact-oriented Actions.
- This repo keeps a single source file at the root, preserves the existing GitHub Pages styling, and builds directly into `dist/`.
- Upstream is designed as a reusable resume starter.
- This repo is designed as a source-only publishing pipeline for one resume site.
- Upstream stores build logic for many environments.
- This repo optimizes for GitHub Pages deployment via Actions without committing generated `html`/`pdf`/`docx` files.

## Local build

Requirements:

- `pandoc`
- a PDF engine supported by pandoc, defaulting to `xelatex`

Install locally with one of the following:

```bash
# macOS
brew install pandoc
brew install --cask mactex-no-gui
```

```bash
# Ubuntu / Debian
sudo apt-get update
sudo apt-get install -y pandoc texlive-xetex
```

```bash
# Fedora
sudo dnf install -y pandoc texlive-xetex
```

The Makefile also prints the same install hints:

```bash
make deps
```

To check that the required tools are available:

```bash
make check-deps
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

If your preferred PDF engine is different, override it:

```bash
make pdf PDF_ENGINE=pdflatex
```

To preview the generated site locally:

```bash
python3 -m http.server --directory dist 8000
```

Then open `http://localhost:8000`.

## GitHub Pages deployment

The workflow in [`.github/workflows/deploy.yml`](./.github/workflows/deploy.yml) does the following on every relevant push to `master`:

1. installs `pandoc` and `xelatex`
2. runs `make all`
3. uploads `dist/` as the GitHub Pages artifact
4. deploys that artifact to GitHub Pages

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
