from google.cloud import texttospeech
import tempfile

def generate_speech_from_ssml(ssml_text):
    """
    Generate speech from SSML text using Google Cloud Text-to-Speech API.

    Args:
    ssml_text (str): The SSML text to convert to speech.

    Returns:
    str: Path to the temporary audio file.
    """
    # Instantiate the client
    client = texttospeech.TextToSpeechClient()

    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)

    # Build the voice request
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )

    # Select the type of audio file
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Perform the text-to-speech request
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
        temp_audio_file.write(response.audio_content)

    # Return the path to the temporary file
    return temp_audio_file.name