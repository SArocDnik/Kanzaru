import io
import pytest
from src.services.extractor import extract_from_text, extract_from_pdf, PageText


def test_extract_from_text_single_page():
    pages = extract_from_text("Hello world")
    assert len(pages) == 1
    assert pages[0].page_num == 1
    assert pages[0].text == "Hello world"
    assert pages[0].extraction_method == "text"


def test_extract_from_text_multi_page():
    text = "Page one\n---\nPage two\n---\nPage three"
    pages = extract_from_text(text, page_delimiter="\n---\n")
    assert len(pages) == 3
    assert pages[0].text == "Page one"
    assert pages[1].text == "Page two"
    assert pages[2].text == "Page three"
    assert pages[1].page_num == 2


def test_extract_from_pdf_text_based():
    import fitz
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "This is a text-based PDF page with enough content to pass the threshold.")
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    buf.seek(0)

    pages = extract_from_pdf(buf)
    assert len(pages) == 1
    assert pages[0].extraction_method == "pymupdf"
    assert "text-based" in pages[0].text


def test_extract_from_pdf_empty_page_marked_for_ocr():
    import fitz
    doc = fitz.open()
    doc.new_page()
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    buf.seek(0)

    pages = extract_from_pdf(buf, run_ocr=False)
    assert len(pages) == 1
    assert pages[0].extraction_method == "needs_ocr"
    assert pages[0].text == ""
