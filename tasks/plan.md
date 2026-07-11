# Implementation Plan: Kanzaru — Story Translation App

## Overview

Web app dịch truyện đa ngôn ngữ → Việt. Input: PDF (text + scanned) hoặc raw text. Pipeline: extract text → detect chapters → pre-analyze (summary + characters + relationships) → research (glossary + LLM + web search) → context-aware translation → structured JSON output → TTS audio generation (VieNeu-TTS) với karaoke text sync. Chạy local LLM qua Ollama, không cần API key.

## Architecture Decisions

### Stack
- **Backend:** Python 3.14 + FastAPI + uv (package manager)
- **Frontend:** React + Vite + TypeScript + Tailwind CSS
- **LLM:** Ollama local — Llama 3.1 8B hoặc Qwen2.5 7B
- **TTS:** VieNeu-TTS v3 Turbo (`vieneu` SDK) — CPU ONNX, 48kHz, 14 preset voices, `doc_truyen` style, emotion cues, streaming
- **DB:** SQLite via SQLModel (integrated with Pydantic)
- **OCR:** RapidOCR (pip, PaddleOCR-based) primary + Tesseract fallback
- **PDF:** PyMuPDF (fitz) — fast, reliable text extraction
- **Web search:** DuckDuckGo HTML scraping (no API key needed)
- **Streaming:** Server-Sent Events (SSE) cho translation + TTS progress
- **Audio:** WAV (lossless) + MP3 (ffmpeg encode) cho web playback

### Pipeline Design
```
Upload PDF/Text
    │
    ▼
[1] Text Extraction
    ├ Text PDF → PyMuPDF
    └ Scanned PDF → RapidOCR (auto-detect: <50 chars/page → OCR)
    │
    ▼
[2] Chapter Detection
    ├ Auto: regex patterns (Chương X, 第X章, Chapter X, 第X話, etc.)
    └ Manual: user adjusts in UI
    │
    ▼
[3] Pre-Translation Analysis (per chapter, incremental)
    ├ Summary: tóm tắt nội dung chương
    ├ Character extraction: tên, vai trò, xưng hô
    ├ Relationship mapping: quan hệ giữa nhân vật
    └ Context carry: running glossary across chapters
    │
    ▼
[4] Research & Enrichment
    ├ User glossary lookup (exact match)
    ├ DuckDuckGo web search (character + series → wiki/fandom)
    └ LLM knowledge synthesis
    │
    ▼
[5] Translation (per chapter, streaming via SSE)
    ├ Prompt: summary + characters + glossary + context
    ├ Honorifics: keep or translate per glossary rules
    ├ Emotion cues auto-injected: [cười], [thở dài], [hắng giọng]
    └ Output: Vietnamese text
    │
    ▼
[6] Structured JSON Output
    {
      "metadata": {source_lang, target_lang, model, timestamp},
      "summary": "...",
      "characters": [{name, role, relationships, honorifics, notes}],
      "chapters": [{number, title, original, translated, analysis}]
    }
    │
    ▼
[7] Emotion Cue Injection (post-translation edit)
    ├ LLM auto-inject cues during translation step
    └ User edit text trước khi TTS (textarea + cue preview)
    │
    ▼
[8] TTS Generation (per chapter, background job)
    ├ Split translated text → segments (sentence-level)
    ├ Generate audio per segment via vieneu SDK (infer_stream)
    ├ Style: doc_truyen (default) | tu_nhien | tin_tuc
    ├ Voice: 14 preset voices (Bắc/Trung/Nam)
    ├ Track timestamps per segment → timeline
    ├ Save WAV (lossless) + MP3 (ffmpeg encode)
    └ Store AudioFile + AudioTimeline in DB
    │
    ▼
[9] Audio Playback UI
    ├ Player: play/pause/seek/speed/skip ±15s
    ├ Auto-next chapter (toggleable)
    ├ Text sync (karaoke): highlight current segment, click → seek
    └ Voice + style selection
```

### Key Design Principles
- **Vertical slicing:** Mỗi task deliver working, testable functionality
- **Offline-first:** Core pipeline không cần internet. Web search là enhancement
- **Streaming UX:** SSE cho translation + TTS progress, không block UI
- **Glossary persistence:** Lưu trữ glossary per-project, reusable across chapters
- **Context window management:** Chia chương nhỏ, carry context qua running glossary
- **Sequential heavy processing:** Translation xong → TTS. Tránh memory pressure (Ollama + VieNeu cùng chạy)
- **Segment-level TTS:** Split theo câu → timeline chính xác cho karaoke sync

## Project Structure

