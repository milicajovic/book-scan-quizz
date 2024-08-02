"""
Google AI Module

This module provides functionality for transcription and question generation
using Google's AI services.
"""

from . import config
from .question_generator import generate_questions
from .transcription import transcribe_audio

from .audio_answer_evaluator import evaluate_audio_answer
from .text_answer_evaluator import evaluate_text_answer

__all__ = ['transcribe_audio', 'generate_questions',
           'evaluate_audio_answer', 'evaluate_text_answer',
           'evaluate_language_audio',
           'config']

# Version of the google_ai module
__version__ = "0.2.0"
