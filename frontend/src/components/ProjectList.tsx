import { useState } from "react"
import { useProjects, useCreateProject, useDeleteProject } from "../hooks/useProject"
import type { ProjectCreate } from "../types"
import { useNavigate } from "react-router-dom"

export default function ProjectList() {
  const { data: projects, isLoading } = useProjects()
  const createProject = useCreateProject()
  const deleteProject = useDeleteProject()
  const navigate = useNavigate()

  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState<ProjectCreate>({
    name: "",
    source_lang: "auto",
    target_lang: "vi",
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.name.trim()) return
    createProject.mutate(form, {
      onSuccess: () => {
        setShowForm(false)
        setForm({ name: "", source_lang: "auto", target_lang: "vi" })
      },
    })
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-slate-800">Projects</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-4 py-2 bg-slate-800 text-white rounded hover:bg-slate-700 transition-colors"
        >
          {showForm ? "Cancel" : "New Project"}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-4 bg-white rounded-lg shadow space-y-3">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Name</label>
            <input
              type="text"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="w-full px-3 py-2 border border-slate-300 rounded focus:outline-none focus:ring-2 focus:ring-slate-500"
              placeholder="Novel title"
              autoFocus
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Source Language</label>
              <select
                value={form.source_lang}
                onChange={(e) => setForm({ ...form, source_lang: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded focus:outline-none focus:ring-2 focus:ring-slate-500"
              >
                <option value="auto">Auto-detect</option>
                <option value="ja">Japanese</option>
                <option value="en">English</option>
                <option value="vi">Vietnamese</option>
                <option value="zh">Chinese</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Target Language</label>
              <select
                value={form.target_lang}
                onChange={(e) => setForm({ ...form, target_lang: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded focus:outline-none focus:ring-2 focus:ring-slate-500"
              >
                <option value="vi">Vietnamese</option>
                <option value="en">English</option>
              </select>
            </div>
          </div>
          <button
            type="submit"
            disabled={createProject.isPending || !form.name.trim()}
            className="px-4 py-2 bg-slate-800 text-white rounded hover:bg-slate-700 disabled:opacity-50 transition-colors"
          >
            {createProject.isPending ? "Creating..." : "Create"}
          </button>
        </form>
      )}

      {isLoading ? (
        <p className="text-slate-500">Loading...</p>
      ) : !projects || projects.length === 0 ? (
        <p className="text-slate-500">No projects yet. Create one to get started.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map((p) => (
            <div
              key={p.id}
              className="p-4 bg-white rounded-lg shadow hover:shadow-md transition-shadow cursor-pointer group"
              onClick={() => navigate(`/projects/${p.id}`)}
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-slate-800 group-hover:text-slate-900">{p.name}</h3>
                  <p className="text-sm text-slate-500 mt-1">
                    {p.source_lang} → {p.target_lang}
                  </p>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    if (confirm(`Delete "${p.name}"? This removes all chapters and data.`))
                      deleteProject.mutate(p.id)
                  }}
                  className="text-slate-400 hover:text-red-500 transition-colors text-sm"
                  title="Delete"
                >
                  ✕
                </button>
              </div>
              <p className="text-xs text-slate-400 mt-2">
                {new Date(p.created_at).toLocaleDateString()}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
