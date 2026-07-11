# Kanzaru — Task Checklist

## Phase 1: Foundation — Backend Core

### Task 1: Project scaffold + backend setup

**Description:** Init backend project với uv, FastAPI, SQLModel. Cấu trúc thư mục, config, dev server chạy được.
**Acceptance criteria:**

- [x] `uv init` + `pyproject.toml` với dependencies: fastapi, uvicorn, sqlmodel, pymupdf, rapidocr-onnxruntime, ollama, httpx, sse-starlette, python-multipart, pillow, vieneu
- [x] FastAPI app chạy tại `localhost:8000`, health check endpoint `/health` trả `{"status": "ok"}`
- [x] SQLite DB auto-init on startup
- [x] Config via environment variables (OLLAMA_URL, DB_PATH, AUDIO_DIR, TTS_VOICE, TTS_STYLE, etc.)
- [x] CORS enabled cho `localhost:5173` (frontend dev)
  **Verification:**
- [x] `uv run uvicorn src.main:app --reload` starts without errors
- [x] `curl localhost:8000/health` returns 200
  **Dependencies:** None
  **Files likely touched:**

- `backend/pyproject.toml`
- `backend/src/main.py`
- `backend/src/config.py`
- `backend/src/models/db.py`
  **Estimated scope:** Small (3-4 files)

---

### Task 2: Database models + project management API

**Description:** SQLModel tables cho Project, Chapter, Character, GlossaryEntry, Translation, AudioFile, AudioTimeline. REST API CRUD cho Project.
**Acceptance criteria:**

- [x] Tables: `Project`, `Chapter`, `Character`, `GlossaryEntry`, `CharacterRelationship`, `AudioFile`, `AudioTimeline`
- [x] `POST /projects` — create project (name, source_lang, target_lang)
- [x] `GET /projects` — list all projects
- [x] `GET /projects/{id}` — get project detail
- [x] `DELETE /projects/{id}` — delete project + cascade
- [x] DB migrations auto-run on startup
  **Verification:**
- [x] Create project via API, verify in DB
- [x] Delete cascade works (chapters, characters, audio files deleted with project)
  **Dependencies:** Task 1
  **Files likely touched:**

- `backend/src/models/db.py`
- `backend/src/models/schemas.py`
- `backend/src/api/routes/projects.py`
- `backend/src/api/deps.py`
  **Estimated scope:** Medium (4 files)

---

### Task 3: PDF/text extraction service

**Description:** Service extract text từ PDF (text-based + scanned) và raw text input. Auto-detect nếu PDF là scanned → chạy OCR.
**Acceptance criteria:**

- [x] `extract_from_pdf(file) -> list[PageText]` — PyMuPDF extract
- [x] Auto-detect: nếu page có <50 chars → mark for OCR
- [x] `extract_with_ocr(file) -> list[PageText]` — RapidOCR
- [x] `extract_from_text(content) -> list[PageText]` — raw text input
- [ ] Tesseract fallback nếu RapidOCR fail
- [x] Return structured: `[{page_num, text, extraction_method}]`
- [x] `POST /upload` endpoint accepts PDF + text
  **Verification:**
- [x] Test với text PDF → extracts correctly
- [ ] Test với scanned PDF → OCR runs
- [x] Test với raw text → parses to pages
  **OCR Verification (Youjo Senki PDF):**
- [x] 403 pages total, pages 1-6 + 25 blank/cover → marked `needs_ocr`
- [x] Pages 7-24 text-based → extracted via PyMuPDF
- [x] Extracted text = EXACT MATCH with `example_1.txt` (ignoring whitespace)
  **Dependencies:** Task 1, Task 2
  **Files likely touched:**

- `backend/src/services/extractor.py`
- `backend/src/api/routes/upload.py`
- `backend/tests/test_extractor.py`
  **Estimated scope:** Medium (3 files)

---

### Task 4: Chapter detection service

**Description:** Detect chapter boundaries từ extracted text. Regex patterns cho đa ngôn ngữ + LLM-assisted fallback.
**Acceptance criteria:**

