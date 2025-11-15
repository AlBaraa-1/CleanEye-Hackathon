"""
Email Intent Classifier Tool - Classify email intents using NLP
"""
import logging
from typing import Dict, Any, List
import re
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)


class EmailIntentClassifier:
    """
    Rule-based email intent classifier with confidence scoring
    """
    
    # Define intent patterns (keywords and phrases)
    INTENT_PATTERNS = {
        "inquiry": [
            r'\b(question|wondering|curious|clarification|information|details|help)\b',
            r'\b(what|when|where|who|why|how)\b.*\?',
            r'\b(could you|can you|would you).*\b(explain|tell|provide|share)\b'
        ],
        "complaint": [
            r'\b(complaint|issue|problem|disappointed|frustrated|unhappy|angry)\b',
            r'\b(not working|broken|failed|error|mistake)\b',
            r'\b(terrible|awful|worst|horrible|unacceptable)\b'
        ],
        "request": [
            r'\b(please|kindly|request|need|require|would like)\b',
            r'\b(send|provide|share|give|deliver|forward)\b.*\b(me|us)\b',
            r'\b(need|want|looking for)\b'
        ],
        "feedback": [
            r'\b(feedback|suggestion|recommend|improve|enhancement)\b',
            r'\b(think|believe|feel|opinion)\b.*\b(should|could|would)\b',
            r'\b(great|excellent|good|nice|appreciate|love)\b'
        ],
        "meeting": [
            r'\b(meeting|schedule|appointment|call|discuss|conference)\b',
            r'\b(available|availability|free time|calendar)\b',
            r'\b(reschedule|postpone|cancel|confirm)\b'
        ],
        "order": [
            r'\b(order|purchase|buy|payment|invoice|receipt)\b',
            r'\b(shipping|delivery|tracking|status)\b',
            r'\b(product|item|package)\b'
        ],
        "urgent": [
            r'\b(urgent|asap|immediately|critical|emergency|priority)\b',
            r'\b(time-sensitive|deadline|due)\b',
            r'!!+|\bIMPORTANT\b'
        ],
        "follow_up": [
            r'\b(follow up|following up|checking in|reminder)\b',
            r'\b(haven\'t heard|waiting for|still pending)\b',
            r'\b(previous|earlier|sent|mentioned)\b.*\b(email|message)\b'
        ],
        "thank_you": [
            r'\b(thank|thanks|grateful|appreciate|gratitude)\b',
            r'\b(wonderful|excellent|helpful)\b.*\b(work|help|support)\b'
        ],
        "application": [
            r'\b(apply|application|position|job|role|opportunity)\b',
            r'\b(resume|cv|cover letter|portfolio)\b',
            r'\b(interested in|applying for)\b'
        ]
    }
    
    def classify(self, email_text: str) -> Dict[str, Any]:
        """
        Classify email intent with confidence scores.
        
        Args:
            email_text: Email text to classify
            
        Returns:
            Dictionary with primary intent, confidence, and secondary intents
        """
        if not email_text or not email_text.strip():
            raise ValueError("Email text cannot be empty")
        
        # Convert to lowercase for matching
        text_lower = email_text.lower()
        
        # Calculate scores for each intent
        intent_scores = {}
        
        for intent, patterns in self.INTENT_PATTERNS.items():
            score = 0
            matches = 0
            
            for pattern in patterns:
                found = re.findall(pattern, text_lower, re.IGNORECASE)
                if found:
                    matches += len(found)
                    score += len(found)
            
            # Normalize score
            if score > 0:
                intent_scores[intent] = min(score / 3.0, 1.0)  # Cap at 1.0
        
        # If no patterns matched, classify as "general"
        if not intent_scores:
            return {
                "intent": "general",
                "confidence": 0.5,
                "secondary_intents": [],
                "explanation": "No specific intent patterns detected"
            }
        
        # Sort by score
        sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Get primary intent
        primary_intent = sorted_intents[0][0]
        primary_confidence = sorted_intents[0][1]
        
        # Get secondary intents (top 3)
        secondary_intents = [
            {"intent": intent, "confidence": round(score, 3)}
            for intent, score in sorted_intents[1:4]
        ]
        
        return {
            "intent": primary_intent,
            "confidence": round(primary_confidence, 3),
            "secondary_intents": secondary_intents,
            "explanation": f"Detected {primary_intent} intent based on keyword analysis"
        }


def classify_email_intent(email_text: str) -> Dict[str, Any]:
    """
    Classify the intent of an email.
    
    Args:
        email_text: Email text to classify
        
    Returns:
        Dictionary with classification results
    """
    try:
        classifier = EmailIntentClassifier()
        result = classifier.classify(email_text)
        
        # Add metadata
        result["email_length"] = len(email_text)
        result["word_count"] = len(email_text.split())
        
        return result
        
    except Exception as e:
        logger.error(f"Error classifying email intent: {e}")
        raise


def classify_batch_emails(emails: List[str]) -> Dict[str, Any]:
    """
    Classify multiple emails at once.
    
    Args:
        emails: List of email text strings
        
    Returns:
        Dictionary with batch classification results
    """
    try:
        classifier = EmailIntentClassifier()
        results = []
        
        for idx, email_text in enumerate(emails):
            try:
                result = classifier.classify(email_text)
                result["email_index"] = idx
                results.append(result)
            except Exception as e:
                logger.error(f"Error classifying email {idx}: {e}")
                results.append({
                    "email_index": idx,
                    "error": str(e),
                    "intent": "error",
                    "confidence": 0.0
                })
        
        # Aggregate statistics
        intent_distribution = {}
        for result in results:
            intent = result.get("intent", "unknown")
            intent_distribution[intent] = intent_distribution.get(intent, 0) + 1
        
        return {
            "total_emails": len(emails),
            "results": results,
            "intent_distribution": intent_distribution
        }
        
    except Exception as e:
        logger.error(f"Error in batch email classification: {e}")
        raise


def extract_email_features(email_text: str) -> Dict[str, Any]:
    """
    Extract features from an email for analysis.
    
    Args:
        email_text: Email text
        
    Returns:
        Dictionary with extracted features
    """
    try:
        features = {
            "length": len(email_text),
            "word_count": len(email_text.split()),
            "sentence_count": len(re.split(r'[.!?]+', email_text)),
            "has_greeting": bool(re.search(r'\b(hi|hello|dear|hey)\b', email_text.lower())),
            "has_closing": bool(re.search(r'\b(regards|sincerely|thanks|best)\b', email_text.lower())),
            "question_count": len(re.findall(r'\?', email_text)),
            "exclamation_count": len(re.findall(r'!', email_text)),
            "has_url": bool(re.search(r'https?://', email_text)),
            "has_email_address": bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email_text))
        }
        
        return features
        
    except Exception as e:
        logger.error(f"Error extracting email features: {e}")
        raise
