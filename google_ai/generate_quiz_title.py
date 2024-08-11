from flask import current_app
from google import generativeai as genai

from google_ai import DEFAULT_MODEL, GENERATION_CONFIG, SAFETY_SETTINGS


def generate_quiz_title(questions, model_name=DEFAULT_MODEL):
    """
    Generate a quiz title based on the given questions using Google's Generative AI.

    Args:
    questions (list): List of Question objects.
    model_name (str): Name of the Gemini model to use. Defaults to the value in config.py.

    Returns:
    str: Generated quiz title.
    """
    try:
        genai.configure(api_key=current_app.config['GEMINI_API_KEY'])
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=GENERATION_CONFIG,
            safety_settings=SAFETY_SETTINGS
        )

        # Prepare the prompt
        questions_text = "\n".join([f"- {q.question_text}" for q in questions])
        prompt = f"Generate a concise and engaging title for a quiz based on these questions:\n{questions_text}\nThe title should be no more than 6 words long."

        # Generate the title
        response = model.generate_content(prompt)

        # Extract and return the generated title
        return response.text.strip()

    except Exception as e:
        current_app.logger.error(f"Error in generate_quiz_title: {str(e)}")
        return "Untitled Quiz"  # Fallback title in case of an error
