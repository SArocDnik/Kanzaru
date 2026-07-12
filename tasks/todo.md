# Kanzaru — Task Checklist

## Phase 1: Foundation — Backend Core

### Task 1: Project scaffold + backend setup

**Description:** Init backend project, FastAPI, SQLModel. Cấu trúc thư mục, config, dev server.

- [x] `pyproject.toml` với dependencies: fastapi, uvicorn, sqlmodel, pymupdf, rapidocr-onnxruntime, ollama, httpx, sse-starlette, python-multipart, pillow, pydantic-settings
- [x] FastAPI app chạy tại `localhost:8000`, health check `/health`
- [x] SQLite DB auto-init on startup
- [x] Config via environment variables (KANZARU_ prefix)
- [x] CORS enabled cho `localhost:5173`
- [x] Root `package.json` với `concurrently` để chạy song song backend + frontend

**Files:**
- `backend/pyproject.toml`
- `backend/src/main.py`
- `backend/src/config.py`
- `package.json` (root, concurrently)

---

### Task 2: Database models + project management API

**Description:** SQLModel tables + REST API CRUD cho Project.

- [x] Tables: `Project`, `Chapter`, `Character`, `GlossaryEntry`, `CharacterRelationship`, `AudioFile`, `AudioTimeline`
- [x] `Project` model có: name, source_lang, target_lang, genre, sample_original, sample_translated
- [x] `Chapter` model có: file_path, status (pending/processing/uploaded/detected/analyzed/translated)
- [x] `POST /projects`, `GET /projects`, `GET /projects/{id}`, `DELETE /projects/{id}`
- [x] DB migrations auto-run on startup (`_migrate()` adds missing columns)

**Files:**
- `backend/src/models/db.py`
- `backend/src/models/schemas.py`
- `backend/src/api/routes/projects.py`
- `backend/src/api/deps.py`

---

### Task 3: PDF/text extraction service

**Description:** Extract text từ PDF (text-based + scanned) và raw text. OCR auto-detect.

- [x] `extract_from_pdf(file) -> list[PageText]` — PyMuPDF
- [x] Auto-detect: <50 chars/page → OCR
- [x] `extract_with_ocr(file) -> list[PageText]` — RapidOCR
- [x] `extract_from_text(content) -> list[PageText]`
- [x] `extract_pdf_streaming(file_path) -> AsyncIterator[ExtractProgress]` — async, per-page yield, OCR via `asyncio.to_thread`
- [x] `POST /projects/{id}/upload` — file saved to disk, chapter status=processing
- [x] `GET /chapters/{id}/extract/stream` — SSE streams extraction progress

**Files:**
- `backend/src/services/extractor.py`
- `backend/src/api/routes/upload.py`
- `backend/tests/test_extractor.py`
- `backend/tests/test_upload.py`

---

### Task 4: Chapter detection service

**Description:** Detect chapter boundaries từ extracted text. Regex patterns đa ngôn ngữ.

- [x] Regex: `Chương \d+`, `第.+章`, `Chapter \d+`, `第.+話`, `第.+回`
- [x] `detect_chapters(text, lang_hint) -> list[Chapter]`
- [x] `POST /projects/{id}/chapters/detect` — auto-detect + store
- [x] `GET /projects/{id}/chapters` — list
- [x] `PUT /chapters/{id}` — edit
- [x] `POST /projects/{id}/chapters` — manual add
- [x] `DELETE /chapters/{id}` — delete
- [ ] LLM-assisted fallback khi không match pattern

**Files:**
- `backend/src/services/chapter_splitter.py`
- `backend/src/api/routes/chapters.py`
- `backend/tests/test_chapter_splitter.py`

---

## Checkpoint: Foundation — DONE

---

### Task 5: Ollama client wrapper

**Description:** Wrapper cho Ollama Python client.

- [x] `LLMClient` class: `health_check()`, `list_models()`, `chat()`, `stream()`
- [x] Config: Ollama URL from env
- [x] Default model: Qwen2.5 7B
- [x] `GET /llm/health`, `GET /llm/models`

**Files:**
- `backend/src/services/llm_client.py`
- `backend/src/api/routes/llm.py`

---

### Task 6: Story analyzer service

**Description:** LLM-powered analysis: tóm tắt + extract nhân vật + xưng hô.

