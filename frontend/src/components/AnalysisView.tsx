import { useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { useAnalysis, useAnalyzeChapter, useRelationships, useMapRelationships } from "../hooks/useAnalysis"
import { useToast } from "../contexts/ToastContext"
import CharacterGraph from "./CharacterGraph"

export default function AnalysisView() {
  const { chapterId: chIdStr, id: projectIdStr } = useParams()
  const chId = Number(chIdStr)
  const projectId = Number(projectIdStr)
  const navigate = useNavigate()

  const { data: analysis, isLoading } = useAnalysis(chId)
  const analyze = useAnalyzeChapter()
  const { data: relData } = useRelationships(projectId)
  const mapRels = useMapRelationships()
  const { addToast } = useToast()

  const [selectedChar, setSelectedChar] = useState<string | null>(null)

  const handleAnalyze = () =>
    analyze.mutate(chId, {
      onSuccess: (result) =>
        addToast(`Analysis complete: ${result.characters} characters, ${result.key_terms} key terms`, "success"),
      onError: (err) => addToast(`Analysis failed: ${err.message}`, "error"),
    })
  const handleMapRels = () =>
    mapRels.mutate(chId, {
      onSuccess: (result) => addToast(`Mapped ${result.relationships_created} new relationships (${result.total} total)`, "success"),
      onError: (err) => addToast(`Relationship mapping failed: ${err.message}`, "error"),
    })

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-3 mb-4">
        <button
          onClick={() => navigate(`/projects/${projectId}/chapters/${chId}`)}
          className="text-slate-500 hover:text-slate-700"
        >
          ← Back
        </button>
        <h2 className="text-xl font-bold text-slate-800 flex-1">Analysis</h2>
        <button
          onClick={handleAnalyze}
          disabled={analyze.isPending}
          className="px-3 py-1.5 text-sm bg-amber-700 text-white rounded hover:bg-amber-600 disabled:opacity-50"
        >
          {analyze.isPending ? "Analyzing..." : "Analyze Chapter"}
        </button>
        <button
          onClick={handleMapRels}
          disabled={mapRels.isPending}
          className="px-3 py-1.5 text-sm bg-slate-800 text-white rounded hover:bg-slate-700 disabled:opacity-50"
        >
          {mapRels.isPending ? "Mapping..." : "Map Relationships"}
        </button>
      </div>

      {analyze.isError && (
        <div className="mb-3 p-3 bg-red-50 text-red-700 rounded text-sm">
          Analysis failed: {analyze.error?.message}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 flex-1 overflow-auto">
        <div className="lg:col-span-1 space-y-4">
          <div className="p-4 bg-white rounded-lg shadow-sm">
            <h3 className="font-semibold text-slate-700 mb-2">Summary</h3>
            {isLoading ? (
              <p className="text-slate-400 text-sm">Loading...</p>
            ) : analysis?.summary ? (
              <p className="text-sm text-slate-600">{analysis.summary}</p>
            ) : (
              <p className="text-slate-400 text-sm">No analysis yet.</p>
            )}
          </div>

          <div className="p-4 bg-white rounded-lg shadow-sm">
            <h3 className="font-semibold text-slate-700 mb-2">Characters</h3>
            {!analysis?.characters || analysis.characters.length === 0 ? (
              <p className="text-slate-400 text-sm">None found.</p>
            ) : (
              <div className="space-y-2">
                {analysis.characters.map((c) => (
                  <div
                    key={c.id}
                    onClick={() => setSelectedChar(selectedChar === c.name ? null : c.name)}
                    className={`p-2 rounded cursor-pointer transition-colors ${
                      selectedChar === c.name ? "bg-amber-50 ring-1 ring-amber-300" : "hover:bg-slate-50"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-slate-800 text-sm">{c.name}</span>
                      {c.role && (
                        <span className="text-xs px-1.5 py-0.5 bg-slate-100 rounded text-slate-600">
                          {c.role}
                        </span>
                      )}
                    </div>
                    {selectedChar === c.name && (
                      <div className="mt-2 text-xs text-slate-500 space-y-1">
                        {c.aliases && <p>Aliases: {c.aliases}</p>}
                        {c.honorifics && <p>Honorifics: {c.honorifics}</p>}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="lg:col-span-2">
          <h3 className="font-semibold text-slate-700 mb-2">Relationship Graph</h3>
          {relData ? <CharacterGraph data={relData} /> : (
            <div className="flex items-center justify-center h-64 text-slate-400">
              No relationship data. Map relationships first.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
