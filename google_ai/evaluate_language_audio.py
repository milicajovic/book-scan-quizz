import google.generativeai as genai
from flask import current_app
from typing import Generator

from app.language_utils import get_language_name
from .config import GENERATION_CONFIG, SAFETY_SETTINGS, DEFAULT_MODEL

LANGUAGE_EVALUATION_PROMPT = """
You are an AI language tutor evaluating a learner's spoken response. You will receive:
1. The user's native language (user_language)
2. The language they are learning (target_language)
3. The prompt given to the learner
4. An audio file of the learner's response, is already uploaded in this chat.

Your task is to:
1. Evaluate the response for pronunciation, grammar, and content relevance
2. Provide friendly, constructive feedback in the user's native language
3. Give a score from 1-10 for each aspect: pronunciation, grammar, and content

Format your response as follows:
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
        {LANGUAGE_EVALUATION_PROMPT}
        
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