- [x] `analyze_chapter(text, lang) -> AnalysisResult` (summary, characters, key_terms)
- [x] Structured JSON prompt
- [x] `POST /chapters/{id}/analyze` — trigger analysis
- [x] `GET /chapters/{id}/analysis` — get stored analysis

**Files:**
- `backend/src/services/analyzer.py`
- `backend/src/prompts/analyze.py`
- `backend/src/api/routes/chapters.py`
- `backend/tests/test_analyzer.py`

---

### Task 7: Relationship mapper

**Description:** Build character relationship graph.

- [x] `map_relationships(characters, text) -> list[Relationship]`
- [x] Relationship types: family, romantic, friendship, rivalry, master_servant, other
- [x] `GET /projects/{id}/characters`, `GET /projects/{id}/relationships`
- [x] Merge duplicates across chapters
- [x] Relationships included in translation context (`_build_context()`)

**Files:**
- `backend/src/services/analyzer.py`
- `backend/src/prompts/analyze.py`
- `backend/src/api/routes/characters.py`

---

### Task 8: Translation service (context-aware, streaming, emotion cues)

**Description:** Core translation. Context-aware, SSE streaming, emotion cues.

- [x] `translate_chapter(text, ctx) -> str`
- [x] `translate_chapter_stream(text, ctx) -> AsyncGenerator[str]` — SSE streaming
- [x] Chunk long chapters (>8000 chars) → translate per chunk → stitch
- [x] Emotion cues auto-injected: `[cười]`, `[thở dài]`, etc.
- [x] `POST /chapters/{id}/translate` — non-streaming
- [x] `GET /chapters/{id}/translate/stream` — SSE streaming
- [x] `GET /chapters/{id}/translation` — get stored
- [x] `PUT /chapters/{id}/translation` — user edit

**Files:**
- `backend/src/services/translator.py`
- `backend/src/prompts/translate.py`
- `backend/src/api/routes/translate.py`
- `backend/tests/test_translator.py`

---

## Checkpoint: LLM Pipeline — DONE

---

### Task 9: Frontend scaffold

- [x] Vite + React + TS + Tailwind
- [x] API client (fetch wrapper)
- [x] Layout: sidebar + main content
- [x] React Router, TanStack Query
- [x] `npm run dev` at `localhost:5173`

**Files:**
- `frontend/package.json`, `frontend/vite.config.ts`
- `frontend/src/App.tsx`, `frontend/src/main.tsx`
- `frontend/src/api/client.ts`, `frontend/src/components/Layout.tsx`

---

### Task 10: Upload panel + project list UI

- [x] Project list: cards with name, lang pair, status
- [x] New project creation
- [x] Upload panel: drag-drop PDF or paste text
- [x] Upload success feedback (toast + inline message)
- [x] Navigate to chapter detail after file upload (for extraction progress)

**Files:**
- `frontend/src/components/UploadPanel.tsx`
- `frontend/src/components/ProjectList.tsx`
- `frontend/src/hooks/useUpload.ts`, `useProject.ts`
- `frontend/src/types/index.ts`

---

### Task 11: Chapter manager UI

- [x] Chapter list: numbers + titles + status badges + char count
- [x] Chapter detail: original text view, edit title/text
- [x] Detect chapters button (with toast feedback)
- [x] Delete chapter (with toast feedback)
- [x] Workflow guidance banner ("Next: Analyze..." / "Next: Translate...")
- [x] SSE extraction progress bar (auto-connect when status=processing)
- [x] Stop extraction button

**Files:**
- `frontend/src/components/ChapterList.tsx`
- `frontend/src/components/ChapterDetail.tsx`
- `frontend/src/hooks/useChapters.ts`, `useExtractStream.ts`

---

### Task 12: Analysis view (summary + character graph)

- [x] Summary panel
- [x] Character graph: nodes + edges (reactflow)
- [x] Click character → side panel with details
- [x] Analyze button (with toast feedback)
- [x] Map relationships button (with toast feedback)

**Files:**
- `frontend/src/components/AnalysisView.tsx`
- `frontend/src/components/CharacterGraph.tsx`
- `frontend/src/hooks/useAnalysis.ts`

---

### Task 13: Translation view (SSE streaming, emotion cue edit)

- [x] Translate button → SSE stream
- [x] Progressive display (word by word)
- [x] Toggle: original / translated / side-by-side
- [x] Re-translate (with confirmation)
- [x] Edit mode: textarea with emotion cue highlighting
- [x] Save edited translation
- [x] Stream completion toast

