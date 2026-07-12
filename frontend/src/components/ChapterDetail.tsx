import { useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { useChapter, useUpdateChapter } from "../hooks/useChapters"
import type { ChapterUpdate } from "../types"

export default function ChapterDetail() {
  const { chapterId: chIdStr, id: projectIdStr } = useParams()
  const chId = Number(chIdStr)
  const projectId = Number(projectIdStr)
  const { data: chapter, isLoading } = useChapter(chId)
  const update = useUpdateChapter()
  const navigate = useNavigate()

  const [editing, setEditing] = useState(false)
  const [title, setTitle] = useState("")
  const [text, setText] = useState("")

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
      { onSuccess: () => setEditing(false) },
    )
  }

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
