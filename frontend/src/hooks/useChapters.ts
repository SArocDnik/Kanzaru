import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { api } from "../api/client"
import type { Chapter, ChapterUpdate } from "../types"

export function useChapters(projectId: number | undefined) {
  return useQuery({
    queryKey: ["chapters", projectId],
    queryFn: () => api.get<Chapter[]>(`/projects/${projectId}/chapters`),
    enabled: !!projectId,
  })
}

export function useChapter(chapterId: number | undefined) {
  return useQuery({
    queryKey: ["chapter", chapterId],
    queryFn: () => api.get<Chapter>(`/chapters/${chapterId}`),
    enabled: !!chapterId,
  })
}

export function useUpdateChapter() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: ChapterUpdate }) =>
      api.put<Chapter>(`/chapters/${id}`, data),
    onSuccess: (chapter) => {
      qc.invalidateQueries({ queryKey: ["chapters", chapter.project_id] })
      qc.invalidateQueries({ queryKey: ["chapter", chapter.id] })
    },
  })
}

export function useDetectChapters() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (projectId: number) =>
      api.post<Chapter[]>(`/projects/${projectId}/chapters/detect`),
    onSuccess: (chapters) => {
      if (chapters[0]) qc.invalidateQueries({ queryKey: ["chapters", chapters[0].project_id] })
    },
  })
}

export function useDeleteChapter() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => api.delete(`/chapters/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["chapters"] }),
  })
}
