import google.generativeai as genai
from flask import current_app
from google.api_core import exceptions
from typing import Generator
from .config import GENERATION_CONFIG, SAFETY_SETTINGS, DEFAULT_MODEL

SYSTEM_PROMPT = """
You are a kind teacher AI that receives a Question, a correct-answer, and a student-answer as audio file uploaded in this chat. 
Your task is to evaluate the student-answer based on the information from the correct-answer provided.
If you think that the answer is empty, ask the user to repeat the answer and fix potential issues in recording.
Analyze the language of correct-answer,  and provide response in that language.Your response should be in this language.
You must provide feedback in a friendly and supportive tone. The output should be formatted as a text and should have following segments 

- first segment: A friendly and constructive explanation of what was wrong or missing in the student's answer, aimed at helping the student understand the errors and guiding them on how to improve.
- separator: ####, feedback is finished by the separator ####, which indicates end of the student feedback, after this you will provide grade for correctness and completeness 
- correctness: A score between 0-10 that indicates how correct the student's answer is. This score evaluates the accuracy of the content in the student's answer relative to the correct answer.
- completeness: A score between 0-10 that indicates how correct the student's answer is. This score evaluates the completeness of the content in the student's answer relative to the correct answer.

Here is an example of the expected Text output:
Your explanation of photosynthesis correctly mentioned that plants use light! However, it would be helpful to mention that they also need water and carbon dioxide, and that they produce not only oxygen but also glucose. Try to include these aspects next time.
####
Correctness:6
Completeness:5
"""


import logging
import traceback

import logging
import traceback
from google.api_core import exceptions

def evaluate_audio_answer(
        question: str,
        correct_answer: str,
        audio_path: str,
        model_name: str = DEFAULT_MODEL
) -> Generator[str, None, None]:
    try:
        genai.configure(api_key=current_app.config['GEMINI_API_KEY'])
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=GENERATION_CONFIG,
            safety_settings=SAFETY_SETTINGS,
            system_instruction=SYSTEM_PROMPT
        )

        prompt = f"Question: '{question}'\nCorrect Answer: '{correct_answer}'\n"

        parts = []
        file = genai.upload_file(audio_path, mime_type="audio/wav")
        parts.append(file)
        parts.append(prompt)

        chat_session = model.start_chat(history=[{"role": "user", "parts": parts}])
        response_stream = chat_session.send_message(prompt, stream=True)

        for chunk in response_stream:
            if chunk.text:
                #print("x*x*x*x" + chunk.text)
                yield chunk.text

    except Exception as e:
        error_msg = f"Error in evaluate_audio_answer: {str(e)}"
        logging.error(error_msg)
        #logging.error(f"Call Stack:\n{traceback.format_exc()}")
        raise  # Re-raise the original exception