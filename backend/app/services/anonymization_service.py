"""
Anonymization service for user posts and content
"""
from datetime import datetime, timedelta
import hashlib
import secrets
import logging
import re
from typing import Dict, Optional

from app.core.security import scrub_pii, generate_anonymous_id
from app.core.config import settings

logger = logging.getLogger(__name__)


class AnonymizationService:
    """Service for anonymizing user content and protecting privacy"""
    
    def __init__(self):
        self.salt_secret = settings.SALT_SECRET
    
    def anonymize_post(
        self,
        user_id: str,
        email: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Anonymize user post with PII scrubbing and temporal fuzzing
        
        Args:
            user_id: User's unique identifier (Cognito sub)
            email: User's email
            content: Post content to anonymize
            metadata: Optional metadata (tags, intensity, etc.)
        
        Returns:
            Dictionary with anonymized post data
        """
        # Generate anonymous ID
        anonymous_id = generate_anonymous_id(user_id, email)
        
        # Scrub PII from content
        clean_content = scrub_pii(content)
        
        # Additional content cleaning
        clean_content = self._remove_identifying_info(clean_content)
        
        # Fuzz timestamp for privacy
        fuzzy_timestamp = self._fuzz_timestamp(datetime.utcnow())
        
        # Extract context safely
        context_data = self._extract_safe_context(clean_content, metadata)
        
        return {
            'anonymous_id': anonymous_id,
            'content': clean_content,
            'timestamp': fuzzy_timestamp,
            'context': context_data,
            'original_length': len(content),
            'scrubbed': content != clean_content
        }
    
    def _remove_identifying_info(self, text: str) -> str:
        """
        Remove additional identifying information beyond basic PII
        
        Args:
            text: Input text
        
        Returns:
            Cleaned text with identifying info removed
        """
        # Remove common name patterns (e.g., "My name is John")
        text = re.sub(r'\b(?:my name is|i\'m|i am)\s+[A-Z][a-z]+\b', 
                     '[NAME REMOVED]', text, flags=re.IGNORECASE)
        
        # Remove location mentions (basic implementation)
        # In production, use NER models for better detection
        text = re.sub(r'\b(?:I live in|from)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b',
                     '[LOCATION REMOVED]', text, flags=re.IGNORECASE)
        
        # Remove URLs
        text = re.sub(r'https?://\S+', '[LINK REMOVED]', text)
        
        # Remove @mentions and #hashtags that might identify
        text = re.sub(r'@\w+', '[MENTION]', text)
        
        return text
    
    def _fuzz_timestamp(self, timestamp: datetime) -> datetime:
        """
        Add temporal fuzzing to prevent correlation attacks
        
        Rounds timestamp to nearest 15-minute interval for k-anonymity
        
        Args:
            timestamp: Original timestamp
        
        Returns:
            Fuzzed timestamp
        """
        # Round to nearest 15 minutes
        minutes = (timestamp.minute // 15) * 15
        fuzzed = timestamp.replace(minute=minutes, second=0, microsecond=0)
        
        # Add small random offset (-5 to +5 minutes) for additional privacy
        random_offset = secrets.randbelow(11) - 5
        fuzzed = fuzzed + timedelta(minutes=random_offset)
        
        return fuzzed
    
    def _extract_safe_context(self, content: str, metadata: Optional[Dict]) -> Dict:
        """
        Extract contextual information that's safe to store
        
        Args:
            content: Cleaned content
            metadata: Additional metadata
        
        Returns:
            Safe context dictionary
        """
        context = {
            'word_count': len(content.split()),
            'character_count': len(content),
            'has_question': '?' in content,
            'sentiment_hint': self._basic_sentiment_analysis(content)
        }
        
        # Add safe metadata
        if metadata:
            safe_fields = ['topics', 'emotional_intensity', 'content_type']
            for field in safe_fields:
                if field in metadata:
                    context[field] = metadata[field]
        
        return context
    
    def _basic_sentiment_analysis(self, text: str) -> str:
        """
        Basic sentiment analysis (should be replaced with ML model)
        
        Args:
            text: Input text
        
        Returns:
            Sentiment label: positive, negative, neutral
        """
        # Simple keyword-based analysis (placeholder)
        positive_words = {'happy', 'good', 'great', 'better', 'hope', 'joy', 'love'}
        negative_words = {'sad', 'bad', 'worst', 'hate', 'angry', 'depressed', 'anxious'}
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def verify_anonymization(self, original_content: str, anonymized_content: str) -> Dict:
        """
        Verify that anonymization was successful
        
        Args:
            original_content: Original user content
            anonymized_content: Anonymized content
        
        Returns:
            Verification results
        """
        # Check for common PII patterns
        pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
        }
        
        found_pii = {}
        for pii_type, pattern in pii_patterns.items():
            matches = re.findall(pattern, anonymized_content)
            if matches:
                found_pii[pii_type] = len(matches)
        
        is_safe = len(found_pii) == 0
        
        return {
            'is_safe': is_safe,
            'found_pii': found_pii,
            'scrubbed_items': original_content != anonymized_content,
            'message': 'Anonymization verified' if is_safe else 'PII detected in anonymized content'
        }


# Singleton instance
anonymization_service = AnonymizationService()
