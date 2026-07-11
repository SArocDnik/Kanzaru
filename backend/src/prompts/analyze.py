ANALYZE_PROMPT = """You are a story analysis assistant. Analyze the following chapter text and return JSON.

Return ONLY valid JSON, no markdown, no explanation.

JSON structure:
{{
  "summary": "2-3 sentence summary of the chapter",
  "characters": [
    {{
      "name": "character name as appears in text",
      "aliases": ["other names/nicknames"],
      "role": "protagonist|antagonist|supporting|minor",
      "honorifics_used": ["san", "sama", "kun", etc.]
    }}
  ],
  "key_terms": [
    {{
      "term": "important term",
      "meaning": "what it means in context"
    }}
  ]
}}

Chapter text:
{text}
"""

RELATIONSHIP_PROMPT = """You are a story analysis assistant. Given the following characters and chapter text, identify relationships between characters.

Return ONLY valid JSON, no markdown, no explanation.

JSON structure:
{{
  "relationships": [
    {{
      "character_a": "name of first character",
      "character_b": "name of second character",
      "rel_type": "family|romantic|friendship|rivalry|master_servant|other",
      "description": "brief description of the relationship"
    }}
  ]
}}

Characters:
{characters}

Chapter text:
{text}
"""
