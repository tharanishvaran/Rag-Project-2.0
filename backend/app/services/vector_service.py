import os
import uuid
import logging
import chromadb
from flask import current_app

logger = logging.getLogger(__name__)

# Singleton ChromaDB client
_chroma_client = None
_collection = None
COLLECTION_NAME = 'smart_doc_ai_chunks'

# Resolve the backend root directory (two levels up from this file)
_BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_chroma_client():
    """Return singleton persistent ChromaDB client."""
    global _chroma_client
    
    if _chroma_client is None:
        persist_dir = current_app.config.get('CHROMA_PERSIST_DIRECTORY', 'chroma_db')
        # Always resolve to an absolute path relative to the backend root
        # so the correct DB is found regardless of the process working directory.
        if not os.path.isabs(persist_dir):
            persist_dir = os.path.join(_BACKEND_ROOT, persist_dir)
        persist_dir = os.path.normpath(persist_dir)
        logger.info(f'Initializing ChromaDB at: {persist_dir}')
        _chroma_client = chromadb.PersistentClient(path=persist_dir)
    
    return _chroma_client


def get_collection():
    """Return the main ChromaDB collection (create if not exists)."""
    global _collection
    
    if _collection is None:
        client = get_chroma_client()
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={'hnsw:space': 'cosine'},  # cosine similarity
        )
        logger.info(f'Using ChromaDB collection: {COLLECTION_NAME} ({_collection.count()} vectors)')
    
    return _collection


class VectorService:
    """Manages ChromaDB vector operations."""
    
    def add_chunks(self, chunks: list[dict], embeddings: list[list[float]]) -> list[str]:
        """
        Add document chunks and their embeddings to ChromaDB.
        
        Args:
            chunks: List of {'text': str, 'metadata': dict}
            embeddings: Corresponding list of embedding vectors
        
        Returns:
            List of generated chunk IDs.
        """
        collection = get_collection()
        
        ids = []
        documents = []
        metadatas = []
        
        for chunk in chunks:
            chunk_id = str(uuid.uuid4())
            ids.append(chunk_id)
            documents.append(chunk['text'])
            
            # ChromaDB metadata values must be str, int, float, or bool
            # None values for int fields must become 0 so $eq filters work
            int_fields = {'user_id', 'document_id', 'category_id', 'page_number'}
            meta = {}
            for k, v in chunk['metadata'].items():
                if v is None:
                    meta[k] = 0 if k in int_fields else ''
                else:
                    meta[k] = v
            metadatas.append(meta)
        
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        
        logger.info(f'Added {len(ids)} chunks to ChromaDB.')
        return ids
    
    def query(
        self,
        query_embedding: list[float],
        user_id: int,
        n_results: int = 5,
        document_id: int = None,
        category_id: int = None,
    ) -> list[dict]:
        """
        Search for relevant chunks using vector similarity.
        Always filters by user_id for data isolation.
        
        Returns list of results with text, metadata, and relevance score.
        """
        collection = get_collection()
        
        # Build where filter — always scope to the user
        # ChromaDB v0.4+ requires $and operator for multiple conditions
        if document_id is not None:
            where_filter = {
                '$and': [
                    {'user_id': {'$eq': user_id}},
                    {'document_id': {'$eq': document_id}},
                ]
            }
        elif category_id is not None:
            where_filter = {
                '$and': [
                    {'user_id': {'$eq': user_id}},
                    {'category_id': {'$eq': category_id}},
                ]
            }
        else:
            # Single condition — no $and needed
            where_filter = {'user_id': {'$eq': user_id}}
        
        try:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_filter,
                include=['documents', 'metadatas', 'distances'],
            )
        except Exception as e:
            logger.error(f'ChromaDB query failed: {e}')
            return []
        
        # Parse results
        parsed = []
        min_relevance = current_app.config.get('RAG_MIN_RELEVANCE_SCORE', 0.0)
        if results and results['ids'] and results['ids'][0]:
            for i, chunk_id in enumerate(results['ids'][0]):
                distance = results['distances'][0][i]
                # Convert cosine distance to similarity score (1 = perfect match)
                relevance_score = 1.0 - distance
                
                if relevance_score < min_relevance:
                    logger.debug(f'Skipping chunk {chunk_id} — score {relevance_score:.3f} below threshold {min_relevance}')
                    continue
                
                parsed.append({
                    'chunk_id': chunk_id,
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'relevance_score': relevance_score,
                })
        
        logger.info(f'ChromaDB query returned {len(parsed)} results (filter: user={user_id}, doc={document_id}, cat={category_id})')
        return parsed
    
    def delete_by_document(self, document_id: int, user_id: int):
        """Remove all chunks belonging to a specific document."""
        collection = get_collection()
        
        try:
            collection.delete(
                where={
                    '$and': [
                        {'user_id': {'$eq': user_id}},
                        {'document_id': {'$eq': document_id}},
                    ]
                }
            )
            logger.info(f'Deleted ChromaDB chunks for document {document_id}')
        except Exception as e:
            logger.error(f'Failed to delete ChromaDB chunks: {e}')
    
    def get_collection_count(self) -> int:
        """Return total number of vectors in the collection."""
        return get_collection().count()
