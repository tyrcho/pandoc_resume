import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from scripts.document_tools import (
    WORD_NS,
    get_metadata_value,
    set_docx_margins,
)


class DocumentToolsTest(unittest.TestCase):
    def test_metadata_reads_yaml_block_scalar_title(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            markdown_path = Path(tmpdir) / "resume.md"
            markdown_path.write_text(
                "---\n"
                "title: |\n"
                "  Senior Engineering Manager\n"
                "  Platform & AI\n"
                "margin: 1in\n"
                "---\n",
                encoding="utf-8",
            )

            self.assertEqual(
                get_metadata_value("title", markdown_path),
                "Senior Engineering Manager\nPlatform & AI\n",
            )

    def test_set_docx_margins_updates_all_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            docx_path = Path(tmpdir) / "resume.docx"
            document_xml = (
                '<?xml version="1.0" encoding="UTF-8"?>'
                '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                "<w:body>"
                "<w:p/>"
                '<w:sectPr><w:pgMar w:top="1440" w:right="1440" '
                'w:bottom="1440" w:left="1440"/></w:sectPr>'
                "<w:p/>"
                '<w:sectPr><w:pgMar w:top="1440" w:right="1440" '
                'w:bottom="1440" w:left="1440"/></w:sectPr>'
                "</w:body>"
                "</w:document>"
            )
            with zipfile.ZipFile(
                docx_path,
                "w",
                compression=zipfile.ZIP_DEFLATED,
            ) as docx:
                docx.writestr("word/document.xml", document_xml)

            set_docx_margins(docx_path, "720")

            with zipfile.ZipFile(docx_path) as docx:
                root = ET.fromstring(docx.read("word/document.xml"))

            margins = []
            for sect_pr in root.findall(f".//{{{WORD_NS}}}sectPr"):
                pg_mar = sect_pr.find(f"{{{WORD_NS}}}pgMar")
                self.assertIsNotNone(pg_mar)
                margins.append(
                    (
                        pg_mar.attrib[f"{{{WORD_NS}}}top"],
                        pg_mar.attrib[f"{{{WORD_NS}}}right"],
                        pg_mar.attrib[f"{{{WORD_NS}}}bottom"],
                        pg_mar.attrib[f"{{{WORD_NS}}}left"],
                    )
                )

            self.assertEqual(
                margins,
                [("720", "720", "720", "720"), ("720", "720", "720", "720")],
            )


if __name__ == "__main__":
    unittest.main()
