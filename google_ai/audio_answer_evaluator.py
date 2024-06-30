import google.generativeai as genai
from flask import current_app
from google.api_core import exceptions
from typing import Generator
from .config import GENERATION_CONFIG, SAFETY_SETTINGS, DEFAULT_MODEL

SYSTEM_PROMPT = """
You are a kind teacher AI that receives a Question, a correct-answer, and a student-answer as audio file uploaded in this chat. 
Your task is to evaluate the student-answer based on the information from the correct-answer provided. 
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


def evaluate_audio_answer(
        question: str,
        correct_answer: str,
        audio_path: str,
        model_name: str = DEFAULT_MODEL
) -> Generator[str, None, None]:
    """
    Evaluate an audio answer using Google's Generative AI.

    Args:
    question (str): The question being answered.
    correct_answer (str): The correct answer to the question.
    audio_path (str): Path to the audio file containing the student's answer.
    model_name (str): Name of the AI model to use. Defaults to DEFAULT_MODEL.

    Yields:
    str: Chunks of the evaluation text.

    Raises:
    FileNotFoundError: If the audio file is not found.
    exceptions.GoogleAPICallError: If there's an error in the API call.
    """
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
                yield chunk.text

    except FileNotFoundError:
        yield "Error: Audio file not found."
    except exceptions.GoogleAPICallError as e:
        yield f"Error in API call: {str(e)}"
    except Exception as e:
        yield f"An unexpected error occurred: {str(e)}"