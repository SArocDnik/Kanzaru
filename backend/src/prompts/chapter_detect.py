CHAPTER_DETECT_PROMPT = """You are a text structure analyzer. Given a long text (possibly a full novel volume), identify all chapter boundaries.

Return ONLY valid JSON, no markdown, no explanation.

JSON structure:
{{
  "chapters": [
    {{
      "title": "exact chapter title/heading as it appears in text",
      "start_marker": "the EXACT first ~80 characters of the chapter content (used to locate where it starts)",
      "estimated_number": 1
    }}
  ]
}}

Rules:
- Order chapters by appearance in the text.
- "start_marker" must be verbatim from the text (copy exactly, including punctuation). This is used to split the text programmatically.
- Include prologue/epilogue/interlude as chapters with their actual title.
- If the text has NO chapter structure (single continuous text), return one entry with title "Chapter 1" and start_marker as the first ~80 chars of the text.
- Look for patterns like: Chapter N, Chương N, 第N章, 第N話, 第N回, Prologue, Epilogue, 序章, 終章, Interlude, Section N, Part N, 第N節, and any similar heading formats.

Text to analyze (may be truncated to first ~{max_chars} chars):
{text}
"""
