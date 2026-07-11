from fastapi.testclient import TestClient
import io


def test_upload_text(client: TestClient):
    create = client.post("/projects", json={"name": "Upload Test"})
    pid = create.json()["id"]

    resp = client.post(
        f"/projects/{pid}/upload",
        data={"text": "This is some uploaded text content."},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["chapter_id"] > 0
    assert data["chars"] > 0


def test_upload_pdf(client: TestClient):
    import fitz
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "This is a text-based PDF with enough content to pass the extraction threshold check.")
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()

    create = client.post("/projects", json={"name": "PDF Upload"})
    pid = create.json()["id"]

    resp = client.post(
        f"/projects/{pid}/upload",
        files={"file": ("test.pdf", buf.getvalue(), "application/pdf")},
    )
    assert resp.status_code == 200
    assert resp.json()["chapter_id"] > 0


def test_upload_nothing(client: TestClient):
    create = client.post("/projects", json={"name": "No Upload"})
    pid = create.json()["id"]

    resp = client.post(f"/projects/{pid}/upload")
    assert resp.status_code == 400
