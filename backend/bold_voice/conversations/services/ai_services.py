import logging
import random

from deepgram import (
    DeepgramClient,
    PrerecordedOptions, FileSource,
)
from django.conf import settings
from openai import OpenAI

from bold_voice.conversations.api.v1.exceptions import AudioAnalysisFailed
from bold_voice.conversations.models import Category
from config.settings.base import env

OPENAI_API_KEY = env.str('OPENAI_API_KEY')
DEEPGRAM_API_KEY = env.str('DEEPGRAM_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)
deepgram = DeepgramClient(DEEPGRAM_API_KEY)

logger = logging.getLogger(__name__)


def get_ai_transcript(title, context, ai_role, ai_character, scenario_type, voice_chat):
    """""
    Generate a natural and engaging voice-chat question.

    :param title: Title of the scenario
    :param context: Context describing the scenario
    :param ai_role: Role of the AI in the conversation
    :param ai_character: Character instance of the AI in the conversation
    :param scenario_type: Scenario type
    :param voice_chat: Voice chat messages to use as context for the question generation
    :return: A dynamically generated question

    Generates an AI response transcript.
    If voice_chat is provided, generate a response based on it.
    Otherwise, generate an initial message.
    """""

    chat_history = [
        {
            "role": "system",
            "content": (
                f"You are an AI assistant playing the role of {ai_role} in a voice chat with a human. "
                "Speak naturally, using friendly, clear, and simple English. "
                "The scenario context provided below will guide your tone, personality, and behavior throughout the conversation. "
                "Stay focused on the current scenario and keep your replies relevant to it—even as the conversation evolves. "
                "Your tone and personality should match the scenario below. "
                "Keep your replies short—1 to 3 sentences—like real conversation. "
                "Always ask a simple, friendly follow-up question after each message. "
                "Avoid sounding robotic, overly scripted, using difficult words or drifting into unrelated scenarios."
                "Use everyday, human-like phrases that are easy to understand."
            )
        },
        {
            "role": "user",
            "content": (
                f"The conversation is titled '{title}'.\n"
                f"In this scenario, you are acting as: {ai_role} ({ai_character.name} - {ai_character.voice_type}).\n"
                f"Context of the situation: {context}\n"
                f"The user's name is: {voice_chat.user.get_short_name()}.\n"
                "Please reply naturally based on this scenario. "
                "Use short, simple sentences. "
                "Ask a related and easy-to-understand question to keep the conversation going."
            )
        }
    ]

    if voice_chat:
        messages = (
            voice_chat.voice_messages
            .filter(transcript__isnull=False)
            .order_by("-id")[:settings.AI_CHAT_HISTORY_LIMIT]
        )

        for message in reversed(messages):
            chat_history.append({"role": message.role, "content": message.transcript})

    else:
        if Category.Type.TOPIC == scenario_type:
            question_instruction = """
            Create a simple and friendly question for someone who is learning English and speaks very little.
            Use very basic words and short sentences. Avoid grammar that is too hard (no past perfect, no complex phrases).
            Make sure the question is easy to answer in a short sentence.
            
            Examples:
            - What food do you like?
            - Do you have a pet?
            - How are you today?
            
            Start with a question like this, based on the scenario.
            """

            example_instruction = """
            After the question, write a short and friendly answer. 
            Use very simple English. The answer should feel natural and easy to understand.
            
            Example:
            Question: What food do you like?
            Answer: I like pizza. It is hot and tasty.
            
            Another Example:
            Question: Do you have a pet?
            Answer: Yes, I have a cat. Her name is Mimi.
            
            Keep the answer short and friendly, like in a real conversation.
            """

            final_instruction = """
            Now make a question and a short example answer based on the scenario. 
            Use easy English with small words and short sentences. Make it friendly and simple.
            """

        else:
            question_instruction = """
            Create a simple and friendly question for someone who is learning English and speaks very little.
            Use very basic words and short sentences. Avoid grammar that is too hard (no past perfect, no complex phrases).
            Make sure the question is easy to answer in one or two words or a short sentence.
            
            Examples:
            - What food do you like?
            - Do you have a pet?
            - How are you today?
            
            Start with a question like this, based on the scenario.
            """

            example_instruction = None

            final_instruction = """
            Now make a question based on the scenario. 
            Use easy English with small words and short sentences. Make it friendly and simple.
            """

        prompt = f"""
            {question_instruction}
           
            {example_instruction}
            
            {final_instruction}
           """

        chat_history.append({"role": "user", "content": prompt})

    try:
        completion = client.chat.completions.create(
            model=settings.OPENAI_TRANSCRIPT_GENERATION_MODEL,
            messages=chat_history,
        )
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"AI response generation failed: {e}")
        raise RuntimeError("AI response could not be generated at the moment. Please try again later.")


def get_ai_audio_analysis(audio_file):
    """
    Analyze an audio file using Deepgram's transcription service.
    :param audio_file: The audio file to analyze
    :return: A dictionary containing the transcript, score, word list, and other metrics.
    """
    try:
        buffer_data = audio_file.read()

        payload: FileSource = {
            "buffer": buffer_data,
        }

        options = PrerecordedOptions(
            model=settings.DEEPGRAM_AUDIO_ANALYSIS_MODEL,
            smart_format=True,
        )

        response = deepgram.listen.rest.v("1").transcribe_file(payload, options)

        transcript = response.results.channels[0].alternatives[0].transcript
        word_list = response.results.channels[0].alternatives[0].words
        word_list_serializable = [
            {"word": word.punctuated_word, "start": word.start, "end": word.end, "score": word.confidence}
            for word in word_list
        ]

        if len(word_list_serializable) == 0:
            raise AudioAnalysisFailed("No words spoken in the audio message. Please try again.")

        for word in word_list_serializable:
            if word["score"] >= settings.PERFECT_WORD_MIN_SCORE:
                word["score"] -= random.uniform(0.05, 0.25)
            else:
                word["score"] = max(0, word["score"] - random.uniform(0.20, 0.40))

        total_word_score = sum(word["score"] for word in word_list_serializable)
        num_words_spoken = len(word_list_serializable)
        score = total_word_score / num_words_spoken
        num_perfect_words = sum(
            1 for word in word_list_serializable
            if word["score"] >= settings.PERFECT_WORD_MIN_SCORE
        )
        time_spoken = sum(word["end"] - word["start"] for word in word_list_serializable)

        return {
            "transcript": transcript,
            "score": score,
            "word_list_serializable": word_list_serializable,
            "total_word_score": total_word_score,
            "num_words_spoken": num_words_spoken,
            "num_perfect_words": num_perfect_words,
            "time_spoken": time_spoken,
        }

    except Exception as e:
        logger.error(f"AI audio analysis failed: {e}")
        raise AudioAnalysisFailed("Failed to analyze audio. Please try again later.") from e
