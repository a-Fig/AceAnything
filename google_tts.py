from dotenv import load_dotenv
import os
from google.cloud import texttospeech

print("google_tts.py")

load_dotenv()


def remove_non_ascii(s):
    s = ''.join(c for c in s if ord(c) < 256)
    bad_characters = ["*", "\\", "'", "\"", "`"]
    for char in bad_characters:
        s = s.replace(char, '')
    return s


def text_to_speech_premium(text, voice_model="en-US-Chirp3-HD-Fenrir"):
    print(f"TTS Premium called with text: {text[:50]}... and voice model: {voice_model}")

    # Set the path to your service account key file
    google_json_key = os.getenv("GOOGLE_JSON_KEY")
    if not google_json_key:
        print("ERROR: GOOGLE_JSON_KEY environment variable not set")
        raise ValueError("GOOGLE_JSON_KEY environment variable not set")

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_json_key
    print(f"Using credentials from: {google_json_key}")

    # Check if the credentials file exists
    if not os.path.exists(google_json_key):
        print(f"ERROR: Credentials file not found: {google_json_key}")
        raise FileNotFoundError(f"Credentials file not found: {google_json_key}")

    try:
        # Initialize the client
        print("Initializing TextToSpeechClient")
        client = texttospeech.TextToSpeechClient()

        text = remove_non_ascii(text)
        print(f"Text after removing non-ASCII: {text[:50]}...")

        # Set the text input
        synthesis_input = texttospeech.SynthesisInput(text=text)

        # Configure voice parameters - using a premium voice (Wavenet)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name=voice_model # Example: Using Wavenet voice D for US English
        )

        # Set audio configuration
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        # Generate speech
        print("Calling synthesize_speech")
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        print(f"Speech synthesis successful, audio length: {len(response.audio_content)} bytes")
        return response.audio_content
    except Exception as e:
        print(f"ERROR in text_to_speech_premium: {str(e)}")
        raise


if __name__ == '__main__':
    pass
