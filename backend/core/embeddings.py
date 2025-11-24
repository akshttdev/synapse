# backend/core/embeddings.py
"""
ImageBind wrapper with GPU support
Handles image, audio, video, and text embedding
"""

import torch
import numpy as np
from pathlib import Path
from typing import List, Union
import logging
from functools import lru_cache

# Import ImageBind
from imagebind import data
from imagebind.models import imagebind_model
from imagebind.models.imagebind_model import ModalityType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageBindEmbedder:
    """
    Production-ready ImageBind embedder with GPU support
    Supports: images, audio, video, text
    """
    
    def __init__(
        self,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
        batch_size: int = 32,
        model_name: str = "imagebind_huge"
    ):
        self.device = device
        self.batch_size = batch_size
        self.model = self._load_model(model_name)
        
        logger.info(f"✓ ImageBind loaded on {self.device}")
        logger.info(f"Batch size: {self.batch_size}")
    
    @lru_cache(maxsize=1)
    def _load_model(self, model_name: str):
        """Load ImageBind model (cached)"""
        logger.info(f"Loading ImageBind model: {model_name}")
        
        if model_name == "imagebind_huge":
            model = imagebind_model.imagebind_huge(pretrained=True)
        else:
            raise ValueError(f"Unknown model: {model_name}")
        
        model.eval()
        model.to(self.device)
        
        # Optional: Compile for faster inference (PyTorch 2.0+)
        if self.device == "cuda" and hasattr(torch, 'compile'):
            try:
                model = torch.compile(model, mode="reduce-overhead")
                logger.info("✓ Model compiled with torch.compile")
            except Exception as e:
                logger.warning(f"torch.compile failed: {e}")
        
        return model
    
    @torch.inference_mode()
    def embed_images(self, image_paths: List[str]) -> np.ndarray:
        """
        Embed images in batches
        
        Args:
            image_paths: List of image file paths
        
        Returns:
            np.ndarray: (N, 1024) float32 embeddings
        """
        all_embeddings = []
        
        for i in range(0, len(image_paths), self.batch_size):
            batch_paths = image_paths[i:i + self.batch_size]
            
            # Load and transform images
            inputs = {
                ModalityType.VISION: data.load_and_transform_vision_data(
                    batch_paths, self.device
                )
            }
            
            # Generate embeddings
            embeddings = self.model(inputs)
            batch_emb = embeddings[ModalityType.VISION].cpu().numpy()
            all_embeddings.append(batch_emb)
        
        return np.vstack(all_embeddings).astype(np.float32)
    
    @torch.inference_mode()
    def embed_audio(self, audio_paths: List[str]) -> np.ndarray:
        """
        Embed audio files in batches
        
        Args:
            audio_paths: List of audio file paths
        
        Returns:
            np.ndarray: (N, 1024) float32 embeddings
        """
        all_embeddings = []
        
        for i in range(0, len(audio_paths), self.batch_size):
            batch_paths = audio_paths[i:i + self.batch_size]
            
            inputs = {
                ModalityType.AUDIO: data.load_and_transform_audio_data(
                    batch_paths, self.device
                )
            }
            
            embeddings = self.model(inputs)
            batch_emb = embeddings[ModalityType.AUDIO].cpu().numpy()
            all_embeddings.append(batch_emb)
        
        return np.vstack(all_embeddings).astype(np.float32)
    
    @torch.inference_mode()
    def embed_text(self, texts: List[str]) -> np.ndarray:
        """
        Embed text queries in batches
        
        Args:
            texts: List of text strings
        
        Returns:
            np.ndarray: (N, 1024) float32 embeddings
        """
        all_embeddings = []
        
        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i:i + self.batch_size]
            
            inputs = {
                ModalityType.TEXT: data.load_and_transform_text(
                    batch_texts, self.device
                )
            }
            
            embeddings = self.model(inputs)
            batch_emb = embeddings[ModalityType.TEXT].cpu().numpy()
            all_embeddings.append(batch_emb)
        
        return np.vstack(all_embeddings).astype(np.float32)
    
    @torch.inference_mode()
    def embed_videos(
        self, 
        video_paths: List[str],
        sample_frames: int = 8
    ) -> np.ndarray:
        """
        Embed videos by sampling frames and averaging
        
        Args:
            video_paths: List of video file paths
            sample_frames: Number of frames to sample per video
        
        Returns:
            np.ndarray: (N, 1024) float32 embeddings
        """
        from .video_utils import extract_frames
        
        all_embeddings = []
        
        for video_path in video_paths:
            # Extract frames
            frame_paths = extract_frames(
                video_path, 
                num_frames=sample_frames
            )
            
            # Embed frames
            frame_embeddings = self.embed_images(frame_paths)
            
            # Average pooling across frames
            video_embedding = frame_embeddings.mean(axis=0, keepdims=True)
            all_embeddings.append(video_embedding)
            
            # Cleanup temp frames
            for frame_path in frame_paths:
                Path(frame_path).unlink(missing_ok=True)
        
        return np.vstack(all_embeddings).astype(np.float32)
    
    def embed_single(
        self,
        path: str,
        modality: str
    ) -> np.ndarray:
        """
        Convenience method for single file embedding
        
        Args:
            path: File path
            modality: One of: image, audio, video, text
        
        Returns:
            np.ndarray: (1024,) float32 embedding
        """
        if modality == "image":
            return self.embed_images([path])[0]
        elif modality == "audio":
            return self.embed_audio([path])[0]
        elif modality == "video":
            return self.embed_videos([path])[0]
        elif modality == "text":
            return self.embed_text([path])[0]
        else:
            raise ValueError(f"Unknown modality: {modality}")


# Singleton instance (lazy loaded)
_embedder = None

def get_embedder() -> ImageBindEmbedder:
    """Get or create singleton ImageBindEmbedder"""
    global _embedder
    if _embedder is None:
        _embedder = ImageBindEmbedder()
    return _embedder