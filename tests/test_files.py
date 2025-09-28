import io


def test_upload_and_list_file(client):
    # Upload a file
    file_content = b"hello resmed!"
    response = client.post(
        "/files/", files={"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
    )
    assert response.status_code == 201
    data = response.json()
    file_id = data["id"]

    # List files
    resp = client.get("/files/")
    items = resp.json()
    assert resp.status_code == 200
    assert len(items) == 1
    assert items[0]["filename"] == "test.txt"

    # Download file
    resp = client.get(f"/files/{file_id}")
    assert resp.status_code == 200
    assert resp.content == file_content
    assert 'attachment; filename="test.txt"' in resp.headers["content-disposition"]


def test_reject_large_file(client):
    big_content = b"x" * (25 * 1024 * 1024)  # 25 MB
    resp = client.post(
        "/files/", files={"file": ("big.txt", io.BytesIO(big_content), "text/plain")}
    )
    assert resp.status_code == 413
    assert "File exceeds 20MB" in resp.json()["detail"]


def test_download_nonexistent_file(client):
    resp = client.get("/files/does-not-exist")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "File not found"


def test_list_when_empty(client):
    # No files uploaded yet
    resp = client.get("/files/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_upload_multiple_files(client):
    contents = [b"file1", b"file2", b"file3"]
    ids = []
    for i, c in enumerate(contents, 1):
        resp = client.post(
            "/files/", files={"file": (f"file{i}.txt", io.BytesIO(c), "text/plain")}
        )
        assert resp.status_code == 201
        ids.append(resp.json()["id"])

    # List should return 3 files
    resp = client.get("/files/")
    items = resp.json()
    filenames = [item["filename"] for item in items]
    assert len(items) == 3
    assert set(filenames) == {"file1.txt", "file2.txt", "file3.txt"}
