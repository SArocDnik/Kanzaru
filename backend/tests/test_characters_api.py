from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


MOCK_ANALYSIS = """{
  "summary": "Hero meets mentor.",
  "characters": [
    {"name": "Taro", "aliases": ["Tarou"], "role": "protagonist", "honorifics_used": ["kun"]},
    {"name": "Sora", "aliases": [], "role": "supporting", "honorifics_used": ["san"]}
  ],
  "key_terms": []
}"""

MOCK_RELS = """{
  "relationships": [
    {"character_a": "Taro", "character_b": "Sora", "rel_type": "friendship", "description": "Friends"}
  ]
}"""


def _setup_chapter_with_chars(client: TestClient):
    create = client.post("/projects", json={"name": "Char Test", "source_lang": "ja"})
    pid = create.json()["id"]
    client.post(f"/projects/{pid}/upload", data={"text": "Some text"})

    with patch("src.api.routes.chapters.LLMClient") as mock_cls:
        mock_c = MagicMock()
        mock_c.chat.return_value = MOCK_ANALYSIS
        mock_cls.return_value = mock_c
        detect = client.post(f"/projects/{pid}/chapters/detect")
        ch_id = detect.json()[0]["id"]
        client.post(f"/chapters/{ch_id}/analyze")

    return pid, ch_id


def test_list_characters(client: TestClient):
    pid, ch_id = _setup_chapter_with_chars(client)
    resp = client.get(f"/projects/{pid}/characters")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 2
    names = [c["name"] for c in data]
    assert "Taro" in names
    assert "Sora" in names


def test_map_relationships_api(client: TestClient):
    pid, ch_id = _setup_chapter_with_chars(client)

    with patch("src.api.routes.characters.LLMClient") as mock_cls:
        mock_c = MagicMock()
        mock_c.chat.return_value = MOCK_RELS
        mock_cls.return_value = mock_c
        resp = client.post(f"/chapters/{ch_id}/relationships")

    assert resp.status_code == 200
    assert resp.json()["relationships_created"] >= 1


def test_list_relationships(client: TestClient):
    pid, ch_id = _setup_chapter_with_chars(client)

    with patch("src.api.routes.characters.LLMClient") as mock_cls:
        mock_c = MagicMock()
        mock_c.chat.return_value = MOCK_RELS
        mock_cls.return_value = mock_c
        client.post(f"/chapters/{ch_id}/relationships")

    resp = client.get(f"/projects/{pid}/relationships")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["nodes"]) >= 2
    assert len(data["edges"]) >= 1
    assert data["edges"][0]["rel_type"] == "friendship"
