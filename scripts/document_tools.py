#!/usr/bin/env python3

# Keep PDF and DOCX page margins in one place by reading the shared inch-based
# margin value from Markdown front matter. DOCX then needs a post-process step
# because Pandoc does not expose Word page margins directly.

from __future__ import annotations

import argparse
import re
import shutil
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import yaml

WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
ET.register_namespace("w", WORD_NS)


def read_front_matter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}

    match = re.match(r"^---\s*\n(.*?)\n---(?:\s*\n|$)", text, re.DOTALL)
    if match is None:
        return {}

    loaded = yaml.safe_load(match.group(1))
    if loaded is None:
        return {}
    if not isinstance(loaded, dict):
        raise ValueError("Front matter must be a YAML mapping.")

    return {
        str(key): "" if value is None else str(value)
        for key, value in loaded.items()
    }


def margin_to_twips(margin: str) -> str:
    match = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)in", margin)
    if not match:
        raise ValueError(
            f"Unsupported margin format: {margin!r}. Expected values like 0.5in or 1in."
        )
    return str(round(float(match.group(1)) * 1440))


def get_margin(target: str, markdown_path: Path) -> str:
    metadata = read_front_matter(markdown_path)
    margin = metadata.get("margin", "1in")
    if target == "pdf":
        return margin
    if target == "docx":
        return margin_to_twips(margin)
    raise ValueError(f"Unsupported target: {target!r}")


def get_metadata_value(key: str, markdown_path: Path) -> str:
    metadata = read_front_matter(markdown_path)
    if key == "title":
        return metadata.get("title") or metadata.get("pagetitle") or ""
    return metadata.get(key, "")


def set_docx_margins(docx_path: Path, margin_twips: str) -> None:
    docx_path = docx_path.resolve()
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        with zipfile.ZipFile(docx_path) as source_zip:
            source_zip.extractall(tmpdir_path)

        document_xml = tmpdir_path / "word" / "document.xml"
        tree = ET.parse(document_xml)
        root = tree.getroot()

        sect_pr_nodes = root.findall(f".//{{{WORD_NS}}}sectPr")
        if not sect_pr_nodes:
            raise RuntimeError("Could not find <w:sectPr> in document.xml")

        for sect_pr in sect_pr_nodes:
            pg_mar = sect_pr.find(f"{{{WORD_NS}}}pgMar")
            if pg_mar is None:
                pg_mar = ET.Element(f"{{{WORD_NS}}}pgMar")
                sect_pr.insert(0, pg_mar)

            pg_mar.attrib.update(
                {
                    f"{{{WORD_NS}}}top": margin_twips,
                    f"{{{WORD_NS}}}right": margin_twips,
                    f"{{{WORD_NS}}}bottom": margin_twips,
                    f"{{{WORD_NS}}}left": margin_twips,
                    f"{{{WORD_NS}}}header": "720",
                    f"{{{WORD_NS}}}footer": "720",
                    f"{{{WORD_NS}}}gutter": "0",
                }
            )

        tree.write(document_xml, encoding="UTF-8", xml_declaration=True)

        rebuilt_path = tmpdir_path / "rebuilt.docx"
        with zipfile.ZipFile(
            rebuilt_path,
            "w",
            compression=zipfile.ZIP_DEFLATED,
        ) as target_zip:
            for path in sorted(tmpdir_path.rglob("*")):
                if path == rebuilt_path or path.is_dir():
                    continue
                target_zip.write(path, path.relative_to(tmpdir_path))

        shutil.move(rebuilt_path, docx_path)


def set_docx_margins_from_markdown(docx_path: Path, markdown_path: Path) -> None:
    set_docx_margins(docx_path, get_margin("docx", markdown_path))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    margin_parser = subparsers.add_parser("margin")
    margin_parser.add_argument("target", choices=["pdf", "docx"])
    margin_parser.add_argument("markdown_path")

    metadata_parser = subparsers.add_parser("metadata")
    metadata_parser.add_argument("key")
    metadata_parser.add_argument("markdown_path")

    docx_parser = subparsers.add_parser("set-docx-margins")
    docx_parser.add_argument("docx_path")
    docx_parser.add_argument("margin_twips")

    docx_from_md_parser = subparsers.add_parser("set-docx-margins-from-markdown")
    docx_from_md_parser.add_argument("docx_path")
    docx_from_md_parser.add_argument("markdown_path")

    return parser


def main() -> int:
    args = build_parser().parse_args()

    if args.command == "margin":
        print(get_margin(args.target, Path(args.markdown_path)))
        return 0

    if args.command == "metadata":
        print(get_metadata_value(args.key, Path(args.markdown_path)))
        return 0

    if args.command == "set-docx-margins":
        set_docx_margins(Path(args.docx_path), args.margin_twips)
        return 0

    if args.command == "set-docx-margins-from-markdown":
        set_docx_margins_from_markdown(Path(args.docx_path), Path(args.markdown_path))
        return 0

    raise RuntimeError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
