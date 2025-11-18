# app/main.py
import os
import tempfile
import subprocess
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import numpy as np
import torch
import torchaudio

from .imagebind_service import encode_audio_tensor
from .milvus_client import init_collection, search_vector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("synapse-backend")

app = FastAPI(title="Synapse Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_methods=["*"],
    allow_headers=["*"]
)

# Ensure collection exists on startup
@app.on_event("startup")
def startup_event():
    try:
        init_collection()
        logger.info("Milvus collection initialized.")
    except Exception as e:
        logger.exception("Milvus init failed: %s", e)


def ffmpeg_convert_to_wav16(input_path: str, output_path: str):
    """
    Uses ffmpeg to convert input -> 16kHz mono WAV (PCM S16)
    """
    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-ar", "16000",
        "-ac", "1",
        "-f", "wav",
        output_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def load_audio_to_tensor(path: str):
    """
    Load wav file and return a torch.FloatTensor normalized (-1.0, 1.0), shape (1, N)
    """
    waveform, sr = torchaudio.load(path)  # waveform shape (channels, samples)
    if sr != 16000:
        waveform = torchaudio.functional.resample(waveform, sr, 16000)
    if waveform.ndim == 2 and waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)
    waveform = waveform.float()
    # Normalize if necessary (already typically in [-1,1])
    max_val = waveform.abs().max()
    if max_val > 0:
        waveform = waveform / max_val
    return waveform  # (1, N)


@app.post("/api/embed/audio")
async def embed_audio(file: UploadFile = File(...)):
    """
    Accepts multipart file upload, returns embedding vector (JSON)
    """
    try:
        contents = await file.read()
        # write to tmp input file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[-1] or ".bin") as tmp_in:
            tmp_in.write(contents)
            tmp_in.flush()
            tmp_in_path = tmp_in.name

        # convert to wav16k
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_out:
            tmp_out_path = tmp_out.name
        try:
            ffmpeg_convert_to_wav16(tmp_in_path, tmp_out_path)
        except subprocess.CalledProcessError as e:
            logger.exception("ffmpeg convert failed.")
            raise HTTPException(status_code=400, detail="Audio conversion failed.")

        # load to tensor
        audio_tensor = load_audio_to_tensor(tmp_out_path)  # torch tensor (1, N)
        # pass to ImageBind wrapper
        emb = encode_audio_tensor(audio_tensor)
        # cleanup tmp files
        try:
            os.unlink(tmp_in_path)
            os.unlink(tmp_out_path)
        except Exception:
            pass

        return JSONResponse({"embedding": emb.tolist() if hasattr(emb, "tolist") else list(map(float, emb))})
    except Exception as e:
        logger.exception("embed_audio failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/search/audio")
async def search_audio(file: UploadFile = File(...), top_k: int = 10):
    """
    Accepts audio file upload, returns nearest neighbors from Milvus
    """
    try:
        contents = await file.read()
        # write to tmp input file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[-1] or ".bin") as tmp_in:
            tmp_in.write(contents)
            tmp_in.flush()
            tmp_in_path = tmp_in.name

        # convert to wav16k
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_out:
            tmp_out_path = tmp_out.name
        try:
            ffmpeg_convert_to_wav16(tmp_in_path, tmp_out_path)
        except subprocess.CalledProcessError:
            raise HTTPException(status_code=400, detail="Audio conversion failed.")

        # load to tensor
        audio_tensor = load_audio_to_tensor(tmp_out_path)  # torch tensor
        emb = encode_audio_tensor(audio_tensor)  # numpy array

        # cleanup
        try:
            os.unlink(tmp_in_path)
            os.unlink(tmp_out_path)
        except Exception:
            pass

        # call Milvus search (expects numpy array)
        results = search_vector(np.array(emb).astype(np.float32), top_k=top_k)
        return JSONResponse({"results": results})
    except Exception as e:
        logger.exception("search_audio failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}