```
D:\Kanzaru\
├── backend/
│   ├── pyproject.toml          # uv-managed
│   ├── src/
│   │   ├── main.py             # FastAPI app entry
│   │   ├── config.py           # Settings (Ollama URL, DB path, TTS config, etc.)
│   │   ├── models/
│   │   │   ├── db.py           # SQLModel tables (incl. AudioFile, AudioTimeline)
│   │   │   └── schemas.py      # API request/response models
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── upload.py   # PDF/text upload
│   │   │   │   ├── chapters.py # Chapter management
│   │   │   │   ├── translate.py # Translation + SSE streaming
│   │   │   │   ├── glossary.py # Glossary CRUD
│   │   │   │   ├── projects.py # Project management
│   │   │   │   ├── tts.py      # TTS generation + audio serving
│   │   │   │   └── llm.py      # LLM health + model listing
│   │   │   └── deps.py         # Dependencies (DB session, etc.)
│   │   ├── services/
│   │   │   ├── extractor.py    # PDF text extraction + OCR
│   │   │   ├── chapter_splitter.py  # Chapter detection
│   │   │   ├── analyzer.py     # Summary + character extraction
│   │   │   ├── researcher.py   # Web search + glossary lookup
│   │   │   ├── translator.py   # LLM translation orchestration
│   │   │   ├── llm_client.py   # Ollama API wrapper
│   │   │   ├── tts_client.py   # VieNeu-TTS SDK wrapper
│   │   │   ├── tts_service.py  # TTS generation orchestration
│   │   │   ├── audio_store.py  # Audio file storage + serving
│   │   │   └── queue.py        # Background job management
│   │   └── prompts/
│   │       ├── analyze.py      # Analysis prompt templates
│   │       ├── translate.py    # Translation prompt templates (incl. emotion cues)
│   │       └── research.py     # Research prompt templates
│   ├── audio/                  # Generated audio files (gitignored)
│   │   └── {project_id}/{chapter_id}/
│   │       ├── audio.wav
│   │       ├── audio.mp3
│   │       └── timeline.json
│   └── tests/
│       ├── test_extractor.py
│       ├── test_chapter_splitter.py
│       ├── test_analyzer.py
│       ├── test_translator.py
│       └── test_tts_service.py
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── components/
│   │   │   ├── UploadPanel.tsx
│   │   │   ├── ChapterList.tsx
│   │   │   ├── AnalysisView.tsx
│   │   │   ├── CharacterGraph.tsx  # reactflow
│   │   │   ├── TranslationView.tsx  # incl. emotion cue edit
│   │   │   ├── GlossaryEditor.tsx
│   │   │   ├── AudioPlayer.tsx     # play/pause/seek/speed/skip
│   │   │   ├── TextSync.tsx        # karaoke highlight
│   │   │   ├── VoiceSelector.tsx   # preset voices + style
│   │   │   └── Layout.tsx
│   │   ├── hooks/
│   │   │   ├── useUpload.ts
│   │   │   ├── useTranslation.ts  # SSE consumer
│   │   │   ├── useAudio.ts        # audio playback state
│   │   │   ├── useTimeline.ts     # karaoke sync
│   │   │   └── useProject.ts
│   │   ├── api/
│   │   │   └── client.ts
│   │   └── types/
│   │       └── index.ts
│   └── index.html
├── tasks/
│   ├── plan.md    (this file)
│   └── todo.md
└── README.md
```

## Task List

### Phase 1: Foundation — Backend Core

- [x] **Task 1:** Project scaffold + backend setup (uv, FastAPI, SQLModel)
- [x] **Task 2:** Database models + project management API
- [x] **Task 3:** PDF/text extraction service (PyMuPDF + RapidOCR auto-detect)
- [x] **Task 4:** Chapter detection service (regex-based + LLM-assisted)

### Checkpoint: Foundation
- [x] Backend runs, DB initialized, can upload PDF and see extracted chapters

### Phase 2: LLM Integration — Analysis Pipeline

- [x] **Task 5:** Ollama client wrapper + config
- [x] **Task 6:** Story analyzer service (summary + character extraction)
- [x] **Task 7:** Relationship mapper (character graph data)
- [x] **Task 8:** Translation service (context-aware, streaming, emotion cues)

### Checkpoint: LLM Pipeline
- [x] End-to-end: upload → analyze → translate → JSON output (via API only)

### Phase 3: Frontend — Web UI

- [ ] **Task 9:** Frontend scaffold (Vite + React + TS + Tailwind)
- [ ] **Task 10:** Upload panel + project list UI
- [ ] **Task 11:** Chapter manager UI (view, edit, reorder)
- [ ] **Task 12:** Analysis view (summary + character graph with reactflow)
- [ ] **Task 13:** Translation view (SSE streaming, emotion cue edit)

### Checkpoint: Web UI
- [ ] Full flow works in browser: upload → analyze → translate → view results

### Phase 4: Enhancement — Research & Glossary

- [ ] **Task 14:** Glossary manager service + API (CRUD, persist per project)
- [ ] **Task 15:** DuckDuckGo web search service (character research)
- [ ] **Task 16:** Research enrichment integration (combine glossary + web + LLM)
- [ ] **Task 17:** Glossary editor UI
- [ ] **Task 18:** Context carry across chapters (running glossary)

### Checkpoint: Full Pipeline
- [ ] Glossary + research enhances translation quality
- [ ] Multi-chapter context preserved

### Phase 5: Polish

