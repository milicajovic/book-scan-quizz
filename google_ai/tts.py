from google.cloud import texttospeech
import tempfile
import logging


def generate_speech_from_ssml(ssml_text):
    """
    Generate speech from SSML text using Google Cloud Text-to-Speech API.

    Args:
    ssml_text (str): The SSML text to convert to speech.

    Returns:
    str: Path to the temporary audio file.

    Raises:
    Exception: If anything goes wrong.
    """
    try:
        client = texttospeech.TextToSpeechClient()

        synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
            temp_audio_file.write(response.audio_content)

        return temp_audio_file.name

    except Exception as e:
        logging.error(f"Shit hit the fan in TTS: {str(e)}")
        raise