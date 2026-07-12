import { useChapters, useDetectChapters, useDeleteChapter } from "../hooks/useChapters"
import { useNavigate, useParams } from "react-router-dom"
import { useToast } from "../contexts/ToastContext"

const STATUS_STYLES: Record<string, string> = {
  pending: "bg-slate-200 text-slate-700",
  uploaded: "bg-blue-100 text-blue-700",
  detected: "bg-cyan-100 text-cyan-700",
  analyzed: "bg-amber-100 text-amber-700",
  translating: "bg-purple-100 text-purple-700",
  translated: "bg-green-100 text-green-700",
}

export default function ChapterList() {
  const { id: projectIdStr } = useParams()
  const projectId = Number(projectIdStr)
  const { data: chapters, isLoading } = useChapters(projectId)
  const detect = useDetectChapters()
  const deleteChapter = useDeleteChapter()
  const navigate = useNavigate()
  const { addToast } = useToast()

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate("/")}
            className="text-slate-500 hover:text-slate-700"
          >
            ← Back
          </button>
          <h2 className="text-xl font-bold text-slate-800">Chapters</h2>
          {chapters && chapters.length > 0 && (
            <span className="text-sm text-slate-400">({chapters.length})</span>
          )}
        </div>
        <button
          onClick={() =>
            detect.mutate(projectId, {
              onSuccess: (chs) =>
                addToast(`Detected ${chs.length} chapter${chs.length !== 1 ? "s" : ""}`, "success"),
              onError: (err) => addToast(`Detection failed: ${err.message}`, "error"),
            })
          }
          disabled={detect.isPending}
          className="px-3 py-1.5 text-sm bg-slate-800 text-white rounded hover:bg-slate-700 disabled:opacity-50"
        >
          {detect.isPending ? "Detecting..." : "Detect Chapters"}
        </button>
      </div>

      {isLoading ? (
        <p className="text-slate-500">Loading...</p>
      ) : !chapters || chapters.length === 0 ? (
        <p className="text-slate-500">No chapters yet. Upload text and detect chapters.</p>
      ) : (
        <div className="space-y-2 overflow-auto">
          {chapters.map((ch) => (
            <div
              key={ch.id}
              className="flex items-center gap-3 p-3 bg-white rounded-lg shadow-sm hover:shadow cursor-pointer"
              onClick={() => navigate(`/projects/${projectId}/chapters/${ch.id}`)}
            >
              <span className="text-sm font-mono text-slate-400 w-8 text-right">
                {ch.chapter_number}
              </span>
              <span className="flex-1 font-medium text-slate-800 truncate">
                {ch.title || "(untitled)"}
              </span>
              <span className="text-xs text-slate-400">
                {ch.original_text.length} chars
              </span>
              <span
                className={`text-xs px-2 py-0.5 rounded ${STATUS_STYLES[ch.status] ?? "bg-slate-100 text-slate-600"}`}
              >
                {ch.status}
              </span>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  if (confirm(`Delete "${ch.title}"?`))
                    deleteChapter.mutate(ch.id, {
                      onSuccess: () => addToast(`Deleted chapter "${ch.title}"`, "info"),
                      onError: (err) => addToast(`Delete failed: ${err.message}`, "error"),
                    })
                }}
                className="text-slate-300 hover:text-red-500 text-sm"
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