- [x] Regex patterns: `Chương \d+`, `第.+章`, `Chapter \d+`, `第.+話`, `第.+回`
- [x] `detect_chapters(text, lang_hint) -> list[Chapter]` returns chapters with title + content
- [ ] Fallback: nếu regex không match → LLM-assisted split (ask Ollama to find chapter boundaries)
- [x] `POST /projects/{id}/chapters/detect` — auto-detect + store
- [x] `GET /projects/{id}/chapters` — list chapters
- [x] `PUT /chapters/{id}` — edit chapter title/content
- [x] `POST /projects/{id}/chapters` — manual add chapter
- [x] `DELETE /chapters/{id}` — delete chapter
  **Verification:**
- [x] Test với Vietnamese novel → detects "Chương 1", "Chương 2"
- [x] Test với Japanese novel → detects "第1章"
- [x] Test với English → detects "Chapter 1"
- [ ] Fallback works when no patterns found
  **Dependencies:** Task 2, Task 3
  **Files likely touched:**

- `backend/src/services/chapter_splitter.py`
- `backend/src/api/routes/chapters.py`
- `backend/tests/test_chapter_splitter.py`
  **Estimated scope:** Medium (3 files)

---

## Checkpoint: Foundation

- [x] Backend runs without errors
- [x] DB initialized with all tables
- [x] Upload PDF → extract text → detect chapters → view in API
- [x] All tests pass: `uv run pytest`

---

### Task 5: Ollama client wrapper

**Description:** Wrapper cho Ollama Python client. Health check, model listing, chat + streaming.
**Acceptance criteria:**

- [x] `LLMClient` class with: `health_check()`, `list_models()`, `chat(model, messages)`, `stream(model, messages)`
- [x] Config: Ollama URL from env (default `http://localhost:11434`)
- [x] Default model configurable (Qwen2.5 7B preferred for đa ngôn ngữ)
- [x] `GET /llm/health` — check Ollama running + model available
- [x] `GET /llm/models` — list available models
- [x] Error handling: clear message if Ollama not running
  **Verification:**
- [x] Health check returns model status
- [x] Can send simple prompt and get response
- [x] Streaming works (yield chunks)
  **Dependencies:** Task 1
  **Files likely touched:**

- `backend/src/services/llm_client.py`
- `backend/src/api/routes/llm.py`
  **Estimated scope:** Small (2 files)

---

### Task 6: Story analyzer service

**Description:** LLM-powered analysis: tóm tắt chương + extract nhân vật + xưng hô. Input: chapter text. Output: summary + character list.
**Acceptance criteria:**

- [x] `analyze_chapter(text, lang) -> AnalysisResult` returns:
  - `summary`: tóm tắt nội dung (2-3 câu)
  - `characters`: `[{name, aliases, role, honorifics_used}]`
  - `key_terms`: thuật ngữ quan trọng cần注意
- [x] Prompt template asks LLM to output structured JSON
- [x] Parse LLM response → validate → store in DB
- [x] `POST /chapters/{id}/analyze` — trigger analysis
- [x] `GET /chapters/{id}/analysis` — get stored analysis
  **Verification:**
- [x] Test với sample chapter → returns meaningful summary
- [x] Character names extracted correctly
- [x] Honorifics detected (san, sama, kun, etc.)
  **Dependencies:** Task 4, Task 5
  **Files likely touched:**

- `backend/src/services/analyzer.py`
- `backend/src/prompts/analyze.py`
- `backend/src/api/routes/chapters.py` (extend)
- `backend/tests/test_analyzer.py`
  **Estimated scope:** Medium (4 files)

---

### Task 7: Relationship mapper

**Description:** Build character relationship graph từ analysis data. Identify quan hệ (family, friend, rival, master-servant, etc.).
**Acceptance criteria:**

- [x] `map_relationships(characters, chapter_text) -> list[Relationship]`
- [x] Relationship types: family, romantic, friendship, rivalry, master_servant, other
- [x] `GET /projects/{id}/characters` — all characters across chapters
- [x] `GET /projects/{id}/relationships` — all relationships
- [x] LLM prompt extracts relationships from text
- [x] Merge duplicates across chapters (same character different chapter)
  **Verification:**
- [x] Test với multi-chapter text → relationships consistent
- [x] Graph data valid for frontend (nodes + edges)
  **Dependencies:** Task 6
  **Files likely touched:**

- `backend/src/services/analyzer.py` (extend)
- `backend/src/prompts/analyze.py` (extend)
- `backend/src/api/routes/characters.py`
  **Estimated scope:** Medium (3 files)

---

### Task 8: Translation service (context-aware, streaming, emotion cues)

**Description:** Core translation. Context-aware: uses summary + characters + glossary. Streaming via SSE. Auto-inject emotion cues cho TTS.
**Acceptance criteria:**