**Files:**
- `frontend/src/components/TranslationView.tsx`
- `frontend/src/hooks/useTranslation.ts`

---

## Checkpoint: Web UI — DONE

---

### Task 14: DB migration system

**Description:** Auto-migrate SQLite schema on startup. Add missing columns to existing tables.

- [x] `_migrate()` in `deps.py`: checks `PRAGMA table_info()` + `ALTER TABLE ADD COLUMN`
- [x] Migrates: `chapter.file_path`, `project.genre`, `project.sample_original`, `project.sample_translated`
- [x] Test: `test_migration.py` — creates old schema, runs `init_db()`, asserts new columns exist

**Files:**
- `backend/src/api/deps.py`
- `backend/tests/test_migration.py`

---

### Task 15: Toast notification system

**Description:** Global toast provider for success/error feedback across all components.

- [x] `ToastContext.tsx` — context + provider, auto-dismiss (4s), fixed bottom-right
- [x] Toast types: success (green), error (red), info (slate)
- [x] Wired into: UploadPanel, ChapterList, ChapterDetail, AnalysisView, TranslationView
- [x] `App.tsx` wrapped with `<ToastProvider>`

**Files:**
- `frontend/src/contexts/ToastContext.tsx`
- `frontend/src/App.tsx`
- All component files (toast usage)

---

### Task 16: Async upload + SSE extraction

**Description:** Upload saves file to disk, returns immediately. Extraction streams via SSE.

- [x] Upload endpoint: `shutil.copyfileobj` to `uploads/{project_id}/`, chapter status=processing
- [x] SSE endpoint `GET /chapters/{id}/extract/stream`: streams per-page progress
- [x] `extract_pdf_streaming()` async generator: yields `ExtractProgress` per page
- [x] OCR runs via `asyncio.to_thread` (non-blocking)
- [x] Frontend: `useExtractStream` hook (SSE client)
- [x] ChapterDetail auto-connects SSE when status=processing
- [x] Progress bar with page count, method, char count

**Files:**
- `backend/src/api/routes/upload.py`
- `backend/src/services/extractor.py`
- `frontend/src/hooks/useExtractStream.ts`
- `frontend/src/components/ChapterDetail.tsx`
- `frontend/src/components/UploadPanel.tsx`

---

### Task 17: Relationships in translation context

**Description:** Wire character relationships into translation prompt for dialogue tone accuracy.

- [x] `TranslationContext.relationships` field
- [x] `_build_context()` queries `CharacterRelationship` table
- [x] Relationships formatted as `A — B (type): description`
- [x] Translation prompt includes relationship section + tone instruction

**Files:**
- `backend/src/services/translator.py`
- `backend/src/prompts/translate.py`
- `backend/src/api/routes/translate.py`

---

## Checkpoint: Infrastructure — DONE

---

### Task 18: Professional translation prompt (persona, genre, constraints, few-shot)

**Description:** Rewrite prompt with 5 professional translation techniques.

- [x] **Persona:** "Bạn là dịch giả văn học chính thống, 20 năm kinh nghiệm..."
- [x] **Context:** Genre from project, sample_original/translated for few-shot
- [x] **Constraints:** Thành ngữ→tương đương, giữ tên riêng, KHÔNG tóm tắt câu dài, honorifics, quan hệ→ngôn xưng
- [x] **Few-shot:** Project `sample_original` + `sample_translated` → "Hãy dịch theo phong cách tương tự"
- [x] Prompt rewritten entirely in Vietnamese
- [x] Tests: persona, genre, constraints, sample in prompt

**Files:**
- `backend/src/prompts/translate.py`
- `backend/src/services/translator.py`
- `backend/tests/test_translator.py`

---

### Task 19: 3-step translation mode (rough → critique → final)

**Description:** Multi-turn LLM conversation: rough translation → self-critique → final polished translation.

- [x] `ROUGH_PROMPT`, `CRITIQUE_PROMPT`, `FINAL_PROMPT` templates
- [x] `build_3step_prompts(text, ctx) -> list[str]` — returns 3 prompts
- [x] `translate_chapter_3step(text, ctx, client) -> str` — 3 LLM calls per chunk, multi-turn
- [x] `POST /chapters/{id}/translate/quality` endpoint
- [x] Tests: `build_3step_prompts` returns 3, `translate_chapter_3step` returns final only, 3 chat calls

