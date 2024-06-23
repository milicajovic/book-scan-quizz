import os
import google.generativeai as genai
from flask import current_app


#os.environ["GEMINI_API_KEY"] = "AIzaSyDQyT_XQpie3uGPa2DbYGf6yaNie0CzyV0"
# genai.configure(api_key=os.environ["GEMINI_API_KEY"])


def transcribe_file(file_path: str) -> str:
    """
    Transcribe the audio file at the given path.

    :param file_path: Path to the audio file
    :return: Transcribed text
    """
    # Placeholder implementation
    return "Hello World! This is a placeholder transcription."



"""
Install the Google AI Python SDK

$ pip install google-generativeai

See the getting started guide for more information:
https://ai.google.dev/gemini-api/docs/get-started/python
"""




def upload_to_gemini(path, mime_type="audio/wav"):
  """Uploads the given file to Gemini.

  See https://ai.google.dev/gemini-api/docs/prompting_with_media
  """
  file = genai.upload_file(path, mime_type=mime_type)
  print(f"Uploaded file '{file.display_name}' as: {file.uri}")
  return file

def transcribe_audio(audio_path: str, mime_type="audio/wav") -> str:
  genai.configure(api_key=current_app.config['GEMINI_API_KEY'])
  # See https://ai.google.dev/api/python/google/generativeai/GenerativeModel
  generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
  }

  model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    # safety_settings = Adjust safety settings
    # See https://ai.google.dev/gemini-api/docs/safety-settings
  )

  # TODO Make these files available on the local file system
  # You may need to update the file paths
  # files = [
  #   upload_to_gemini(audio_path, mime_type=mime_type),
  # ]
  file = upload_to_gemini(audio_path, mime_type=mime_type)

  chat_session = model.start_chat(
    history=[
      {
        "role": "user",
        "parts": [file],
      },
    ]
  )

  response = chat_session.send_message("give a short summary of the file")

  print(response.text)
  return response.text