- [x] `translate_chapter(chapter_id, context) -> AsyncGenerator[str]` streams translated text
- [x] Prompt includes: chapter text + summary + character list + glossary + honorific rules
- [x] Chunk long chapters (>2000 tokens) → translate per chunk → stitch
- [x] Context carry: running glossary from previous chapters
- [x] Translation prompt instructs LLM to auto-inject emotion cues: `[cười]`, `[thở dài]`, `[hắng giọng]` where contextually appropriate
- [x] Cues match VieNeu-TTS format exactly
- [x] `POST /chapters/{id}/translate` — returns SSE stream
- [x] `GET /chapters/{id}/translation` — get stored translation
- [x] Translation stored in DB linked to chapter
- [x] `PUT /chapters/{id}/translation` — user edit translated text (add/remove cues)
  **Verification:**
- [x] SSE stream delivers translation progressively
- [x] Character names consistent across chapters
- [x] Honorifics handled per glossary rules
- [x] Long chapters handled without context overflow
- [x] Emotion cues present in translated text where appropriate
  **Dependencies:** Task 6, Task 7
  **Files likely touched:**

- `backend/src/services/translator.py`
- `backend/src/prompts/translate.py`
- `backend/src/api/routes/translate.py`
- `backend/tests/test_translator.py`
  **Estimated scope:** Medium (4 files)

---

## Checkpoint: LLM Pipeline

- [x] Full backend pipeline: upload → extract → detect chapters → analyze → translate → JSON
- [x] All API endpoints working
- [x] SSE streaming functional
- [x] Emotion cues in translated text
- [x] Tests pass

---

### Task 9: Frontend scaffold

**Description:** Init React + Vite + TypeScript + Tailwind. Basic layout, routing, API client.
**Acceptance criteria:**

- [ ] Vite + React + TS project created
- [ ] Tailwind CSS configured
- [ ] API client (`fetch` wrapper) with base URL config
- [ ] Basic layout: sidebar + main content area
- [ ] React Router setup (projects, upload, translate views)
- [ ] TanStack Query provider configured
  **Verification:**
- [ ] `npm run dev` starts at `localhost:5173`
- [ ] Can call backend `/health` from frontend
  **Dependencies:** None (parallel with Phase 1-2 possible)
  **Files likely touched:**

- `frontend/package.json`
- `frontend/vite.config.ts`
- `frontend/src/App.tsx`
- `frontend/src/main.tsx`
- `frontend/src/api/client.ts`
- `frontend/src/components/Layout.tsx`
  **Estimated scope:** Medium (5-6 files)

---

### Task 10: Upload panel + project list UI

**Description:** UI for creating projects, uploading PDF/text, viewing project list.
**Acceptance criteria:**

- [ ] Project list page: cards with name, lang pair, chapter count, status
- [ ] New project modal: name, source lang, target lang
- [ ] Upload panel: drag-drop PDF or paste text
- [ ] Upload progress indicator
- [ ] Navigate to project detail after upload
  **Verification:**
- [ ] Create project → appears in list
- [ ] Upload PDF → triggers extraction + chapter detection
- [ ] Chapters visible in project detail
  **Dependencies:** Task 9
  **Files likely touched:**

- `frontend/src/components/UploadPanel.tsx`
- `frontend/src/components/ProjectList.tsx`
- `frontend/src/hooks/useUpload.ts`
- `frontend/src/hooks/useProject.ts`
- `frontend/src/types/index.ts`
  **Estimated scope:** Medium (5 files)

---

### Task 11: Chapter manager UI

**Description:** View, edit, reorder chapters. Show original text per chapter.
**Acceptance criteria:**

- [ ] Chapter list: sidebar with chapter numbers + titles
- [ ] Chapter detail: original text view (scrollable)
- [ ] Edit chapter title
- [ ] Split/merge chapters manually
- [ ] Status badges: pending, analyzing, analyzed, translating, translated, tts_pending, tts_done
  **Verification:**
- [ ] Chapters load from API
- [ ] Edit saves to backend
- [ ] Status updates reflect in UI
  **Dependencies:** Task 10
  **Files likely touched:**

- `frontend/src/components/ChapterList.tsx`
- `frontend/src/components/ChapterDetail.tsx`
- `frontend/src/hooks/useChapters.ts`
  **Estimated scope:** Medium (3 files)

