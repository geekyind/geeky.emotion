"""
Similar post discovery using semantic embeddings
"""
import logging
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)


class SimilarPostService:
    """Service for finding similar posts using ML embeddings"""
    
    def __init__(self):
        # Load sentence transformer model
        self.model = SentenceTransformer(settings.SENTENCE_TRANSFORMER_MODEL)
        logger.info(f"Loaded sentence transformer model: {settings.SENTENCE_TRANSFORMER_MODEL}")
        
        # In production, use vector database like Pinecone or Milvus
        # For now, use in-memory storage
        self.embeddings_cache = {}
        self.posts_cache = {}
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate semantic embedding for text
        
        Args:
            text: Input text
        
        Returns:
            Embedding vector
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    async def find_similar_posts(
        self,
        query_content: str,
        top_k: int = 10,
        similarity_threshold: float = 0.7,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Find similar posts using semantic similarity
        
        Args:
            query_content: Content to find similar posts for
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score (0-1)
            filters: Optional filters (e.g., has_positive_resolution, topic)
        
        Returns:
            List of similar posts with similarity scores
        """
        # Generate embedding for query
        query_embedding = self.generate_embedding(query_content)
        
        # In production, query vector database
        # For now, compute similarity with cached embeddings
        similar_posts = []
        
        for post_id, post_data in self.posts_cache.items():
            # Apply filters
            if filters:
                if not self._matches_filters(post_data, filters):
                    continue
            
            # Compute cosine similarity
            post_embedding = self.embeddings_cache.get(post_id)
            if post_embedding is None:
                continue
            
            similarity = self._cosine_similarity(query_embedding, post_embedding)
            
            if similarity >= similarity_threshold:
                similar_posts.append({
                    'post_id': post_id,
                    'similarity_score': float(similarity),
                    'content_preview': post_data['content'][:200],
                    'topics': post_data.get('topics', []),
                    'has_positive_resolution': post_data.get('has_positive_resolution', False),
                    'response_count': post_data.get('response_count', 0)
                })
        
        # Sort by similarity score and return top_k
        similar_posts.sort(key=lambda x: x['similarity_score'], reverse=True)
        return similar_posts[:top_k]
    
    async def index_post(
        self,
        post_id: str,
        content: str,
        metadata: Dict
    ) -> bool:
        """
        Index a post for similarity search
        
        Args:
            post_id: Post identifier
            content: Post content
            metadata: Additional metadata (topics, resolution status, etc.)
        
        Returns:
            True if indexed successfully
        """
        try:
            # Generate and store embedding
            embedding = self.generate_embedding(content)
            self.embeddings_cache[post_id] = embedding
            
            # Store post data
            self.posts_cache[post_id] = {
                'content': content,
                'topics': metadata.get('topics', []),
                'has_positive_resolution': metadata.get('has_positive_resolution', False),
                'response_count': metadata.get('response_count', 0),
                'emotional_intensity': metadata.get('emotional_intensity', 5)
            }
            
            logger.info(f"Indexed post: {post_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error indexing post {post_id}: {e}")
            return False
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Compute cosine similarity between two vectors
        
        Args:
            vec1: First vector
            vec2: Second vector
        
        Returns:
            Similarity score (0-1)
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _matches_filters(self, post_data: Dict, filters: Dict) -> bool:
        """
        Check if post matches filter criteria
        
        Args:
            post_data: Post data
            filters: Filter criteria
        
        Returns:
            True if post matches filters
        """
        # Check positive resolution filter
        if 'has_positive_resolution' in filters:
            if post_data.get('has_positive_resolution') != filters['has_positive_resolution']:
                return False
        
        # Check topic filter
        if 'topics' in filters:
            required_topics = set(filters['topics'])
            post_topics = set(post_data.get('topics', []))
            if not required_topics.intersection(post_topics):
                return False
        
        # Check moderation status
        if 'moderation_approved' in filters:
            if post_data.get('moderation_approved') != filters['moderation_approved']:
                return False
        
        return True
    
    async def get_recommendation_explanation(
        self,
        query_content: str,
        recommended_post: Dict
    ) -> str:
        """
        Generate human-readable explanation for why a post was recommended
        
        Args:
            query_content: Original query content
            recommended_post: Recommended post data
        
        Returns:
            Explanation string
        """
        similarity_score = recommended_post['similarity_score']
        
        if similarity_score > 0.9:
            similarity_desc = "very similar"
        elif similarity_score > 0.8:
            similarity_desc = "quite similar"
        elif similarity_score > 0.7:
            similarity_desc = "somewhat similar"
        else:
            similarity_desc = "related"
        
        explanation = f"This post is {similarity_desc} to your experience "
        
        if recommended_post.get('has_positive_resolution'):
            explanation += "and has received helpful responses from the community."
        else:
            explanation += "and others are going through something similar."
        
        if recommended_post.get('response_count', 0) > 0:
            explanation += f" It has {recommended_post['response_count']} supportive responses."
        
        return explanation


# Singleton instance
similar_post_service = SimilarPostService()
