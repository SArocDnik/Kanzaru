import { useState, useRef } from "react"
import { useProjects } from "../hooks/useProject"
import { useUpload } from "../hooks/useUpload"
import { useNavigate } from "react-router-dom"
import { useToast } from "../contexts/ToastContext"
import type { UploadResult } from "../types"

export default function UploadPanel() {
  const { data: projects } = useProjects()
  const upload = useUpload()
  const navigate = useNavigate()
  const { addToast } = useToast()
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [projectId, setProjectId] = useState<number | null>(null)
  const [text, setText] = useState("")
  const [dragOver, setDragOver] = useState(false)
  const [lastResult, setLastResult] = useState<UploadResult | null>(null)

  const navigateAfter = (pid: number, chId: number) => {
    setTimeout(() => navigate(`/projects/${pid}/chapters/${chId}`), 1000)
  }

  const handleFile = (file: File) => {
    if (!projectId) return
    setLastResult(null)
    upload.mutate(
      { projectId, file },
      {
        onSuccess: (result) => {
          setLastResult(result)
          addToast(`File uploaded. Starting extraction...`, "success")
          navigateAfter(projectId, result.chapter_id)
        },
        onError: (err) => addToast(`Upload failed: ${err.message}`, "error"),
      },
    )
  }

  const handleText = () => {
    if (!projectId || !text.trim()) return
    setLastResult(null)
    upload.mutate(
      { projectId, text },
      {
        onSuccess: (result) => {
          setLastResult(result)
          addToast(`Text uploaded: ${result.chars} chars`, "success")
          setTimeout(() => navigate(`/projects/${projectId}`), 1000)
        },
        onError: (err) => addToast(`Upload failed: ${err.message}`, "error"),
      },
    )
  }

  return (
    <div>
      <h2 className="text-2xl font-bold text-slate-800 mb-6">Upload</h2>

      <div className="mb-4">
        <label className="block text-sm font-medium text-slate-700 mb-1">Select Project</label>
        <select
          value={projectId ?? ""}
          onChange={(e) => setProjectId(Number(e.target.value) || null)}
          className="w-full max-w-md px-3 py-2 border border-slate-300 rounded focus:outline-none focus:ring-2 focus:ring-slate-500"
        >
          <option value="">— Choose a project —</option>
          {projects?.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name} ({p.source_lang} → {p.target_lang})
            </option>
          ))}
        </select>
        {!projects || projects.length === 0 ? (
          <p className="text-sm text-amber-600 mt-1">Create a project first.</p>
        ) : null}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <h3 className="font-medium text-slate-700 mb-2">PDF Upload</h3>
          <div
            onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
            onDrop={(e) => {
              e.preventDefault()
              setDragOver(false)
              const file = e.dataTransfer.files[0]
              if (file) handleFile(file)
            }}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              dragOver ? "border-slate-500 bg-slate-100" : "border-slate-300 hover:border-slate-400"
            }`}
          >
            <p className="text-slate-500">
              {dragOver ? "Drop file here" : "Drag & drop PDF or click to browse"}
            </p>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.txt"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0]
                if (file) handleFile(file)
              }}
            />
          </div>
        </div>

        <div>
          <h3 className="font-medium text-slate-700 mb-2">Paste Text</h3>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={8}
            placeholder="Paste raw text here..."
            className="w-full px-3 py-2 border border-slate-300 rounded focus:outline-none focus:ring-2 focus:ring-slate-500 resize-none"
          />
          <button
            onClick={handleText}
            disabled={!projectId || !text.trim() || upload.isPending}
            className="mt-2 px-4 py-2 bg-slate-800 text-white rounded hover:bg-slate-700 disabled:opacity-50 transition-colors"
          >
            Upload Text
          </button>
        </div>
      </div>

      {upload.isPending && (
        <div className="mt-4 text-slate-600 animate-pulse">Uploading...</div>
      )}
      {lastResult && (
        <div className="mt-4 text-green-700 bg-green-50 px-4 py-2 rounded border border-green-200">
          ✓ File saved. {lastResult.status === "processing" ? "Redirecting to extraction progress..." : `Uploaded — ${lastResult.chars} chars.`}
        </div>
      )}
      {upload.isError && (
        <div className="mt-4 text-red-600 bg-red-50 px-4 py-2 rounded border border-red-200">
          Error: {upload.error?.message}
        </div>
      )}
    </div>
  )
}