**Files:**
- `backend/src/prompts/translate.py`
- `backend/src/services/translator.py`
- `backend/src/api/routes/translate.py`
- `backend/tests/test_translator.py`

---

### Task 20: Project fields for genre + sample translation

**Description:** Add genre + sample_original + sample_translated to Project model.

- [x] `Project` model: `genre`, `sample_original`, `sample_translated` fields
- [x] `ProjectCreate`, `ProjectRead`, `ProjectUpdate` schemas updated
- [x] Migration adds columns to existing DB
- [x] `_build_context()` passes genre + sample to `TranslationContext`
- [x] Tests: migration adds columns, prompt includes genre + sample

**Files:**
- `backend/src/models/db.py`
- `backend/src/models/schemas.py`
- `backend/src/api/deps.py`
- `backend/src/api/routes/translate.py`
- `backend/tests/test_migration.py`

---

## Checkpoint: Translation Quality — DONE

---

### Task 21: Glossary manager service + API

- [ ] CRUD for `GlossaryEntry` (term, translation, notes)
- [ ] `POST /projects/{id}/glossary`, `GET`, `PUT`, `DELETE`
- [ ] Bulk import (JSON/CSV)
- [ ] Glossary passed to translator (already wired in `_build_context()`)

### Task 22: DuckDuckGo web search service

- [ ] `search_ddg(query) -> list[SearchResult]`
- [ ] Cache results in SQLite
- [ ] Rate limiting: 1 req/sec
- [ ] `POST /characters/{id}/research`, `GET /characters/{id}/research`

### Task 23: Research enrichment integration

- [ ] `enrich_context(chapter_id) -> EnrichedContext`
- [ ] Merge: glossary + web search + LLM knowledge
- [ ] `POST /chapters/{id}/enrich`

### Task 24: Glossary editor UI

- [ ] Glossary table: term, translation, notes
- [ ] Add/edit/delete, import modal
- [ ] Search/filter

### Task 25: Context carry across chapters

- [ ] Running glossary accumulates across chapters
- [ ] Translating chapter N+1 includes context from 1..N
- [ ] `GET /projects/{id}/context`

---

## Checkpoint: Full Pipeline
- [ ] Glossary + research enhances translation
- [ ] Multi-chapter context preserved

---

### Task 26: Export structured JSON output

- [ ] `GET /projects/{id}/export` — JSON
- [ ] Frontend download button

### Task 27: Error handling + retry logic

- [ ] OCR failure → fallback → notification
- [ ] LLM timeout → retry (max 3) → notification
- [ ] All errors logged

### Task 28: Settings UI

- [ ] Model dropdown, OCR engine toggle
- [ ] TTS voice/style selector
- [ ] Ollama URL field

### Task 29: README + setup instructions

- [ ] Prerequisites, install, run, usage guide
- [ ] Troubleshooting

---

## Checkpoint: Polish
- [ ] Error handling robust
- [ ] Settings configurable
- [ ] Setup documented

---

### Task 30: VieNeu-TTS service wrapper

- [ ] `vieneu` SDK, `TTSClient` class
- [ ] `GET /tts/health`, `GET /tts/voices`

### Task 31: TTS generation service

- [ ] `generate_chapter_audio(chapter_id, voice, style)`
- [ ] Split by sentence → generate per segment → timeline
- [ ] Save WAV + MP3, store AudioFile + AudioTimeline
- [ ] `POST /chapters/{id}/tts`, SSE progress

### Task 32: Audio storage + serving

- [ ] `backend/audio/{project_id}/{chapter_id}/`
- [ ] Seekable streaming, download
- [ ] Cascade delete with project

### Task 33: Audio player UI

- [ ] Play/pause/seek/speed/skip ±15s
- [ ] Voice selector, auto-next chapter

### Task 34: Text sync (karaoke)

- [ ] Highlight current segment synced with audio
- [ ] Click text → seek audio
- [ ] Auto-scroll

---

## Checkpoint: TTS Integration
- [ ] TTS from translated chapter → playable audio
- [ ] Karaoke text sync
- [ ] Auto-next chapter
- [ ] WAV + MP3 available

---

## Checkpoint: Complete
- [ ] All acceptance criteria met
- [ ] Ready for use
