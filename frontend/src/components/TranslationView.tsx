import { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { useChapter } from "../hooks/useChapters"
import { useTranslation, useUpdateTranslation, useStreamTranslation } from "../hooks/useTranslation"

const CUE_REGEX = /\[(cười|thở dài|hắng giọng|giật mình|càu nhàu|thì thầm|hét lên|nói nhỏ)\]/g

const CUE_STYLES: Record<string, string> = {
  "cười": "bg-amber-100 text-amber-700",
  "thở dài": "bg-blue-100 text-blue-700",
  "hắng giọng": "bg-purple-100 text-purple-700",
  "giật mình": "bg-red-100 text-red-700",
  "càu nhàu": "bg-orange-100 text-orange-700",
  "thì thầm": "bg-green-100 text-green-700",
  "hét lên": "bg-red-100 text-red-700",
  "nói nhỏ": "bg-green-100 text-green-700",
}

type ViewMode = "original" | "translated" | "sidebyside"

export default function TranslationView() {
  const { chapterId: chIdStr, id: projectIdStr } = useParams()
  const chId = Number(chIdStr)
  const projectId = Number(projectIdStr)
  const navigate = useNavigate()

  const { data: chapter } = useChapter(chId)
  const { data: translationData } = useTranslation(chId)
  const updateTranslation = useUpdateTranslation()
  const { streaming, streamedText, start, stop } = useStreamTranslation()

  const [mode, setMode] = useState<ViewMode>("sidebyside")
  const [editing, setEditing] = useState(false)
  const [editText, setEditText] = useState("")

  const displayText = streaming ? streamedText : (translationData?.translated_text ?? "")

  useEffect(() => {
    if (translationData?.translated_text && !editText) {
      setEditText(translationData.translated_text)
    }
  }, [translationData])

  const handleSave = () => {
    updateTranslation.mutate(
      { id: chId, text: editText },
      { onSuccess: () => setEditing(false) },
    )
  }

  const renderWithCues = (text: string) => {
    if (!text) return <span className="text-slate-400">(empty)</span>
    const parts = text.split(CUE_REGEX)
    return parts.map((part, i) => {
      if (i > 0) {
        const cue = Object.keys(CUE_STYLES)[i - 1]
        const matched = CUE_STYLES[cue]
        if (matched) {
          return (
            <span key={i} className={`px-1 rounded text-xs ${matched}`}>
              [{part}]
            </span>
          )
        }
      }
      return <span key={i}>{part}</span>
    })
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-3 mb-4 flex-wrap">
        <button
          onClick={() => navigate(`/projects/${projectId}/chapters/${chId}`)}
          className="text-slate-500 hover:text-slate-700"
        >
          ← Back
        </button>
        <h2 className="text-xl font-bold text-slate-800 flex-1">Translation</h2>

        <div className="flex bg-slate-200 rounded p-0.5">
          {(["original", "translated", "sidebyside"] as ViewMode[]).map((m) => (
            <button
              key={m}
              onClick={() => setMode(m)}
              className={`px-3 py-1 text-xs rounded transition-colors ${
                mode === m ? "bg-white text-slate-800 shadow-sm" : "text-slate-600"
              }`}
            >
              {m === "sidebyside" ? "Side-by-side" : m.charAt(0).toUpperCase() + m.slice(1)}
            </button>
          ))}
        </div>

        {!streaming ? (
          <button
            onClick={() => {
              if (displayText && !confirm("Re-translate? Existing translation will be overwritten.")) return
              start(chId)
            }}
            className="px-3 py-1.5 text-sm bg-purple-700 text-white rounded hover:bg-purple-600"
          >
            Translate
          </button>
        ) : (
          <button
            onClick={stop}
            className="px-3 py-1.5 text-sm bg-red-600 text-white rounded hover:bg-red-500"
          >
            Stop
          </button>
        )}

        {displayText && !streaming && (
          !editing ? (
            <button
              onClick={() => { setEditText(displayText); setEditing(true) }}
              className="px-3 py-1.5 text-sm bg-slate-800 text-white rounded hover:bg-slate-700"
            >
              Edit
            </button>
          ) : (
            <>
              <button
                onClick={handleSave}
                disabled={updateTranslation.isPending}
                className="px-3 py-1.5 text-sm bg-green-700 text-white rounded hover:bg-green-600 disabled:opacity-50"
              >
                {updateTranslation.isPending ? "Saving..." : "Save"}
              </button>
              <button
                onClick={() => setEditing(false)}
                className="px-3 py-1.5 text-sm bg-slate-200 text-slate-700 rounded hover:bg-slate-300"
              >
                Cancel
              </button>
            </>
          )
        )}
      </div>

      {streaming && (
        <div className="mb-3 text-sm text-purple-600 animate-pulse">
          Streaming translation... ({streamedText.length} chars)
        </div>
      )}

      {editing ? (
        <div className="flex-1 flex flex-col">
          <p className="text-xs text-slate-500 mb-2">
            Edit translation. Emotion cues in brackets: [cười], [thở dài], [hắng giọng], etc.
          </p>
          <textarea
            value={editText}
            onChange={(e) => setEditText(e.target.value)}
            className="flex-1 w-full p-4 border border-slate-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-slate-500 text-sm"
          />
        </div>
      ) : (
        <div className="flex-1 overflow-auto grid gap-4" style={{
          gridTemplateColumns: mode === "sidebyside" ? "1fr 1fr" : "1fr",
        }}>
          {(mode === "original" || mode === "sidebyside") && (
            <div className="bg-white rounded-lg shadow-sm p-4 overflow-auto">
              <h3 className="text-sm font-semibold text-slate-500 mb-2">Original</h3>
              <pre className="whitespace-pre-wrap text-sm text-slate-700 font-sans">
                {chapter?.original_text || "(empty)"}
              </pre>
            </div>
          )}
          {(mode === "translated" || mode === "sidebyside") && (
            <div className="bg-white rounded-lg shadow-sm p-4 overflow-auto">
              <h3 className="text-sm font-semibold text-slate-500 mb-2">Translated</h3>
              <div className="text-sm text-slate-700 leading-relaxed">
                {renderWithCues(displayText)}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
