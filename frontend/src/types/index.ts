export interface Project {
  id: number
  name: string
  source_lang: string
  target_lang: string
  created_at: string
  updated_at: string
}

export interface ProjectCreate {
  name: string
  source_lang?: string
  target_lang?: string
}

export interface Chapter {
  id: number
  project_id: number
  chapter_number: number
  title: string
  original_text: string
  translated_text: string
  summary: string
  status: string
}

export interface UploadResult {
  chapter_id: number
  pages: number
  chars: number
}