---

### Task 12: Analysis view (summary + character graph)

**Description:** Display story summary + character relationship graph using reactflow.
**Acceptance criteria:**

- [ ] Summary panel: shows chapter summary
- [ ] Character graph: nodes = characters, edges = relationships (labeled)
- [ ] Click character → side panel with details (name, role, honorifics, appearances)
- [ ] Graph auto-layout (force-directed or hierarchical)
- [ ] Color-coded relationship types
  **Verification:**
- [ ] Graph renders from API data
- [ ] Interactive: click, hover, zoom, pan
- [ ] Character details accurate
  **Dependencies:** Task 11
  **Files likely touched:**

- `frontend/src/components/AnalysisView.tsx`
- `frontend/src/components/CharacterGraph.tsx`
- `frontend/src/hooks/useAnalysis.ts`
  **Estimated scope:** Medium (3 files)

---

### Task 13: Translation view (SSE streaming, emotion cue edit)

**Description:** View displaying streaming translation. Side-by-side or tab toggle original/translated. Edit emotion cues trước khi TTS.
**Acceptance criteria:**

- [ ] "Translate" button triggers SSE stream
- [ ] Translation appears progressively (word by word)
- [ ] Progress bar (chapter chunk X/Y)
- [ ] Toggle: original only / translated only / side-by-side
- [ ] Translation stored — reload shows cached translation
- [ ] Re-translate button (with confirmation)
- [ ] Edit mode: textarea to add/remove emotion cues `[cười]`, `[thở dài]`, `[hắng giọng]`
- [ ] Emotion cues highlighted in edit mode (distinct color)
- [ ] Save edited translation to backend
  **Verification:**
- [ ] SSE stream works in browser
- [ ] Translation appears in real-time
- [ ] Page reload shows stored translation
- [ ] Emotion cues visible + editable
- [ ] Save persists changes
  **Dependencies:** Task 12
  **Files likely touched:**

- `frontend/src/components/TranslationView.tsx`
- `frontend/src/hooks/useTranslation.ts`
  **Estimated scope:** Medium (2-3 files)

---

## Checkpoint: Web UI

- [ ] Full browser flow: upload → detect chapters → analyze → translate → view
- [ ] SSE streaming works end-to-end
- [ ] Character graph interactive
- [ ] Emotion cues visible + editable
- [ ] No console errors

---

### Task 14: Glossary manager service + API

**Description:** CRUD for glossary entries (term, translation, notes, context). Per-project storage.
**Acceptance criteria:**

- [ ] `GlossaryEntry` model: term, translation, source_lang, notes, project_id
- [ ] `POST /projects/{id}/glossary` — add entry
- [ ] `GET /projects/{id}/glossary` — list entries
- [ ] `PUT /glossary/{id}` — update
- [ ] `DELETE /glossary/{id}` — delete
- [ ] `POST /projects/{id}/glossary/import` — bulk import (JSON/CSV)
- [ ] Glossary passed to translator as context
  **Verification:**
- [ ] CRUD operations work
- [ ] Glossary terms used in translation prompts
  **Dependencies:** Task 8
  **Files likely touched:**

- `backend/src/models/db.py` (extend)
- `backend/src/models/schemas.py` (extend)
- `backend/src/api/routes/glossary.py`
  **Estimated scope:** Medium (3 files)

---

### Task 15: DuckDuckGo web search service

**Description:** Search DuckDuckGo for character/series info. Parse HTML results. Cache results.
**Acceptance criteria:**

- [ ] `search_ddg(query, max_results=5) -> list[SearchResult]`
- [ ] Returns: title, url, snippet
- [ ] Cache results in SQLite (avoid repeat queries)
- [ ] Rate limiting: max 1 request/second
- [ ] Graceful failure: return empty list on error
- [ ] `POST /characters/{id}/research` — trigger search
- [ ] `GET /characters/{id}/research` — get cached results
  **Verification:**
- [ ] Search returns relevant results
- [ ] Cache works (second query is instant)
- [ ] No crash on network error
  **Dependencies:** Task 7
  **Files likely touched:**

- `backend/src/services/researcher.py`
- `backend/src/api/routes/characters.py` (extend)
  **Estimated scope:** Medium (2-3 files)

---

### Task 16: Research enrichment integration

**Description:** Combine glossary + web search + LLM knowledge → enriched character context for translator.
**Acceptance criteria:**

