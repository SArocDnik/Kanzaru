from fastapi.testclient import TestClient


def test_detect_chapters_vietnamese(client: TestClient):
    create = client.post("/projects", json={"name": "VN Novel", "source_lang": "vi"})
    pid = create.json()["id"]

    text = "Chương 1\nNội dung chương 1\n\nChương 2\nNội dung chương 2"
    client.post(f"/projects/{pid}/upload", data={"text": text})

    resp = client.post(f"/projects/{pid}/chapters/detect")
    assert resp.status_code == 201
    chapters = resp.json()
    assert len(chapters) == 2
    assert chapters[0]["title"] == "Chương 1"
    assert chapters[1]["title"] == "Chương 2"
    assert "Nội dung chương 1" in chapters[0]["original_text"]


def test_detect_chapters_no_text(client: TestClient):
    create = client.post("/projects", json={"name": "Empty"})
    pid = create.json()["id"]

    resp = client.post(f"/projects/{pid}/chapters/detect")
    assert resp.status_code == 400


def test_list_chapters_after_detect(client: TestClient):
    create = client.post("/projects", json={"name": "List Test"})
    pid = create.json()["id"]

    client.post(f"/projects/{pid}/upload", data={"text": "Chapter 1\nContent\n\nChapter 2\nMore content"})
    client.post(f"/projects/{pid}/chapters/detect")

    resp = client.get(f"/projects/{pid}/chapters")
    assert resp.status_code == 200
    assert len(resp.json()) == 2
