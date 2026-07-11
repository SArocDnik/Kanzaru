from dataclasses import dataclass
from io import BytesIO
from typing import BinaryIO, Union

BytesLike = Union[bytes, bytearray, BytesIO, BinaryIO]


@dataclass
class PageText:
    page_num: int
    text: str
    extraction_method: str  # "text", "pymupdf", "ocr", "needs_ocr"


def _to_bytes(file: BytesLike) -> bytes:
    if isinstance(file, (bytes, bytearray)):
        return bytes(file)
    return file.read()


def extract_from_text(content: str, page_delimiter: str = "\n---\n") -> list[PageText]:
    if page_delimiter in content:
        parts = content.split(page_delimiter)
    else:
        parts = [content]
    return [
        PageText(page_num=i + 1, text=p.strip(), extraction_method="text")
        for i, p in enumerate(parts)
        if p.strip()
    ]


def extract_from_pdf(file: BytesLike, run_ocr: bool = True) -> list[PageText]:
    import fitz  # PyMuPDF

    data = _to_bytes(file)
    doc = fitz.open(stream=data, filetype="pdf")
    pages: list[PageText] = []

    for i, page in enumerate(doc):
        text = page.get_text().strip()
        if len(text) < 50:
            pages.append(PageText(page_num=i + 1, text="", extraction_method="needs_ocr"))
        else:
            pages.append(PageText(page_num=i + 1, text=text, extraction_method="pymupdf"))

    doc.close()

    if run_ocr:
        needs_ocr = [p for p in pages if p.extraction_method == "needs_ocr"]
        if needs_ocr:
            ocr_pages = extract_with_ocr(data)
            for p in pages:
                if p.extraction_method == "needs_ocr":
                    ocr_p = next((o for o in ocr_pages if o.page_num == p.page_num), None)
                    if ocr_p:
                        p.text = ocr_p.text
                        p.extraction_method = "ocr"

    return pages


def extract_with_ocr(file: BytesLike) -> list[PageText]:
    import fitz

    data = _to_bytes(file)
    doc = fitz.open(stream=data, filetype="pdf")
    pages: list[PageText] = []

    try:
        from rapidocr_onnxruntime import RapidOCR
        ocr = RapidOCR()
    except ImportError:
        n = len(doc)
        doc.close()
        return [PageText(page_num=i + 1, text="", extraction_method="ocr_failed")
                for i in range(n)]

    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=200)
        img_bytes = pix.tobytes("png")
        result, _ = ocr(img_bytes)
        text = " ".join([line[1] for line in result]) if result else ""
        pages.append(PageText(page_num=i + 1, text=text.strip(), extraction_method="ocr"))

    doc.close()
    return pages