- [ ] `enrich_context(chapter_id) -> EnrichedContext`
- [ ] Merges: user glossary + web search results + LLM knowledge
- [ ] LLM synthesizes research into concise context notes
- [ ] Enriched context passed to translator prompt
- [ ] `POST /chapters/{id}/enrich` — trigger enrichment
  **Verification:**
- [ ] Enriched context improves translation quality (manual check)
- [ ] Web search results relevant to characters
  **Dependencies:** Task 14, Task 15
  **Files likely touched:**

- `backend/src/services/researcher.py` (extend)
- `backend/src/prompts/research.py`
- `backend/src/services/translator.py` (extend)
  **Estimated scope:** Medium (3 files)

---

### Task 17: Glossary editor UI

**Description:** Frontend for managing glossary entries. Add, edit, delete, import.
**Acceptance criteria:**

- [ ] Glossary table: term, translation, notes, source
- [ ] Add entry form
- [ ] Inline edit
- [ ] Delete with confirmation
- [ ] Import modal: paste JSON/CSV
- [ ] Search/filter entries
  **Verification:**
- [ ] CRUD operations sync with backend
- [ ] Import parses correctly
  **Dependencies:** Task 14, Task 13
  **Files likely touched:**

- `frontend/src/components/GlossaryEditor.tsx`
- `frontend/src/hooks/useGlossary.ts`
  **Estimated scope:** Medium (2 files)

---

### Task 18: Context carry across chapters

**Description:** Running glossary that accumulates character info across chapters. Translator uses prior chapter context.
**Acceptance criteria:**

- [ ] After analyzing chapter N, character data merged into project-level context
- [ ] Translating chapter N+1 includes context from chapters 1..N
- [ ] `GET /projects/{id}/context` — view accumulated context
- [ ] Context window managed (summarize if too long)
  **Verification:**
- [ ] Character names consistent across all chapters
- [ ] Later chapters reference earlier context correctly
  **Dependencies:** Task 16
  **Files likely touched:**

- `backend/src/services/translator.py` (extend)
- `backend/src/services/analyzer.py` (extend)
- `backend/src/api/routes/projects.py` (extend)
  **Estimated scope:** Medium (3 files)

---

## Checkpoint: Full Pipeline

- [ ] Glossary + research enhances translation
- [ ] Multi-chapter context preserved
- [ ] Character consistency across entire book

---

### Task 19: Export structured JSON output

**Description:** Export full project as structured JSON (metadata + summary + characters + chapters + translations + audio info).
**Acceptance criteria:**

- [ ] `GET /projects/{id}/export` — returns JSON
- [ ] JSON structure matches spec (metadata, summary, characters, chapters, audio)
- [ ] `POST /projects/{id}/export` — save to file
- [ ] Frontend download button
  **Verification:**
- [ ] JSON valid + parseable
- [ ] All data included
  **Dependencies:** Task 18
  **Files likely touched:**

- `backend/src/api/routes/projects.py` (extend)
- `frontend/src/components/` (export button)
  **Estimated scope:** Small (2 files)

---

### Task 20: Error handling + retry logic

**Description:** Robust error handling for OCR failures, LLM timeouts, TTS failures, network errors.
**Acceptance criteria:**

- [ ] OCR failure → fallback to other engine → user notification
- [ ] LLM timeout → retry (max 3) → user notification
- [ ] TTS failure → retry → user notification
- [ ] Web search failure → graceful degradation
- [ ] All errors logged with context
- [ ] User-facing error messages (Vietnamese)
  **Verification:**
- [ ] Simulate failures → handled gracefully
- [ ] No unhandled exceptions crash the app
  **Dependencies:** All prior
  **Files likely touched:**

- `backend/src/services/extractor.py` (extend)
- `backend/src/services/llm_client.py` (extend)
- `backend/src/services/translator.py` (extend)
- `backend/src/services/tts_service.py` (extend)
- `backend/src/main.py` (error handlers)
  **Estimated scope:** Medium (5 files)

---

### Task 21: Settings UI

**Description:** Frontend settings page: model selection, OCR engine toggle, TTS voice/style, Ollama URL config.
**Acceptance criteria:**

- [ ] Model dropdown (fetched from `/llm/models`)
- [ ] OCR engine toggle (RapidOCR / Tesseract / both)
- [ ] TTS voice dropdown (fetched from `/tts/voices`)
- [ ] TTS style selector (tu_nhien / tin_tuc / doc_truyen)
- [ ] Ollama URL field (with test button)
- [ ] Settings persisted (localStorage or backend)
  **Verification:**
