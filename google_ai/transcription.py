from typing import Optional

from .config import DEFAULT_MODEL
from .utils import execute_genai_operation


def transcribe_audio(audio_path: str, mime_type: str = "audio/wav", model_name: str = DEFAULT_MODEL) -> Optional[str]:
    """
    Transcribes the audio file at the given path using Google's Generative AI.

    Args:
    audio_path (str): Path to the audio file.
    mime_type (str): MIME type of the audio file. Defaults to "audio/wav".
    model_name (str): Name of the Gemini model to use. Defaults to the value in config.py.

    Returns:
    Optional[str]: The transcribed text, or None if transcription failed.
    """
    prompt = "Transcribe the audio file and provide a summary."
    return execute_genai_operation(prompt, file_path=audio_path, mime_type=mime_type, model_name=model_name)
