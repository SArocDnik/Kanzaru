from src.services.chapter_splitter import detect_chapters, ChapterResult


def test_detect_vietnamese_chapters():
    text = "Chương 1\nNội dung chương 1\n\nChương 2\nNội dung chương 2\n\nChương 3\nNội dung chương 3"
    chapters = detect_chapters(text)
    assert len(chapters) == 3
    assert chapters[0].title == "Chương 1"
    assert "Nội dung chương 1" in chapters[0].content
    assert chapters[1].title == "Chương 2"
    assert chapters[2].title == "Chương 3"


def test_detect_japanese_chapters():
    text = "第1章\nコンテンツ1\n\n第2章\nコンテンツ2"
    chapters = detect_chapters(text)
    assert len(chapters) == 2
    assert chapters[0].title == "第1章"
    assert chapters[1].title == "第2章"


def test_detect_english_chapters():
    text = "Chapter 1\nContent one\n\nChapter 2\nContent two"
    chapters = detect_chapters(text)
    assert len(chapters) == 2
    assert chapters[0].title == "Chapter 1"
    assert chapters[1].title == "Chapter 2"


def test_detect_japanese_manga_chapters():
    text = "第1話\n内容1\n\n第2話\n内容2"
    chapters = detect_chapters(text)
    assert len(chapters) == 2


def test_no_chapters_found_returns_single():
    text = "This is just a long text without any chapter markers at all."
    chapters = detect_chapters(text)
    assert len(chapters) == 1
    assert chapters[0].title == "Chapter 1"
    assert chapters[0].content == text


def test_chinese_classical_chapters():
    text = "第一回\n内容1\n\n第二回\n内容2"
    chapters = detect_chapters(text)
    assert len(chapters) == 2


def test_chapter_with_title_on_same_line():
    text = "Chương 1: Mở đầu\nNội dung\n\nChương 2: Kết thúc\nNội dung 2"
    chapters = detect_chapters(text)
    assert len(chapters) == 2
    assert "Mở đầu" in chapters[0].title
    assert "Kết thúc" in chapters[1].title