- [ ] Settings saved + applied
- [ ] Model switch works
- [ ] Voice/style switch works
  **Dependencies:** Task 13
  **Files likely touched:**

- `frontend/src/components/Settings.tsx`
- `backend/src/api/routes/settings.py`
  **Estimated scope:** Small (2 files)

---

### Task 22: README + setup instructions

**Description:** Comprehensive setup guide. Prerequisites, install, run, usage.
**Acceptance criteria:**

- [ ] Prerequisites: Python 3.12+, Node 20+, Ollama, Tesseract (optional), ffmpeg (for MP3)
- [ ] Backend setup: `uv sync`, `uv run uvicorn...`
- [ ] Frontend setup: `npm install`, `npm run dev`
- [ ] Ollama setup: install + pull model (Qwen2.5 7B)
- [ ] VieNeu-TTS: `vieneu` SDK auto-install via `uv sync`
- [ ] ffmpeg setup: install instructions
- [ ] Usage guide: upload → analyze → translate → TTS → playback
- [ ] Troubleshooting section
  **Verification:**
- [ ] Fresh clone → follow README → app runs
  **Dependencies:** All prior
  **Files likely touched:**

- `README.md`
  **Estimated scope:** Small (1 file)

---

## Checkpoint: Polish

- [ ] Error handling robust
- [ ] Settings configurable (LLM + TTS)
- [ ] Setup documented

---

## Phase 6: TTS Integration — Audio Generation & Playback

### Task 23: VieNeu-TTS service wrapper

**Description:** Install `vieneu` SDK, create TTS service. Init `Vieneu()`, list voices, `infer()`, `infer_stream()`.
**Acceptance criteria:**

- [ ] `vieneu` in `pyproject.toml` dependencies
- [ ] `TTSClient` class: `init()`, `list_voices()`, `infer(text, voice, style)`, `infer_stream(text, voice, style)`
- [ ] Default: `style="doc_truyen"`, `precision="int8"` (CPU fastest)
- [ ] `GET /tts/health` — check TTS model loaded
- [ ] `GET /tts/voices` — list 14 preset voices (Bắc/Trung/Nam)
- [ ] Config: voice + style from env or settings
  **Verification:**
- [ ] `Vieneu()` initializes without error
- [ ] `infer("Xin chào", voice="Phạm Tuyên", style="doc_truyen")` returns audio
- [ ] `infer_stream()` yields chunks
  **Dependencies:** Task 1
  **Files likely touched:**

- `backend/src/services/tts_client.py`
- `backend/src/api/routes/tts.py`
  **Estimated scope:** Small (2 files)

---

### Task 24: Emotion cue injection in translation

**Description:** Update translation prompt to auto-inject `[cười]`, `[thở dài]`, `[hắng giọng]` cues. User can edit translated text before TTS.
**Acceptance criteria:**

- [ ] Translation prompt updated: instruct LLM to insert emotion cues where contextually appropriate
- [ ] Cues match VieNeu-TTS format: `[cười]`, `[thở dài]`, `[hắng giọng]`
- [ ] Cues inserted inline, not at segment boundaries
- [ ] Frontend: edit translated text before triggering TTS (textarea with cue preview)
- [ ] Cues stripped from display text, kept for TTS input
  **Verification:**
- [ ] Translated text contains appropriate cues
- [ ] User can add/remove cues manually
- [ ] TTS processes cues correctly (hear emotion)
  **Dependencies:** Task 8
  **Files likely touched:**

- `backend/src/prompts/translate.py` (extend)
- `frontend/src/components/TranslationView.tsx` (extend)
  **Estimated scope:** Small (2 files)

---

### Task 25: TTS generation service (per chapter)

**Description:** Generate audio per chapter. Split text → segments → generate per segment → track timestamps → save WAV + MP3.
**Acceptance criteria:**

