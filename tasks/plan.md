# Implementation Plan: Kanzaru — Story Translation App

## Overview

Web app dịch truyện đa ngôn ngữ → Việt. Input: PDF (text + scanned) hoặc raw text. Pipeline: extract text → detect chapters → pre-analyze (summary + characters + relationships) → context-aware translation → structured JSON output → TTS audio generation (VieNeu-TTS). Chạy local LLM qua Ollama, không cần API key.

## Architecture Decisions

### Stack
- **Backend:** Python 3.12 + FastAPI + uv (package manager)
- **Frontend:** React + Vite + TypeScript + Tailwind CSS
- **LLM:** Ollama local — Qwen2.5 7B
- **TTS:** VieNeu-TTS v3 Turbo (`vieneu` SDK) — CPU ONNX, 48kHz, 14 preset voices
- **DB:** SQLite via SQLModel
- **OCR:** RapidOCR (PaddleOCR-based)
- **PDF:** PyMuPDF (fitz)
- **Streaming:** Server-Sent Events (SSE) cho extraction + translation + TTS progress
- **Audio:** WAV + MP3 (ffmpeg)

### Pipeline Design
```
Upload PDF/Text
    │
    ▼
[1] Text Extraction (async, SSE progress)
    ├ File saved to disk → chapter status=processing
    ├ SSE endpoint streams page-by-page progress
    ├ Text PDF → PyMuPDF
    └ Scanned PDF → RapidOCR (async via to_thread)
    │
    ▼
[2] Chapter Detection
    ├ Auto: regex patterns (Chương X, 第X章, Chapter X, etc.)
    └ Manual: user adjusts in UI
    │
    ▼
[3] Pre-Translation Analysis (per chapter)
    ├ Summary, characters, honorifics
    ├ Relationship mapping
    └ Genre + sample translation stored per project
    │
    ▼
[4] Translation (per chapter)
    ├ Fast mode: single-pass streaming via SSE
    ├ Quality mode: 3-step (rough → critique → final)
    ├ Context: summary + characters + relationships + glossary + genre + sample
    ├ Persona prompt (dịch giả văn học 20 năm kinh nghiệm)
    ├ Constraints (thành ngữ, honorifics, no summarize)
    └ Emotion cues auto-injected
    │
    ▼
[5] Structured JSON Output
    │
    ▼
[6] TTS Generation (planned)
```

## Task List

### Phase 1: Foundation — Backend Core

- [x] **Task 1:** Project scaffold + backend setup
- [x] **Task 2:** Database models + project management API
- [x] **Task 3:** PDF/text extraction service (PyMuPDF + RapidOCR)
- [x] **Task 4:** Chapter detection service (regex-based)

### Checkpoint: Foundation — DONE

### Phase 2: LLM Integration — Analysis Pipeline

- [x] **Task 5:** Ollama client wrapper + config
- [x] **Task 6:** Story analyzer service (summary + character extraction)
- [x] **Task 7:** Relationship mapper (character graph data)
- [x] **Task 8:** Translation service (context-aware, streaming, emotion cues)

### Checkpoint: LLM Pipeline — DONE

### Phase 3: Frontend — Web UI

- [x] **Task 9:** Frontend scaffold (Vite + React + TS + Tailwind)
- [x] **Task 10:** Upload panel + project list UI
- [x] **Task 11:** Chapter manager UI (list, detail, edit, status badges)
- [x] **Task 12:** Analysis view (summary + character graph with reactflow)
- [x] **Task 13:** Translation view (SSE streaming, emotion cue edit)

### Checkpoint: Web UI — DONE

### Phase 3.5: Infrastructure & UX Fixes

- [x] **Task 14:** DB migration system (auto-add missing columns on startup)
- [x] **Task 15:** Toast notification system (global success/error feedback)
- [x] **Task 16:** Async upload + SSE extraction (save file to disk, stream progress)
- [x] **Task 17:** Relationships wired into translation context

### Checkpoint: Infrastructure — DONE

### Phase 4: Translation Quality Enhancement

- [x] **Task 18:** Professional translation prompt (persona, genre, constraints, few-shot)
- [x] **Task 19:** 3-step translation mode (rough → critique → final)
- [x] **Task 20:** Project fields for genre + sample translation

### Checkpoint: Translation Quality — DONE

### Phase 5: Enhancement — Research & Glossary

- [ ] **Task 21:** Glossary manager service + API (CRUD, persist per project)
- [ ] **Task 22:** DuckDuckGo web search service (character research)
- [ ] **Task 23:** Research enrichment integration (combine glossary + web + LLM)
- [ ] **Task 24:** Glossary editor UI
- [ ] **Task 25:** Context carry across chapters (running glossary)

### Checkpoint: Full Pipeline
- [ ] Glossary + research enhances translation quality
- [ ] Multi-chapter context preserved

### Phase 6: Polish

- [ ] **Task 26:** Export structured JSON output
- [ ] **Task 27:** Error handling + retry logic (OCR failures, LLM timeouts)
- [ ] **Task 28:** Settings UI (model selection, OCR engine toggle, TTS voice/style)
- [ ] **Task 29:** README + setup instructions

### Checkpoint: Polish
- [ ] Error handling robust
- [ ] Settings configurable
- [ ] Setup documented

### Phase 7: TTS Integration — Audio Generation & Playback

- [ ] **Task 30:** VieNeu-TTS service wrapper
- [ ] **Task 31:** TTS generation service (per chapter, segment-by-segment)
- [ ] **Task 32:** Audio storage + serving (WAV/MP3, seekable streaming)
- [ ] **Task 33:** Audio player UI + auto-next chapter
- [ ] **Task 34:** Text sync (karaoke) — highlight + click-seek

### Checkpoint: TTS Integration
- [ ] Generate TTS from translated chapter → playable audio
- [ ] Karaoke text sync works
- [ ] Both WAV + MP3 available

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Ollama chưa cài trên máy | High | Health check endpoint + setup docs |
| OCR chất lượng thấp | Med | RapidOCR + manual text fallback |
| LLM context overflow chương dài | Med | Chunk ~8000 chars, carry context |
| Translation quality inconsistent | Med | 3-step translation mode + persona prompt + few-shot |
| `vieneu` SDK Python 3.12 compat | Med | Pin version, test early |
| Memory: Ollama + TTS cùng chạy | Med | Sequential processing |
| SSE on Windows | Low | `sse-starlette`, tested |

## Open Questions

1. **Model default:** Qwen2.5 7B — confirmed
2. **Chunk strategy:** Token count ~8000 chars — working
3. **Honorifics policy:** Glossary-driven, keep if not in glossary — confirmed
4. **Translation modes:** Fast (streaming) vs Quality (3-step) — both implemented
5. **Genre + sample:** Stored per-project, passed to prompt — implemented
