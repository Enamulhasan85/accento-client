import logging

from bold_voice.conversations.services.ai_services import get_ai_audio_analysis
from bold_voice.conversations.services.word_alignment import WordAlignmentAnalyzer

logger = logging.getLogger(__name__)


class SpeakingPracticeService:
    """
    Service to analyze speaking practice by aligning AI-analyzed audio data
    with a given reference text, and computing scores.
    """

    def __init__(self, audio_file, reference_text):
        self.audio_file = audio_file
        self.reference_text = reference_text

    def analyze(self):
        # Step 01: AI audio analysis
        audio_data = get_ai_audio_analysis(self.audio_file)
        comparison_words_info = audio_data.get('word_list_serializable')

        # Step 02:  Text matching
        reference_words = self.reference_text.split()
        comparison_words = [word_info['word'] for word_info in comparison_words_info]

        word_alignment_analyzer = WordAlignmentAnalyzer(reference_words, comparison_words)
        alignment_result = word_alignment_analyzer.analyze()

        # Step 03: Calculate scores
        word_scores = self._calculate_word_scores(alignment_result, comparison_words_info)
        final_score = self._calculate_final_score(word_scores)

        return {
            'score': final_score,
            'word_scores': word_scores
        }

    @staticmethod
    def _calculate_word_scores(alignment_result, comparison_words_info):
        comparison_index = 0
        word_scores = []

        for word_info in alignment_result:
            status = word_info.get('status')
            similarity_score = word_info.get('similarity_score')
            comparison_index = word_info.get('comparison_index')
            score = 0.0
            start = None
            end = None

            if status in ['matched', 'mismatch']:
                spoken_info = comparison_words_info[comparison_index]
                spoken_score = spoken_info.get('score')
                start = spoken_info.get('start')
                end = spoken_info.get('end')

                if status == 'matched':
                    score = spoken_score
                elif status == 'mismatch':
                    calculated_score = (spoken_score * 0.3 + similarity_score * 0.7)
                    score = min(spoken_score, calculated_score)

                comparison_index += 1

            word_scores.append({
                'word': word_info.get('word'),
                'status': status,
                'score': score,
                'start': start,
                'end': end
            })

        return word_scores

    @staticmethod
    def _calculate_final_score(word_scores):
        total_score = sum(word['score'] for word in word_scores)
        return (total_score / len(word_scores))
