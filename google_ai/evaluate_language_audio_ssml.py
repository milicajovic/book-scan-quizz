import google.generativeai as genai
from flask import current_app
from .config import GENERATION_CONFIG, SAFETY_SETTINGS, DEFAULT_MODEL

LANGUAGE_EVALUATION_PROMPT = """
You are an AI language tutor evaluating a learner's spoken response. You will receive:
1. The user's native language (user_language)
2. The language they are learning (target_language)
3. The prompt given to the learner
4. An audio file of the learner's response, which is already uploaded in this chat.

Your task is to:
1. Evaluate the response for pronunciation, grammar, and content relevance
2. Provide friendly, constructive feedback in the user's native language
3. Give a score from 1-10 for each aspect: pronunciation, grammar, and content

Format your response as valid SSML (Speech Synthesis Markup Language) with the following structure:
<speak>
  <voice name="[VOICE FOR TARGET LANGUAGE]">
    [Correct answer in the target language]
  </voice>
  <voice name="[VOICE FOR USER'S NATIVE LANGUAGE]">
    [Feedback and scores in the user's native language]
  </voice>
</speak>

Example SSML output:
<speak>
  <voice name="en-US-Standard-C">
    Good attempt! Your pronunciation was clear, but remember to use <voice name="de-DE-Standard-A">"Ihnen"</voice>
     for formal situations.    
     ###Pronunciation: 8
    Grammar: 9
    Content: 7
  </voice>
</speak>

Ensure that you use appropriate voice names for each language. Common voice names include:
- English: en-US-Standard-C
- German: de-DE-Standard-A
- French: fr-FR-Standard-A
- Spanish: es-ES-Standard-A
"""


def evaluate_language_audio_ssml(
        user_language: str,
        target_language: str,
        prompt: str,
        audio_file: str,
        model_name: str = DEFAULT_MODEL
) -> str:
    try:
        genai.configure(api_key=current_app.config['GEMINI_API_KEY'])
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=GENERATION_CONFIG,
            safety_settings=SAFETY_SETTINGS
        )

        evaluation_prompt = f"""
        {LANGUAGE_EVALUATION_PROMPT}

        User's native language: {user_language}
        Language being learned: {target_language}
        Speaking prompt: '{prompt}'
        """

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

        response = chat_session.send_message(evaluation_prompt)
        return response.text  # This should be the SSML string

    except Exception as e:
        error_msg = f"Error in evaluate_language_audio_ssml: {str(e)}"
        current_app.logger.error(error_msg)
        raise  # Re-raise the exception instead of returning an error SSML