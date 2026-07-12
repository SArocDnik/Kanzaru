import { useMutation, useQueryClient } from "@tanstack/react-query"
import { api } from "../api/client"
import type { UploadResult } from "../types"

export function useUpload() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ projectId, file, text }: { projectId: number; file?: File; text?: string }) => {
      const formData = new FormData()
      if (file) formData.append("file", file)
      if (text) formData.append("text", text)
      return api.upload<UploadResult>(`/projects/${projectId}/upload`, formData)
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["projects"] }),
  })
}
