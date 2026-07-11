from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


MOCK_ANALYSIS = """{
  "summary": "Hero meets mentor.",
  "characters": [
    {"name": "Taro", "aliases": ["Tarou"], "role": "protagonist", "honorifics_used": ["kun"]}
  ],
  "key_terms": [
    {"term": "ki", "meaning": "energy"}
  ]
}"""


def test_analyze_chapter_api(client: TestClient):
    create = client.post("/projects", json={"name": "Analyze Test", "source_lang": "ja"})
    pid = create.json()["id"]
    client.post(f"/projects/{pid}/upload", data={"text": "Some chapter text content here for analysis."})

    with patch("src.api.routes.chapters.LLMClient") as mock_cls:
        mock_client = MagicMock()
        mock_client.chat.return_value = MOCK_ANALYSIS
        mock_cls.return_value = mock_client

        resp = client.post(f"/projects/{pid}/chapters/detect")
        chapter_id = resp.json()[0]["id"]

        resp = client.post(f"/chapters/{chapter_id}/analyze")
    assert resp.status_code == 200
    data = resp.json()
    assert "Hero" in data["summary"]
    assert data["characters"] == 1


def test_get_analysis(client: TestClient):
    create = client.post("/projects", json={"name": "Get Analysis"})
    pid = create.json()["id"]
    client.post(f"/projects/{pid}/upload", data={"text": "Text"})

    with patch("src.api.routes.chapters.LLMClient") as mock_cls:
        mock_client = MagicMock()
        mock_client.chat.return_value = MOCK_ANALYSIS
        mock_cls.return_value = mock_client

        detect = client.post(f"/projects/{pid}/chapters/detect")
        chapter_id = detect.json()[0]["id"]
        client.post(f"/chapters/{chapter_id}/analyze")

        resp = client.get(f"/chapters/{chapter_id}/analysis")
    assert resp.status_code == 200
    data = resp.json()
    assert data["summary"]
    assert len(data["characters"]) >= 1


def test_analyze_chapter_not_found(client: TestClient):
    resp = client.post("/chapters/9999/analyze")
    assert resp.status_code == 404
