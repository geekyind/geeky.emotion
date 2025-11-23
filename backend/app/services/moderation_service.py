"""
Content moderation service with ML-based detection
"""
import logging
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class SeverityLevel(str, Enum):
    """Content severity levels"""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ModerationService:
    """Service for content moderation and safety checks"""
    
    def __init__(self):
        self.crisis_keywords = [
            'suicide', 'kill myself', 'end it all', 'want to die',
            'no reason to live', 'better off dead', 'self harm',
            'cut myself', 'overdose'
        ]
        
        self.harmful_patterns = [
            'how to kill', 'suicide method', 'ways to die',
            'pro ana', 'pro mia', 'thinspo'
        ]
        
        self.toxic_keywords = [
            'hate', 'kill you', 'deserve to die', 'worthless',
            'pathetic', 'loser', 'stupid'
        ]
    
    async def moderate_content(
        self,
        content: str,
        anonymous_id: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Perform multi-stage content moderation
        
        Args:
            content: Content to moderate
            anonymous_id: Anonymous user ID
            context: Additional context
        
        Returns:
            Moderation results with severity and actions
        """
        results = {
            'approved': True,
            'severity': SeverityLevel.SAFE,
            'flags': [],
            'requires_review': False,
            'auto_actions': [],
            'crisis_detected': False,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Stage 1: Crisis detection (highest priority)
        crisis_result = await self._detect_crisis_content(content)
        if crisis_result['detected']:
            results['crisis_detected'] = True
            results['severity'] = SeverityLevel.CRITICAL
            results['flags'].extend(crisis_result['flags'])
            results['requires_review'] = True
            results['auto_actions'].append('hold_post')
            results['auto_actions'].append('alert_moderators')
            results['auto_actions'].append('show_crisis_resources')
        
        # Stage 2: Harmful content detection
        harmful_result = await self._detect_harmful_content(content)
        if harmful_result['detected']:
            results['flags'].extend(harmful_result['flags'])
            if results['severity'] == SeverityLevel.SAFE:
                results['severity'] = SeverityLevel.HIGH
                results['requires_review'] = True
                results['auto_actions'].append('hold_post')
        
        # Stage 3: Toxicity detection
        toxicity_result = await self._detect_toxicity(content)
        if toxicity_result['score'] > 0.7:
            results['flags'].append('high_toxicity')
            if results['severity'] == SeverityLevel.SAFE:
                results['severity'] = SeverityLevel.MEDIUM
                results['requires_review'] = True
        
        # Stage 4: PII leak check
        pii_result = self._check_pii_leak(content)
        if pii_result['found_pii']:
            results['flags'].append('pii_detected')
            results['requires_review'] = True
        
        # Determine final approval status
        if results['severity'] in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]:
            results['approved'] = False
        
        return results
    
    async def _detect_crisis_content(self, content: str) -> Dict:
        """
        Detect crisis-related content requiring immediate intervention
        
        Args:
            content: Content to analyze
        
        Returns:
            Detection results
        """
        content_lower = content.lower()
        
        detected_keywords = []
        for keyword in self.crisis_keywords:
            if keyword in content_lower:
                detected_keywords.append(keyword)
        
        # Check for harmful patterns
        for pattern in self.harmful_patterns:
            if pattern in content_lower:
                detected_keywords.append(f"pattern:{pattern}")
        
        return {
            'detected': len(detected_keywords) > 0,
            'flags': [f'crisis:{kw}' for kw in detected_keywords],
            'keywords_found': detected_keywords
        }
    
    async def _detect_harmful_content(self, content: str) -> Dict:
        """
        Detect harmful content patterns
        
        Args:
            content: Content to analyze
        
        Returns:
            Detection results
        """
        content_lower = content.lower()
        
        harmful_flags = []
        
        # Check for pro-eating disorder content
        pro_ed_keywords = ['pro ana', 'pro mia', 'thinspo', 'bonespo']
        for keyword in pro_ed_keywords:
            if keyword in content_lower:
                harmful_flags.append(f'pro_ed:{keyword}')
        
        # Check for self-harm encouragement
        self_harm_encourage = ['do it', 'just end it', 'no one cares']
        for phrase in self_harm_encourage:
            if phrase in content_lower:
                harmful_flags.append(f'encourage_harm:{phrase}')
        
        return {
            'detected': len(harmful_flags) > 0,
            'flags': harmful_flags
        }
    
    async def _detect_toxicity(self, content: str) -> Dict:
        """
        Detect toxic language (simplified version)
        
        In production, use ML model like Perspective API or fine-tuned BERT
        
        Args:
            content: Content to analyze
        
        Returns:
            Toxicity score and details
        """
        content_lower = content.lower()
        
        toxic_count = 0
        for keyword in self.toxic_keywords:
            toxic_count += content_lower.count(keyword)
        
        # Simple scoring (0-1 scale)
        # In production, use ML model
        score = min(toxic_count * 0.2, 1.0)
        
        return {
            'score': score,
            'threshold_exceeded': score > 0.5,
            'toxic_terms_count': toxic_count
        }
    
    def _check_pii_leak(self, content: str) -> Dict:
        """
        Check for PII that shouldn't be in anonymized content
        
        Args:
            content: Content to check
        
        Returns:
            PII detection results
        """
        import re
        
        pii_found = {}
        
        # Email
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content):
            pii_found['email'] = True
        
        # Phone
        if re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', content):
            pii_found['phone'] = True
        
        # SSN
        if re.search(r'\b\d{3}-\d{2}-\d{4}\b', content):
            pii_found['ssn'] = True
        
        return {
            'found_pii': len(pii_found) > 0,
            'pii_types': list(pii_found.keys())
        }
    
    async def queue_for_review(
        self,
        post_id: str,
        severity: SeverityLevel,
        flags: List[str]
    ) -> Dict:
        """
        Queue post for human moderation review
        
        Args:
            post_id: Post identifier
            severity: Severity level
            flags: List of moderation flags
        
        Returns:
            Queue assignment details
        """
        # Determine SLA based on severity
        sla_hours = {
            SeverityLevel.CRITICAL: 1,
            SeverityLevel.HIGH: 4,
            SeverityLevel.MEDIUM: 24,
            SeverityLevel.LOW: 72
        }
        
        return {
            'post_id': post_id,
            'severity': severity,
            'sla_hours': sla_hours.get(severity, 72),
            'queue': 'crisis' if severity == SeverityLevel.CRITICAL else 'standard',
            'flags': flags,
            'queued_at': datetime.utcnow().isoformat()
        }


# Singleton instance
moderation_service = ModerationService()
