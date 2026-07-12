import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { api } from "../api/client"
import type { AnalysisData, AnalysisResult, RelationshipData } from "../types"

export function useAnalysis(chapterId: number | undefined) {
  return useQuery({
    queryKey: ["analysis", chapterId],
    queryFn: () => api.get<AnalysisData>(`/chapters/${chapterId}/analysis`),
    enabled: !!chapterId,
  })
}

export function useAnalyzeChapter() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (chapterId: number) =>
      api.post<AnalysisResult>(`/chapters/${chapterId}/analyze`),
    onSuccess: (_, chapterId) => {
      qc.invalidateQueries({ queryKey: ["analysis", chapterId] })
      qc.invalidateQueries({ queryKey: ["chapter", chapterId] })
    },
  })
}

export function useRelationships(projectId: number | undefined) {
  return useQuery({
    queryKey: ["relationships", projectId],
    queryFn: () => api.get<RelationshipData>(`/projects/${projectId}/relationships`),
    enabled: !!projectId,
  })
}

export function useMapRelationships() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (chapterId: number) =>
      api.post<{ relationships_created: number; total: number }>(`/chapters/${chapterId}/relationships`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["relationships"] })
    },
  })
}
