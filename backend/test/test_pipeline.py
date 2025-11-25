# backend/tests/test_pipeline.py
"""
Pipeline test for Synapse (S3 presigned + Qdrant Cloud)

Run inside host or backend container:
docker compose exec backend python3 tests/test_pipeline.py
"""
import requests
import time
from pathlib import Path
import os

API = "http://localhost:8000/api/v1"
TEST_IMAGE = "https://picsum.photos/800"  # random image
TMP = "/tmp/synapse_test.jpg"

def download_image():
    r = requests.get(TEST_IMAGE)
    with open(TMP, "wb") as f:
        f.write(r.content)
    return TMP

def wait_for_task(task_id, timeout=120):
    start = time.time()
    while time.time() - start < timeout:
        r = requests.get(f"{API}/upload/status/{task_id}")
        if r.status_code != 200:
            time.sleep(1); continue
        data = r.json()
        status = data.get("status")
        if status in ("SUCCESS", "FAILURE"):
            return data
        time.sleep(1)
    return {"status": "timeout"}

def run():
    print("Downloading test image...")
    p = download_image()

    files = {"file": ("test.jpg", open(p, "rb"), "image/jpeg")}
    data = {"media_type": "image"}
    print("Uploading to API...")
    r = requests.post(f"{API}/upload/", files=files, data=data)
    print("Upload response:", r.status_code, r.text)
    resp = r.json()
    task_id = resp["task_id"]
    media_id = resp["media_id"]

    print("Waiting for pipeline to finish...")
    out = wait_for_task(task_id, timeout=180)
    print("Task result:", out)

    emb_path = f"/app/data/embeddings/{media_id}.npy"
    print("Check embedding file exists at:", emb_path)
    # When running on host, path may be under ./data/embeddings
    if os.path.exists(emb_path) or os.path.exists(f"data/embeddings/{media_id}.npy"):
        print("Embedding exists ✅")
    else:
        print("Embedding missing ❌")

    # Verify presigned thumbnail
    # We try to call search endpoint or inspect returned results from task (if any)
    print("Pipeline test finished.")

if __name__ == "__main__":
    run()
