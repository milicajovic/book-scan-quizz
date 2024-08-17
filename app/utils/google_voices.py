from google.cloud import texttospeech

def get_supported_voices():
    """
    Fetches and prints the list of supported languages and voices by Google Text-to-Speech.
    """

    client = texttospeech.TextToSpeechClient()

    # Performs the list voices request
    voices = client.list_voices()

    # Iterate through the voices and print their language codes
    languages = set()
    for voice in voices.voices:
        print(voice)
        languages.add(voice.language_codes[0])

    print("Supported Languages:")
    for language in languages:
        print(language)

if __name__ == "__main__":
    get_supported_voices()