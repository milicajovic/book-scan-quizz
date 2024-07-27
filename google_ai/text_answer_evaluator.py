import google.generativeai as genai
from flask import current_app
from typing import Generator
from .config import GENERATION_CONFIG, SAFETY_SETTINGS, DEFAULT_MODEL

SYSTEM_PROMPT = """
You are a kind teacher AI that receives a Question, a correct-answer, and a student-answer as text.
Your task is to evaluate the student-answer based on the information from the correct-answer provided.
Analyze the language of correct-answer, and provide response in that language. Your response should be in this language.
You must provide feedback in a friendly and supportive tone. The output should be formatted as a text and should have following segments:

- first segment: A friendly and constructive explanation of what was correct, wrong or missing in the student's answer, aimed at helping the student understand the errors and guiding them on how to improve.
- separator: ####, feedback is finished by the separator ####, which indicates end of the student feedback, after this you will provide grade for correctness and completeness separated by new line character
- correctness: A score between 0-10 that indicates how correct the student's answer is. This score evaluates the accuracy of the content in the student's answer relative to the correct answer.
- completeness: A score between 0-10 that indicates how complete the student's answer is. This score evaluates the completeness of the content in the student's answer relative to the correct answer.

Here is an example of the expected Text output:
Your explanation of photosynthesis correctly mentioned that plants use light! However, it would be helpful to mention that they also need water and carbon dioxide, and that they produce not only oxygen but also glucose. Try to include these aspects next time.
####
Correctness:6
Completeness:5
"""

def evaluate_text_answer(
    question: str,
    correct_answer: str,
    student_answer: str,
    model_name: str = DEFAULT_MODEL
) -> str:
    try:
        genai.configure(api_key=current_app.config['GEMINI_API_KEY'])
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=GENERATION_CONFIG,
            safety_settings=SAFETY_SETTINGS
        )

        prompt = f"""
        Question: '{question}'
        Correct Answer: '{correct_answer}'
        Student Answer: '{student_answer}'

        {SYSTEM_PROMPT}
        """

        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(prompt)

        return response.text

    except Exception as e:
        error_msg = f"Error in evaluate_text_answer: {str(e)}"
        current_app.logger.error(error_msg)
        raise RuntimeError(error_msg)