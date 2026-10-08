"""Reproducible invented PDF and Word fixtures, using existing pypdf and stdlib only."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

ROOT = Path(__file__).parent


def pdf(target: Path, texts: list[str], password: str | None = None) -> None:
    writer = PdfWriter()
    font = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    ref = writer._add_object(font)
    for text in texts:
        page = writer.add_blank_page(width=612, height=792)
        page[NameObject("/Resources")] = DictionaryObject(
            {NameObject("/Font"): DictionaryObject({NameObject("/F1"): ref})}
        )
        stream = DecodedStreamObject()
        stream.set_data(f"BT /F1 12 Tf 50 700 Td ({text}) Tj ET".encode() if text else b"")
        page[NameObject("/Contents")] = writer._add_object(stream)
    if password:
        writer.encrypt(password)
    with target.open("wb") as handle:
        writer.write(handle)


def main() -> None:
    pdf(
        ROOT / "two-pages.pdf",
        [
            "Invented silver orchard report. The violet lantern glows.",
            "Invented second page. The copper meadow blooms.",
        ],
    )
    pdf(ROOT / "large-text.pdf", ["Invented violet garden. " * 2800])
    pdf(ROOT / "scanned.pdf", [""])
    pdf(ROOT / "encrypted.pdf", ["Invented locked garden report."], "synthetic")
    (ROOT / "damaged.pdf").write_bytes((ROOT / "two-pages.pdf").read_bytes()[:80])
    xml = """<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>
<w:p><w:r><w:t>Invented orchard ledger</w:t></w:r>
<w:del><w:r><w:delText>Deleted secret</w:delText></w:r></w:del></w:p>
<w:tbl><w:tr><w:tc><w:p><w:r><w:t>Lantern</w:t></w:r></w:p>
<w:del><w:p><w:r><w:t>Discarded</w:t></w:r></w:p></w:del></w:tc><w:tc><w:p><w:r><w:t>Meadow</w:t></w:r></w:p></w:tc></w:tr><w:tr><w:tc><w:p><w:r><w:t>Violet</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>Copper</w:t></w:r></w:p></w:tc></w:tr></w:tbl>
<w:p><w:r><w:t>Invented final paragraph.</w:t><w:tab/><w:t>Fin.</w:t>
<w:br/><w:t>End.</w:t></w:r></w:p></w:body></w:document>"""
    with ZipFile(ROOT / "table.docx", "w", compression=ZIP_DEFLATED) as archive:
        for name, value in [
            ("word/document.xml", xml),
            ("word/header1.xml", "<ignored>Invented header</ignored>"),
            ("word/comments.xml", "<ignored>Invented comment</ignored>"),
        ]:
            info = ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            archive.writestr(info, value)


if __name__ == "__main__":
    main()