- [ ] `generate_chapter_audio(chapter_id, voice, style) -> AudioResult`
- [ ] Split translated text into segments (by sentence — `.`, `!`, `?`, `。`, `！`, `？`)
- [ ] Generate audio per segment via `tts.infer_stream()`
- [ ] Concatenate segments → full chapter audio
- [ ] Track timeline: `{segment_index, text, start_time, end_time}` per segment
- [ ] Save WAV (lossless) + encode MP3 via ffmpeg subprocess
- [ ] Store `AudioFile` + `AudioTimeline` records in DB
- [ ] `POST /chapters/{id}/tts` — trigger generation (background job)
- [ ] `GET /chapters/{id}/audio` — get audio metadata + timeline
- [ ] `GET /chapters/{id}/audio/stream` — stream MP3
- [ ] Progress: SSE events during generation (segment X/Y)
  **Verification:**
- [ ] Audio generated per chapter, playable
- [ ] Timeline accurate (segment boundaries match audio)
- [ ] Both WAV + MP3 files created
- [ ] Background job status tracked
  **Dependencies:** Task 23, Task 24
  **Files likely touched:**

- `backend/src/services/tts_service.py`
- `backend/src/models/db.py` (extend)
- `backend/src/api/routes/tts.py` (extend)
- `backend/tests/test_tts_service.py`
  **Estimated scope:** Medium (4 files)

---

### Task 26: Audio storage + serving

**Description:** Store audio files on disk, serve via FastAPI. Audio directory structure + cleanup.
**Acceptance criteria:**

- [ ] Directory: `backend/audio/{project_id}/{chapter_id}/`
- [ ] Files: `audio.wav`, `audio.mp3`, `timeline.json`
- [ ] `GET /chapters/{id}/audio/stream` — HTTP range request streaming (seekable)
- [ ] `GET /chapters/{id}/audio/download` — download MP3 or WAV
- [ ] `DELETE /projects/{id}` cascade: delete audio files too
- [ ] Config: audio storage path (default `./audio/`)
  **Verification:**
- [ ] Audio streams with seek support
- [ ] Download works
- [ ] Project deletion cleans audio files
  **Dependencies:** Task 25
  **Files likely touched:**

- `backend/src/services/audio_store.py`
- `backend/src/api/routes/tts.py` (extend)
  **Estimated scope:** Small (2 files)

---

### Task 27: Audio player UI + auto-next

**Description:** Frontend audio player with play/pause/seek/speed/skip + auto-next chapter.
**Acceptance criteria:**

- [ ] Audio player component: play, pause, seek bar, speed (0.5x–2x), skip ±15s
- [ ] Voice selector dropdown (14 preset voices)
- [ ] Style selector: `tu_nhien`, `tin_tuc`, `doc_truyen` (default)
- [ ] "Generate TTS" button per chapter → progress indicator
- [ ] Auto-next: when audio ends, auto-play next chapter (toggleable)
- [ ] Chapter list shows audio status (generated/pending)
- [ ] Volume control
  **Verification:**
- [ ] Audio plays in browser
- [ ] Seek works (drag + click)
- [ ] Speed control works
- [ ] Auto-next transitions smoothly
  **Dependencies:** Task 25, Task 13
  **Files likely touched:**

- `frontend/src/components/AudioPlayer.tsx`
- `frontend/src/components/VoiceSelector.tsx`
- `frontend/src/hooks/useAudio.ts`
  **Estimated scope:** Medium (2-3 files)

---

### Task 28: Text sync (karaoke)

**Description:** Highlight current text segment synced with audio playback. Click text → seek audio.
**Acceptance criteria:**

- [ ] Timeline data fetched from `/chapters/{id}/audio`
- [ ] `timeupdate` event → find current segment → highlight
- [ ] Auto-scroll to current segment (smooth)
- [ ] Click text segment → seek audio to `start_time`
- [ ] Highlight style: background color + smooth transition
- [ ] Works with speed change (timeline adjusts)
- [ ] Toggle: karaoke mode on/off
  **Verification:**
- [ ] Highlight follows audio accurately (<100ms drift)
- [ ] Click seeks to correct position
- [ ] Auto-scroll keeps current segment visible
- [ ] Toggle works
  **Dependencies:** Task 27
  **Files likely touched:**

- `frontend/src/components/TextSync.tsx`
- `frontend/src/hooks/useTimeline.ts`
  **Estimated scope:** Medium (2 files)

---

## Checkpoint: TTS Integration

- [ ] Generate TTS from translated chapter → playable audio
- [ ] Karaoke text sync works
- [ ] Auto-next chapter works
- [ ] Both WAV + MP3 available
- [ ] Emotion cues audible in audio

---

## Checkpoint: Complete

- [ ] All acceptance criteria met
- [ ] Ready for use

