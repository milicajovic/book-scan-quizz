import google.generativeai as genai
from flask import current_app
from typing import Generator

from app.language_utils import get_language_name
from .config import GENERATION_CONFIG, SAFETY_SETTINGS, DEFAULT_MODEL, SHARED_LANGUAGE_EVALUATION_PROMPT

TEXT_FORMATTING = """Format your response as follows:
- Feedback in the user's native language
- Separator: ####
- Scores in the format:
  Pronunciation: X
  Grammar: Y
  Content: Z

Example output:
[Feedback in user's native language]
####
Pronunciation: 7
Grammar: 6
Content: 8
"""


def evaluate_language_audio(
        user_language: str,
        target_language: str,
        prompt: str,
        audio_file: str,
        model_name: str = DEFAULT_MODEL
) -> Generator[str, None, None]:
    try:
        genai.configure(api_key=current_app.config['GEMINI_API_KEY'])
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=GENERATION_CONFIG,
            safety_settings=SAFETY_SETTINGS
        )
        display_user_lng = get_language_name(user_language)
        display_target_lng = get_language_name(target_language)
        evaluation_prompt = f"""
        {SHARED_LANGUAGE_EVALUATION_PROMPT + TEXT_FORMATTING}
        
        User's native language: {display_user_lng}
        Language being learned: {display_target_lng}
        Speaking prompt: '{prompt}'

        """
        #print(evaluation_prompt)
        # print(audio_file)

        file = genai.upload_file(audio_file, mime_type="audio/wav")

        chat_session = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        file
                    ],
                },
            ]
        )

        response_stream = chat_session.send_message(evaluation_prompt, stream=True)


        for chunk in response_stream:
            if chunk.text:
                yield chunk.text

    except Exception as e:
        error_msg = f"Error in evaluate_language_audio: {str(e)}"
        current_app.logger.error(error_msg)
        yield f"An error occurred: {error_msg}"
