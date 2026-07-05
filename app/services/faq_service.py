"""
FAQ service — keyword-based FAQ matching against the Google Sheets knowledge base.

Uses a simple weighted keyword overlap scoring algorithm.
Designed for ~20-50 FAQ entries; upgrade to vector embeddings for larger corpora.
"""

from typing import Optional
from app.models.faq import FAQEntry, FAQResponse
from app.services.sheets_service import sheets_service
from app.utils.logger import logger


class FAQService:
    """
    FAQ lookup service using keyword-based fuzzy matching.

    Loads FAQ entries from Google Sheets, scores them against
    the caller's question using keyword overlap, and returns
    the best match above a confidence threshold.
    """

    # Minimum keyword overlap ratio to consider a match
    MATCH_THRESHOLD = 0.3

    def __init__(self):
        self._faq_cache: Optional[list[FAQEntry]] = None

    def _load_faqs(self) -> list[FAQEntry]:
        """Load and cache FAQ entries from Google Sheets."""
        if self._faq_cache is not None:
            return self._faq_cache

        raw_records = sheets_service.get_all_faqs()
        entries = []

        for record in raw_records:
            keywords_raw = record.get("Keywords", "")
            keywords = [k.strip().lower() for k in keywords_raw.split(",") if k.strip()]

            entries.append(
                FAQEntry(
                    id=record.get("ID", 0),
                    category=record.get("Category", ""),
                    question=record.get("Question", ""),
                    answer=record.get("Answer", ""),
                    keywords=keywords,
                )
            )

        self._faq_cache = entries
        logger.info(f"INFO - Cached {len(entries)} FAQ entries")
        return entries

    def invalidate_cache(self) -> None:
        """Clear the FAQ cache to force a reload from Sheets on next query."""
        self._faq_cache = None
        logger.info("INFO - FAQ cache invalidated")

    def _tokenize(self, text: str) -> set[str]:
        """
        Tokenize text into lowercase words, stripping punctuation.

        Args:
            text: Input text string.

        Returns:
            Set of lowercase word tokens.
        """
        import re
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        return set(words)

    def _calculate_score(self, question_tokens: set[str], faq_entry: FAQEntry) -> float:
        """
        Calculate a match score between the caller's question and an FAQ entry.

        Uses a weighted combination of:
        - Keyword match ratio (weight: 0.6)
        - Question text overlap ratio (weight: 0.4)

        Args:
            question_tokens: Tokenized caller question.
            faq_entry: FAQ entry to score against.

        Returns:
            Score between 0.0 and 1.0.
        """
        if not question_tokens:
            return 0.0

        # Score against keywords
        keyword_set = set(faq_entry.keywords)
        if keyword_set:
            keyword_overlap = len(question_tokens & keyword_set) / len(keyword_set)
        else:
            keyword_overlap = 0.0

        # Score against question text
        faq_question_tokens = self._tokenize(faq_entry.question)
        if faq_question_tokens:
            question_overlap = len(question_tokens & faq_question_tokens) / len(faq_question_tokens)
        else:
            question_overlap = 0.0

        # Weighted combination
        return (0.6 * keyword_overlap) + (0.4 * question_overlap)

    def lookup(self, question: str) -> FAQResponse:
        """
        Find the best-matching FAQ answer for a caller's question.

        Args:
            question: The caller's question as transcribed by Retell.

        Returns:
            FAQResponse with the best match or a not-found message.
        """
        logger.info(f"INFO - FAQ lookup: '{question}'")

        if not question.strip():
            return FAQResponse(
                found=False,
                message="I didn't catch your question. Could you please repeat it?",
            )

        faqs = self._load_faqs()

        if not faqs:
            return FAQResponse(
                found=False,
                message=(
                    "I'm sorry, I don't have that information right now. "
                    "Would you like me to transfer you to our front desk team?"
                ),
            )

        question_tokens = self._tokenize(question)

        # Score all entries and find the best match
        scored = [
            (faq, self._calculate_score(question_tokens, faq))
            for faq in faqs
        ]
        scored.sort(key=lambda x: x[1], reverse=True)

        best_faq, best_score = scored[0]

        logger.info(f"INFO - Best FAQ match: score={best_score:.2f}, id={best_faq.id}, q='{best_faq.question}'")

        if best_score >= self.MATCH_THRESHOLD:
            return FAQResponse(
                found=True,
                answer=best_faq.answer,
                category=best_faq.category,
                message=best_faq.answer,
            )
        else:
            return FAQResponse(
                found=False,
                message=(
                    "I'm sorry, I don't have specific information about that. "
                    "Would you like me to transfer you to our front desk "
                    "so they can help you with your question?"
                ),
            )


# Singleton instance
faq_service = FAQService()
