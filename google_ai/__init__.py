"""
Google AI Module

This module provides functionality for transcription and question generation
using Google's AI services.
"""

from . import config
from .question_generator import generate_questions
from .transcription import transcribe_audio

__all__ = ['transcribe_audio', 'generate_questions', 'config']

# Version of the google_ai module
__version__ = "0.2.0"
