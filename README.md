Synapse — Multimodal Vector Search Engine
“Search anything with anything — text, images, audio, video.”
🚀 Overview

Synapse is a fully GPU-accelerated multimodal embedding system built on top of:

Meta ImageBind — single embedding space for image, text, audio, video

Qdrant — vector search database

FastAPI — backend API

Celery — distributed workers (upload + embedding)

Redis — caching + queueing backend

Docker + CUDA — GPU-ready environment

Synapse lets users:

🔍 Search using any modality

Search images using text

Search videos using audio

Search audio using images

Search images using images

Search videos using text

and any cross-modal combination…

🧠 Use ImageBind to get unified embeddings

All modalities are embedded to the same 1024-dimensional vector space.

⚡ Scale to millions of items using:

Qdrant HNSW + product quantization

Redis caching

GPU-accelerated workers

Distributed Celery workers

📦 Architecture Diagram
                ┌────────────────────┐
                │   Next.js Frontend │
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │    FastAPI API     │
                └─────────┬──────────┘
                          │
         ┌────────────────┴────────────────┐
         ▼                                 ▼
┌────────────────────┐          ┌──────────────────────┐
│  Redis (cache/bus) │◄────────►│   Celery Workers     │
└────────────────────┘          │  ├ Upload Worker     │
                                │  ├ Embedding Worker  │
                                └──────────────────────┘
                                            │
                                            ▼
                                   ┌────────────────┐
                                   │   ImageBind    │
                                   └────────────────┘
                                            │
                                            ▼
                                   ┌────────────────┐
                                   │    Qdrant DB   │
                                   └────────────────┘

🛠 Installation

Synapse supports:

Mac (CPU only) — development

Linux GPU (recommended) — production

Windows WSL2 + GPU — supported

🐳 Running Using Docker (Recommended)
1. Install system dependencies
Linux (GPU):
sudo apt install docker.io docker-compose-plugin


Install NVIDIA Container Toolkit:

curl https://nvidia.github.io/nvidia-container-toolkit/gpgkey | sudo apt-key add -
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl https://nvidia.github.io/nvidia-container-toolkit/$distribution/nvidia-container-toolkit.list | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt update
sudo apt install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

Test GPU visibility:
docker run --gpus all nvidia/cuda:11.8.0-base nvidia-smi

2. Clone Synapse
git clone https://github.com/your-org/synapse
cd synapse

3. Create .env file
cp backend/.env.example backend/.env


Fill in keys (AWS/B2 optional).

4. Start all services
docker compose up --build


Services started:

FastAPI backend → localhost:8000

Qdrant → localhost:6333

Redis → localhost:6379

Celery worker → auto-running

5. Test ImageBind + full pipeline
docker compose exec backend python3 tests/test_pipeline.py


If everything is green → Synapse is fully working.

🧪 Manual GPU Validation
docker compose exec worker python3 - <<EOF
import torch
print("CUDA:", torch.cuda.is_available(), "GPUs:", torch.cuda.device_count())
EOF

🔍 Usage
Search with text:
POST /api/v1/search
{
  "query": "a dog running",
  "modality": "text",
  "top_k": 20
}

Upload:
POST /api/v1/upload
multipart/form-data:
 - file=@image.jpg
 - media_type=image

🧠 Training / Re-training Embeddings

Synapse does NOT need training — it uses pretrained ImageBind.

But you can:

Fine-tune for your domain

Add your own embeddings

Rebuild the entire index

To embed a batch:
python3 scripts/embed_folder.py --path assets/images

🗜 Embedding Compression

Qdrant supports:

✔ Product Quantization (PQ)
✔ Optimized Product Quantization (OPQ)
✔ Scalar quantization

Use this to compress:

docker exec -it qdrant qdrant-cli update-collection media \
  --optimizers-config='{"memmap_threshold":10000}'

🏎 Scaling Synapse

Add more Celery workers

Switch Qdrant to distributed mode

Add GPU worker autoscaling (AWS ECS / Kubernetes)

Add MinIO/S3 storage

Add async prefetching and thumbnail generation

📚 Project Structure
synapse/
  backend/
    api/
    core/
    services/
    workers/
    data/
    Dockerfile
  frontend/
  docker-compose.yml
  README.md