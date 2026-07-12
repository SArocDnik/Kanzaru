import { useState, useEffect, useRef } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { useChapter, useUpdateChapter } from "../hooks/useChapters"
import { useExtractStream } from "../hooks/useExtractStream"
import { useToast } from "../contexts/ToastContext"
import type { ChapterUpdate } from "../types"

export default function ChapterDetail() {
  const { chapterId: chIdStr, id: projectIdStr } = useParams()
  const chId = Number(chIdStr)
  const projectId = Number(projectIdStr)
  const { data: chapter, isLoading } = useChapter(chId)
  const update = useUpdateChapter()
  const navigate = useNavigate()
  const { addToast } = useToast()
  const { streaming, progress, done, error, start, stop } = useExtractStream()
  const startedRef = useRef(false)

  const [editing, setEditing] = useState(false)
  const [title, setTitle] = useState("")
  const [text, setText] = useState("")

  useEffect(() => {
    if (chapter?.status === "processing" && !startedRef.current && !streaming && !done) {
      startedRef.current = true
      start(chId)
    }
  }, [chapter?.status, chId, start, streaming, done])

  useEffect(() => {
    if (done) {
      addToast("Extraction complete", "success")
    }
  }, [done, addToast])

  useEffect(() => {
    if (error) {
      addToast(`Extraction error: ${error}`, "error")
    }
  }, [error, addToast])

  if (isLoading) return <p className="text-slate-500">Loading...</p>
  if (!chapter) return <p className="text-slate-500">Chapter not found.</p>

  const startEdit = () => {
    setTitle(chapter.title)
    setText(chapter.original_text)
    setEditing(true)
  }

  const save = () => {
    const data: ChapterUpdate = { title, original_text: text }
    update.mutate(
      { id: chId, data },
      {
        onSuccess: () => {
          setEditing(false)
          addToast("Chapter saved", "success")
        },
        onError: (err) => addToast(`Save failed: ${err.message}`, "error"),
      },
    )
  }

  const nextStep = () => {
    switch (chapter.status) {
      case "uploaded":
      case "detected":
        return { text: "Analyze this chapter to extract characters and summary", to: "analyze" }
      case "analyzed":
        return { text: "Translate this chapter to the target language", to: "translate" }
      case "translated":
        return null
      default:
        return null
    }
  }

  const step = nextStep()

  const pct = progress && progress.total > 0
    ? Math.round((progress.page / progress.total) * 100)
    : 0

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-3 mb-4">
        <button
          onClick={() => navigate(`/projects/${projectId}`)}
          className="text-slate-500 hover:text-slate-700"
        >
          ← Chapters
        </button>
        {!editing ? (
          <h2 className="text-xl font-bold text-slate-800 flex-1">
            {chapter.chapter_number}. {chapter.title || "(untitled)"}
          </h2>
        ) : (
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="flex-1 px-3 py-1 border border-slate-300 rounded text-lg font-bold"
          />
        )}
        <span className="text-xs px-2 py-0.5 rounded bg-slate-100 text-slate-600">
          {chapter.status}
        </span>
        {!editing ? (
          <button
            onClick={startEdit}
            className="px-3 py-1.5 text-sm bg-slate-800 text-white rounded hover:bg-slate-700"
          >
            Edit
          </button>
        ) : (
          <>
            <button
              onClick={save}
              disabled={update.isPending}
              className="px-3 py-1.5 text-sm bg-green-700 text-white rounded hover:bg-green-600 disabled:opacity-50"
            >
              {update.isPending ? "Saving..." : "Save"}
            </button>
            <button
              onClick={() => setEditing(false)}
              className="px-3 py-1.5 text-sm bg-slate-200 text-slate-700 rounded hover:bg-slate-300"
            >
              Cancel
            </button>
          </>
        )}
        {chapter.status === "analyzed" || chapter.status === "translated" ? (
          <>
            <button
              onClick={() => navigate(`/projects/${projectId}/chapters/${chId}/analyze`)}
              className="px-3 py-1.5 text-sm bg-amber-700 text-white rounded hover:bg-amber-600"
            >
              Analysis →
            </button>
            <button
              onClick={() => navigate(`/projects/${projectId}/chapters/${chId}/translate`)}
              className="px-3 py-1.5 text-sm bg-purple-700 text-white rounded hover:bg-purple-600"
            >
              Translate →
            </button>
          </>
        ) : (
          <button
            onClick={() => navigate(`/projects/${projectId}/chapters/${chId}/analyze`)}
            className="px-3 py-1.5 text-sm bg-amber-700 text-white rounded hover:bg-amber-600"
          >
            Analyze →
          </button>
        )}
      </div>

      {(streaming || progress || done || error) && (
        <div className="mb-4 px-4 py-3 bg-slate-50 border border-slate-200 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-slate-700">
              {error ? "Extraction failed" : done ? "Extraction complete" : streaming ? "Extracting..." : "Ready"}
            </span>
            {progress && (
              <span className="text-xs text-slate-500">
                Page {progress.page}/{progress.total} — {progress.method} ({progress.chars} chars)
              </span>
            )}
          </div>
          {progress && (
            <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
              <div
                className="bg-blue-600 h-full transition-all duration-300"
                style={{ width: `${pct}%` }}
              />
            </div>
          )}
          {error && (
            <p className="text-sm text-red-600 mt-1">{error}</p>
          )}
          {streaming && (
            <button
              onClick={stop}
              className="mt-2 px-3 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-500"
            >
              Stop
            </button>
          )}
        </div>
      )}

      {step && (
        <div className="mb-4 px-4 py-2 bg-blue-50 border border-blue-200 rounded text-sm text-blue-700 flex items-center gap-2">
          <span className="text-lg">→</span>
          <span>Next: {step.text}</span>
          <button
            onClick={() => navigate(`/projects/${projectId}/chapters/${chId}/${step.to}`)}
            className="ml-auto px-3 py-1 bg-blue-700 text-white rounded hover:bg-blue-600 text-xs"
          >
            Go to {step.to === "analyze" ? "Analysis" : "Translation"}
          </button>
        </div>
      )}

      {editing ? (
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          className="flex-1 w-full p-4 border border-slate-300 rounded-lg font-mono text-sm resize-none focus:outline-none focus:ring-2 focus:ring-slate-500"
        />
      ) : (
        <div className="flex-1 overflow-auto bg-white rounded-lg shadow-sm p-6">
          <pre className="whitespace-pre-wrap text-sm text-slate-700 font-sans">
            {chapter.original_text || "(empty)"}
          </pre>
        </div>
      )}
    </div>
  )
}
