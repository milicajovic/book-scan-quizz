from typing import Optional

import google.generativeai as genai
from flask import current_app

from .config import GENERATION_CONFIG, SAFETY_SETTINGS, DEFAULT_MODEL


def execute_genai_operation(
        prompt: str,
        file_path: Optional[str] = None,
        mime_type: Optional[str] = None,
        model_name: str = DEFAULT_MODEL
) -> Optional[str]:
    """
    Executes a Google AI operation with the given parameters.

    Args:
    prompt (str): The prompt to send to the AI model.
    file_path (Optional[str]): Path to the file to be processed, if any.
    mime_type (Optional[str]): MIME type of the file, if a file is provided.
    model_name (str): Name of the Gemini model to use.

    Returns:
    Optional[str]: The response from the AI model, or None if an error occurred.
    """
    try:
        genai.configure(api_key=current_app.config['GEMINI_API_KEY'])

        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=GENERATION_CONFIG,
            safety_settings=SAFETY_SETTINGS
        )

        parts = []
        if file_path:
            file = genai.upload_file(file_path, mime_type=mime_type)
            parts.append(file)
        parts.append(prompt)

        chat_session = model.start_chat(history=[{"role": "user", "parts": parts}])
        response = chat_session.send_message(prompt)

        return response.text

    except Exception as e:
        current_app.logger.error(f"Error in execute_genai_operation: {str(e)}")
        return None
