import faiss
import numpy as np
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from app.core.config import settings


class VectorStore:
    """FAISS-based vector store for job embeddings"""
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = None
        self.job_metadata = []  # List of job dicts
        self.job_id_to_idx = {}  # Map job_id -> index position
    
    def create_index(self, embeddings: np.ndarray, metadata: List[Dict]):
        if len(embeddings) != len(metadata):
            raise ValueError("Embeddings and metadata must have same length")
        
        # Create FAISS index (L2 distance, can be changed to Inner Product)
        self.index = faiss.IndexFlatL2(self.dimension)
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add vectors to index
        self.index.add(embeddings.astype('float32'))
        
        # Store metadata
        self.job_metadata = metadata
        
        # Create ID mapping
        for idx, job in enumerate(metadata):
            self.job_id_to_idx[job['id']] = idx
        
        print(f" Index created with {self.index.ntotal} jobs")
    
    def search(
        self, 
        query_embedding: np.ndarray, 
        k: int = 10,
        filters: Optional[Dict] = None
    ) -> List[Tuple[Dict, float]]:
        if self.index is None:
            raise ValueError("Index not created. Call create_index first.")
        
        # Reshape and normalize query
        query = query_embedding.reshape(1, -1).astype('float32')
        faiss.normalize_L2(query)
        
        # Search
        distances, indices = self.index.search(query, k)
        
        # Convert to results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.job_metadata):
                job = self.job_metadata[idx]
                
                # Apply filters if provided
                if filters:
                    if not self._matches_filters(job, filters):
                        continue
                
                # Convert L2 distance to similarity score (0-1)
                similarity = 1 / (1 + dist)
                results.append((job, similarity))
        
        return results
    
    def _matches_filters(self, job: Dict, filters: Dict) -> bool:
        """Check if job matches all filters"""
        for key, value in filters.items():
            if key not in job:
                return False
            if isinstance(value, list):
                if job[key] not in value:
                    return False
            else:
                if job[key] != value:
                    return False
        return True
    
    def save(self, index_path: Optional[Path] = None, metadata_path: Optional[Path] = None):
        if self.index is None:
            raise ValueError("No index to save")
        
        index_path = index_path or Path(settings.VECTOR_INDEX_PATH + ".index")
        metadata_path = metadata_path or Path(settings.VECTOR_INDEX_PATH + "_metadata.json")
        
        # Create directories
        index_path.parent.mkdir(parents=True, exist_ok=True)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, str(index_path))
        
        # Save metadata
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.job_metadata, f, indent=2, ensure_ascii=False)
        
        print(f" Saved index to {index_path}")
        print(f"Saved metadata to {metadata_path}")
    
    def load(self, index_path: Optional[Path] = None, metadata_path: Optional[Path] = None):
        """
        Load index and metadata from disk.
        """
        index_path = index_path or Path(settings.VECTOR_INDEX_PATH + ".index")
        metadata_path = metadata_path or Path(settings.VECTOR_INDEX_PATH + "_metadata.json")
        
        if not index_path.exists():
            raise FileNotFoundError(f"Index not found: {index_path}")
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata not found: {metadata_path}")
        
        # Load FAISS index
        self.index = faiss.read_index(str(index_path))
        
        # Load metadata
        with open(metadata_path, 'r', encoding='utf-8') as f:
            self.job_metadata = json.load(f)
        
        # Rebuild ID mapping
        self.job_id_to_idx = {
            job['id']: idx for idx, job in enumerate(self.job_metadata)
        }
        
        print(f"Loaded index with {self.index.ntotal} jobs")
        print(f" Loaded {len(self.job_metadata)} job metadata")
    
    def get_stats(self) -> Dict:
        """Get index statistics"""
        if self.index is None:
            return {"status": "No index loaded"}
        
        return {
            "total_jobs": self.index.ntotal,
            "dimension": self.dimension,
            "metadata_count": len(self.job_metadata)
        }