- [ ] **Task 19:** Export structured JSON output
- [ ] **Task 20:** Error handling + retry logic (OCR failures, LLM timeouts, TTS failures)
- [ ] **Task 21:** Settings UI (model selection, OCR engine toggle, TTS voice/style)
- [ ] **Task 22:** README + setup instructions

### Checkpoint: Polish
- [ ] Error handling robust
- [ ] Settings configurable
- [ ] Setup documented

### Phase 6: TTS Integration — Audio Generation & Playback

- [ ] **Task 23:** VieNeu-TTS service wrapper (vieneu SDK, voices, styles, streaming)
- [ ] **Task 24:** Emotion cue injection in translation (LLM auto-inject + user edit)
- [ ] **Task 25:** TTS generation service (per chapter, segment-by-segment, timeline tracking)
- [ ] **Task 26:** Audio storage + serving (WAV/MP3, seekable streaming, download)
- [ ] **Task 27:** Audio player UI + auto-next chapter
- [ ] **Task 28:** Text sync (karaoke) — highlight + click-seek

### Checkpoint: TTS Integration
- [ ] Generate TTS from translated chapter → playable audio
- [ ] Karaoke text sync works
- [ ] Auto-next chapter works
- [ ] Both WAV + MP3 available
- [ ] Emotion cues audible in audio

### Checkpoint: Complete
- [ ] All acceptance criteria met
- [ ] Ready for use

## New DB Models (Phase 6)

```python
class AudioFile(SQLModel, table=True):
    id: int | None = Field(primary_key=True)
    chapter_id: int = Field(foreign_key="chapter.id")
    voice: str                    # preset voice name
    style: str                    # tu_nhien | tin_tuc | doc_truyen
    file_path_wav: str
    file_path_mp3: str
    duration_sec: float
    segment_count: int
    created_at: datetime

class AudioTimeline(SQLModel, table=True):
    id: int | None = Field(primary_key=True)
    audio_file_id: int = Field(foreign_key="audiofile.id")
    segment_index: int
    text: str                    # text of this segment
    start_time: float            # seconds
    end_time: float              # seconds
```

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Ollama chưa cài trên máy | High | Task 1 includes setup instructions + health check endpoint. Document install steps |
| OCR chất lượng thấp cho scanned PDF | Med | RapidOCR (PaddleOCR-based) tốt hơn Tesseract cho đa ngôn ngữ. Allow manual text input as fallback |
| LLM context window overflow với chương dài | Med | Split chapters into chunks (~2000 tokens). Carry running summary + glossary between chunks |
| DuckDuckGo rate limiting | Low | Cache search results. Graceful degradation — if search fails, use LLM knowledge only |
| Translation quality inconsistent | Med | Structured prompts with explicit context (summary + characters + glossary). Allow user edit/refine |
| Python 3.14 compatibility (very new) | Low | Pin dependencies in pyproject.toml. Use uv for reproducible env |
| SSE on Windows (FastAPI) | Low | Use `sse-starlette` package, tested cross-platform |
| `vieneu` SDK slow on CPU cho chương dài | Med | Segment-by-segment generation + background job + progress SSE. int8 precision default |
| MP3 encoding cần ffmpeg | Low | Check ffmpeg on startup. Fallback: serve WAV only, warn user |
| Karaoke sync drift | Low | Sentence-level sync (not word-level). Re-sync on seek. Tolerate <200ms drift |
| Memory: Ollama (7B) + VieNeu-TTS cùng chạy | Med | Sequential processing: TTS after translation complete. Or separate processes |
| `vieneu` package Python 3.14 compat | Med | Pin version. Test early. Fallback: Python 3.12 venv if issues |
| Audio file storage grows large | Low | Config max storage. Cleanup old audio. Compress to MP3 128kbps |

## Open Questions

1. **Model default:** Start with Qwen2.5 7B (better đa ngôn ngữ support than Llama 3.1 8B) — confirm OK?
2. **Memory:** 8GB RAM đủ cho 7-8B quantized model? Kiểm tra khi setup Ollama
3. **Chunk strategy:** Chương dài → split theo paragraph hay theo token count? (Default: token count ~2000)
4. **Honorifics policy:** Giữ nguyên (san, sama, kun) hay dịch sang Việt? (Default: glossary-driven, keep if not in glossary)
5. **Web search scope:** Search toàn web hay giới hạn wiki/fandom sites? (Default: toàn web, LLM filter results)
6. **ffmpeg:** Có sẵn trên máy không? Cần check — nếu không có, cài qua `winget install ffmpeg` hoặc `scoop install ffmpeg`
7. **Voice default:** `Phạm Tuyên` (storytelling Bắc) hay `Trúc Ly` (storytelling Nam)? — chọn theo preference
8. **Segment granularity:** Sentence-level (mỗi câu 1 segment) hay paragraph-level? — default: sentence, configurable
9. **TTS + LLM cùng lúc:** Chạy song song hay sequential? — default: sequential (translation xong → TTS), tránh memory pressure
