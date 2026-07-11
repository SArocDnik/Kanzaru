from fastapi.testclient import TestClient


def test_create_project(client: TestClient):
    resp = client.post("/projects", json={"name": "Test Novel", "source_lang": "ja", "target_lang": "vi"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Test Novel"
    assert data["source_lang"] == "ja"
    assert data["target_lang"] == "vi"
    assert "id" in data


def test_list_projects(client: TestClient):
    client.post("/projects", json={"name": "Novel A"})
    client.post("/projects", json={"name": "Novel B"})
    resp = client.get("/projects")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


def test_get_project(client: TestClient):
    create = client.post("/projects", json={"name": "Get Me"})
    pid = create.json()["id"]
    resp = client.get(f"/projects/{pid}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Get Me"


def test_get_project_not_found(client: TestClient):
    resp = client.get("/projects/9999")
    assert resp.status_code == 404


def test_delete_project(client: TestClient):
    create = client.post("/projects", json={"name": "Delete Me"})
    pid = create.json()["id"]
    resp = client.delete(f"/projects/{pid}")
    assert resp.status_code == 204
    assert client.get(f"/projects/{pid}").status_code == 404


def test_delete_project_cascade(client: TestClient):
    create = client.post("/projects", json={"name": "Cascade Test"})
    pid = create.json()["id"]
    client.post(f"/projects/{pid}/chapters", json={"chapter_number": 1, "title": "Ch.1", "original_text": "text"})
    client.delete(f"/projects/{pid}")
    assert client.get(f"/projects/{pid}").status_code == 404
