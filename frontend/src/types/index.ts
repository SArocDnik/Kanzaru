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

export interface ChapterUpdate {
  title?: string
  original_text?: string
  translated_text?: string
  status?: string
}

export interface Character {
  id: number
  name: string
  aliases: string
  role: string
  honorifics: string
  notes: string
}

export interface GraphNode {
  id: number
  name: string
  role: string
}

export interface GraphEdge {
  source: number
  target: number
  rel_type: string
  description: string
  source_name: string
  target_name: string
}

export interface RelationshipData {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

export interface AnalysisData {
  summary: string
  status: string
  characters: Character[]
}

export interface AnalysisResult {
  summary: string
  characters: number
  key_terms: number
}

export interface TranslationData {
  translated_text: string
  status: string
}
