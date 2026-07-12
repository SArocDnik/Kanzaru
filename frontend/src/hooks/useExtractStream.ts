import { useState, useCallback, useRef } from "react"

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000"

export interface ExtractPageProgress {
  page: number
  total: number
  method: string
  chars: number
}

export function useExtractStream() {
  const [streaming, setStreaming] = useState(false)
  const [progress, setProgress] = useState<ExtractPageProgress | null>(null)
  const [done, setDone] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const abortRef = useRef<AbortController | null>(null)

  const start = useCallback(async (chapterId: number) => {
    setStreaming(true)
    setDone(false)
    setError(null)
    setProgress(null)

    abortRef.current = new AbortController()

    try {
      const resp = await fetch(
        `${BASE_URL}/chapters/${chapterId}/extract/stream`,
        { signal: abortRef.current.signal },
      )

      const reader = resp.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) return

      let buffer = ""
      while (true) {
        const { done: readerDone, value } = await reader.read()
        if (readerDone) break
        buffer += decoder.decode(value, { stream: true })

        const lines = buffer.split("\n")
        buffer = lines.pop() ?? ""

        for (const line of lines) {
          if (line.startsWith("data:")) {
            try {
              const data = JSON.parse(line.slice(5).trim())
              setProgress(data)
            } catch { /* skip */ }
          }
        }
      }
      setDone(true)
    } catch (e) {
      if (!(e instanceof DOMException && e.name === "AbortError")) {
        setError(e instanceof Error ? e.message : String(e))
      }
    } finally {
      setStreaming(false)
    }
  }, [])

  const stop = useCallback(() => {
    abortRef.current?.abort()
  }, [])

  return { streaming, progress, done, error, start, stop }
}
