import os
import logging
from sentence_transformers import SentenceTransformer
from flask import current_app

# Prevent HuggingFace network requests on model load
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'

logger = logging.getLogger(__name__)

# Singleton — loaded once at startup
_model_instance = None


def get_embedding_model(model_name: str = None) -> SentenceTransformer:
    """Return the singleton embedding model, loading it if necessary."""
    global _model_instance
    
    if _model_instance is None:
        name = model_name or current_app.config.get('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
        logger.info(f'Loading embedding model locally: {name}')
        try:
            _model_instance = SentenceTransformer(name, local_files_only=True)
        except Exception:
            _model_instance = SentenceTransformer(name)
        logger.info('Embedding model loaded successfully.')
    
    return _model_instance


class EmbeddingService:
    """Generates sentence embeddings using Sentence Transformers."""
    
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for a list of document chunks.
        Uses batch processing for efficiency.
        
        Returns a list of embedding vectors.
        """
        if not texts:
            return []
        
        model = get_embedding_model()
        
        logger.info(f'Generating embeddings for {len(texts)} chunks...')
        embeddings = model.encode(
            texts,
            batch_size=32,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        
        return embeddings.tolist()
    
    def embed_query(self, query: str) -> list[float]:
        """
        Generate an embedding for a single query string.
        Uses the same model to ensure semantic consistency.
        """
        model = get_embedding_model()
        embedding = model.encode(query, convert_to_numpy=True)
        return embedding.tolist()
