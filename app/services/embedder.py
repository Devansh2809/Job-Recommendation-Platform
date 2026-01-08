"""
Embedding generation using SentenceTransformers.
Converts text (resumes, job descriptions) into dense vector representations.
"""
from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
from app.core.config import settings


class Embedder:
    """Generate embeddings for text using SentenceTransformer"""
    
    def __init__(self, model_name: str = None):
        """
        Initialize embedder with specified model.
        
        Args:
            model_name: Name of the SentenceTransformer model
                       Default: 'all-MiniLM-L6-v2' (fast, good quality)
                       Alternatives: 'all-mpnet-base-v2' (slower, better quality)
        """
        self.model_name = model_name or settings.EMBEDDING_MODEL
        print(f"Loading embedding model: {self.model_name}...")
        self.model = SentenceTransformer(self.model_name)
        print(f"✅ Model loaded. Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text string
        
        Returns:
            1D numpy array (embedding vector)
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def embed_batch(self, texts: List[str], batch_size: int = 32, show_progress: bool = True) -> np.ndarray:
        """
        Generate embeddings for multiple texts efficiently.
        
        Args:
            texts: List of text strings
            batch_size: Number of texts to process at once
            show_progress: Show progress bar
        
        Returns:
            2D numpy array (num_texts x embedding_dim)
        """
        if not texts:
            raise ValueError("Text list cannot be empty")
        
        # Filter out empty texts
        valid_texts = [t for t in texts if t and t.strip()]
        
        if len(valid_texts) != len(texts):
            print(f"⚠️ Filtered out {len(texts) - len(valid_texts)} empty texts")
        
        embeddings = self.model.encode(
            valid_texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )
        
        return embeddings
    
    def get_embedding_dim(self) -> int:
        """Get the dimensionality of embeddings"""
        return self.model.get_sentence_embedding_dimension()


# Singleton instance for reuse
_embedder_instance = None

def get_embedder() -> Embedder:
    """Get or create embedder instance (singleton pattern)"""
    global _embedder_instance
    if _embedder_instance is None:
        _embedder_instance = Embedder()
    return _embedder_instance