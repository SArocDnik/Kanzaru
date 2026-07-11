from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


MOCK_TRANSLATION = "Xin chào [cười] thế giới."


def _setup_project_with_chapter(client: TestClient):
    create = client.post("/projects", json={"name": "Translate Test", "source_lang": "ja"})
    pid = create.json()["id"]
    client.post(f"/projects/{pid}/upload", data={"text": "Hello world."})
    resp = client.post(f"/projects/{pid}/chapters/detect")
    chapter_id = resp.json()[0]["id"]
    return pid, chapter_id


def test_translate_chapter_api(client: TestClient):
    pid, ch_id = _setup_project_with_chapter(client)

    with patch("src.api.routes.translate.LLMClient") as mock_cls:
        mock_c = MagicMock()
        mock_c.chat.return_value = MOCK_TRANSLATION
        mock_cls.return_value = mock_c

        resp = client.post(f"/chapters/{ch_id}/translate")

    assert resp.status_code == 200
    assert resp.json()["chars"] > 0

    get_resp = client.get(f"/chapters/{ch_id}/translation")
    assert get_resp.status_code == 200
    assert "Xin chào" in get_resp.json()["translated_text"]


def test_update_translation(client: TestClient):
    pid, ch_id = _setup_project_with_chapter(client)

    resp = client.put(
        f"/chapters/{ch_id}/translation",
        json={"translated_text": "Bản dịch đã chỉnh sửa [thở dài]."},
    )
    assert resp.status_code == 200

    get_resp = client.get(f"/chapters/{ch_id}/translation")
    assert "đã chỉnh sửa" in get_resp.json()["translated_text"]


def test_translate_not_found(client: TestClient):
    resp = client.post("/chapters/9999/translate")
    assert resp.status_code == 404


def test_translate_stream(client: TestClient):
    pid, ch_id = _setup_project_with_chapter(client)

    with patch("src.api.routes.translate.LLMClient") as mock_cls:
        mock_c = MagicMock()
        def fake_stream(msgs):
            for word in ["Xin", " chào", " thế", " giới."]:
                yield word
        mock_c.stream.side_effect = lambda msgs: fake_stream(msgs)
        mock_cls.return_value = mock_c

        resp = client.get(f"/chapters/{ch_id}/translate/stream")

    assert resp.status_code == 200
    body = resp.text
    assert "chunk" in body
    assert "done" in body
