import json
from typing import List, Dict, Any, Optional

from .config import DEFAULT_PRO_MODEL
from .utils import execute_genai_operation


def generate_questions(image_paths: List[str], model_name: str = DEFAULT_PRO_MODEL) -> Optional[List[Dict[str, Any]]]:
    """
    Generate questions based on the provided images using Google's Generative AI.

    Args:
    image_paths (List[str]): List of paths to image files.
    model_name (str): Name of the Gemini model to use. Defaults to the value in config.py.

    Returns:
    Optional[List[Dict[str, Any]]]: List of generated questions with their details, or None if generation failed.
    """
    prompt = """
    * make sure that you analyze all the uploaded images 
    * for each image find the relevant topics 
    * for each topic come up with one or more relevant questions
    * questions and answers MUST come from uploaded images ONLY!
    * if you can not analyze provide information on that 
    * do not stop until you have analyzed all images 
    * provide your results as JSON
    * each json element MUST have the following structure: page_nr, question, answer, difficulty_level
    * difficulty_level should be one of: easy, medium, hard
    * be very careful to provide VALID JSON!
    """

    result = None
    for image_path in image_paths:
        response = execute_genai_operation(prompt, file_path=image_path, mime_type="image/jpeg", model_name=model_name)
        if response:
            try:
                parsed_response = json.loads(response)
                if result is None:
                    result = parsed_response
                else:
                    result.extend(parsed_response)
            except json.JSONDecodeError:
                print(f"Failed to parse JSON for image: {image_path}")

    return result
