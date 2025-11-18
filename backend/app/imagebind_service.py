# app/imagebind_service.py
import logging
import numpy as np
import torch

logger = logging.getLogger(__name__)

_imagebind_available = False
_model = None

try:
    # Try to import a common ImageBind wrapper — adjust if your install differs
    # Many ImageBind forks expose a helper name; you should replace below with your actual import.
    # Example (pseudo): from imagebind import imagebind_huge
    # Or: from imagebind.models import imagebind_model
    # Here we attempt a few common names — update for your environment.
    try:
        # Attempt a common entrypoint (replace with your project's import)
        from imagebind.models.imagebind_model import imagebind_huge as _ib
        _model = _ib(pretrained=True)
        _model.eval()
        _imagebind_available = True
    except Exception:
        # try another import path
        from imagebind import ImageBindModel  # if available
        _model = ImageBindModel(pretrained=True)
        _model.eval()
        _imagebind_available = True
except Exception as e:
    logger.warning("ImageBind model not available. Install it in production. Falling back to dummy embeddings. Error: %s", e)
    _imagebind_available = False


def encode_audio_tensor(audio_tensor: torch.Tensor) -> np.ndarray:
    """
    audio_tensor: torch.Tensor shape (1, N) or (N,) float32, sample rate 16000 expected.
    Returns: 1-D numpy float32 embedding vector.
    """
    if _imagebind_available and _model is not None:
        # Real embedding call — adjust depending on actual ImageBind API in your environment.
        # Example: emb = _model({ModalityType.AUDIO: audio_tensor})[ModalityType.AUDIO]
        # Here we try a generic .encode_audio if available:
        try:
            if hasattr(_model, "encode_audio"):
                with torch.no_grad():
                    emb = _model.encode_audio(audio_tensor.to(next(_model.parameters()).device))
                    if isinstance(emb, torch.Tensor):
                        return emb.squeeze(0).cpu().numpy()
            # fallback generic call if model uses dict input
            with torch.no_grad():
                # This line is model-specific — modify according to your ImageBind API
                output = _model({"audio": audio_tensor.to(next(_model.parameters()).device)})
                # assume output is dict with 'audio'
                emb = output.get("audio", None) or list(output.values())[0]
                if isinstance(emb, torch.Tensor):
                    return emb.squeeze(0).cpu().numpy()
        except Exception as e:
            logger.exception("Error calling ImageBind model: %s", e)
            # fall through to fallback
    # Fallback deterministic pseudo-embedding
    # Use fixed seed for reproducible values for testing
    rng = np.random.RandomState(12345 + int(audio_tensor.numel() % 1000))
    dummy = rng.normal(size=(512,)).astype(np.float32)
    return dummy
