import { useState, useCallback, useRef } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { api } from "../api/client"
import type { TranslationData } from "../types"

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000"

export function useTranslation(chapterId: number | undefined) {
  return useQuery({
    queryKey: ["translation", chapterId],
    queryFn: () => api.get<TranslationData>(`/chapters/${chapterId}/translation`),
    enabled: !!chapterId,
  })
}

export function useUpdateTranslation() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, text }: { id: number; text: string }) =>
      api.put(`/chapters/${id}/translation`, { translated_text: text }),
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ["translation", vars.id] })
      qc.invalidateQueries({ queryKey: ["chapter", vars.id] })
    },
  })
}

export function useStreamTranslation() {
  const [streaming, setStreaming] = useState(false)
  const [streamedText, setStreamedText] = useState("")
  const [progress, setProgress] = useState(0)
  const abortRef = useRef<AbortController | null>(null)

  const start = useCallback(async (chapterId: number) => {
    setStreaming(true)
    setStreamedText("")
    setProgress(0)

    abortRef.current = new AbortController()

    try {
      const resp = await fetch(
        `${BASE_URL}/chapters/${chapterId}/translate/stream`,
        { signal: abortRef.current.signal },
      )

      const reader = resp.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) return

      let buffer = ""
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })

        const lines = buffer.split("\n")
        buffer = lines.pop() ?? ""

        for (const line of lines) {
          if (line.startsWith("data:")) {
            try {
              const data = JSON.parse(line.slice(5).trim())
              if (data.text) {
                setStreamedText((prev) => prev + data.text)
                setProgress((p) => p + 1)
              }
            } catch { /* skip */ }
          }
        }
      }
    } catch (e) {
      if (!(e instanceof DOMException && e.name === "AbortError")) {
        throw e
      }
    } finally {
      setStreaming(false)
    }
  }, [])

  const stop = useCallback(() => {
    abortRef.current?.abort()
  }, [])

  return { streaming, streamedText, progress, start, stop }
}
