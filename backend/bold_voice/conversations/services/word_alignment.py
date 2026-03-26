import logging
import string
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class WordAlignmentAnalyzer:
    def __init__(self, reference_words: list[str], comparison_words: list[str]):
        self.reference_words = reference_words
        self.comparison_words = comparison_words

    def analyze(self) -> list[dict[str, float | str]]:
        """
        Analyze and return word-wise alignment and scores.
        """

        try:
            reference_words_compare = [word.strip(string.punctuation).lower() for word in self.reference_words]
            comparison_words_compare = [word.strip(string.punctuation).lower() for word in self.comparison_words]

            matcher = SequenceMatcher(None, reference_words_compare, comparison_words_compare)
            opcodes = matcher.get_opcodes()
            logger.error(f"Text matcher opcodes: {opcodes}")

            result = []
            for tag, ref_start, ref_end, cmp_start, cmp_end in opcodes:
                comparison_index = cmp_start
                if tag == 'equal':
                    for idx in range(ref_start, ref_end):
                        result.append({
                            'word': self.reference_words[idx],
                            'comparison_index': comparison_index,
                            'status': 'matched',
                            'similarity_score': 1
                        })
                        comparison_index += 1

                elif tag == 'replace':
                    for idx in range(ref_start, ref_end):
                        ref_word = reference_words_compare[idx]
                        cmp_word = None
                        if comparison_index < cmp_end:
                            cmp_word = comparison_words_compare[comparison_index]

                        similarity_score = 0
                        if cmp_word:
                            similarity_score = SequenceMatcher(None, ref_word, cmp_word).ratio()

                        result.append({
                            'word': self.reference_words[idx],
                            'comparison_index': comparison_index if similarity_score >= 0.7 else None,
                            'status': 'mismatch' if similarity_score >= 0.7 else 'missing',
                            'similarity_score': similarity_score if similarity_score >= 0.7 else 0,
                        })
                        if similarity_score >= 0.7:
                            comparison_index += 1

                elif tag == 'delete':
                    for idx in range(ref_start, ref_end):
                        result.append({
                            'word': self.reference_words[idx],
                            'comparison_index': None,
                            'status': 'missing',
                            'similarity_score': 0
                        })

            return result
        except Exception as e:
            logger.error(f"Word Alignment error during analysis: {e}")
            return []
