import os
from google.cloud import texttospeech

def generate_audio_from_text(text, output_file="output.mp3",
                            language_code="en-US", voice_name="en-US-Standard-D",
                            speaking_rate=1.0, pitch=0.0,
                            credentials_path="./keys/capable-shape-452021-u9-06c66c66092c.json"):
    """
    Convert text to speech using Google Cloud TTS API

    Args:
        text (str): The text to convert to speech
        output_file (str): Path to save the audio file
        language_code (str): Language code (e.g., 'en-US')
        voice_name (str): Name of the voice to use
        speaking_rate (float): Speed of speech (1.0 is normal)
        pitch (float): Voice pitch (-20.0 to 20.0)
        credentials_path (str): Path to Google Cloud credentials

    Returns:
        str: Path to the generated audio file
    """
    # Set environment variable for credentials
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

    # Initialize the client
    client = texttospeech.TextToSpeechClient()

    # Configure the text input
    synthesis_input = texttospeech.SynthesisInput(text=text)

    # Configure the voice
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=voice_name
    )

    # Configure audio settings
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=speaking_rate,
        pitch=pitch
    )

    # Generate the speech
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else ".", exist_ok=True)

    # Write the audio file
    with open(output_file, "wb") as out:
        out.write(response.audio_content)
        print(f"Audio content written to: {output_file}")

    return output_file

def list_available_voices(language_code=None):
    """List available voices for a specific language"""
    client = texttospeech.TextToSpeechClient()
    voices = client.list_voices(language_code=language_code)

    for voice in voices.voices:
        print(f"Name: {voice.name}")
        print(f"  Languages: {', '.join(voice.language_codes)}")
        print(f"  Gender: {texttospeech.SsmlVoiceGender(voice.ssml_gender).name}")

if __name__ == "__main__":
    # Example usage
    text = "This is a test of the Google Cloud Text-to-Speech API."

    # Generate speech with default voice
    generate_audio_from_text(
        text=text,
        output_file="output/speech.mp3"
    )

    # Generate speech with different voice and parameters
    generate_audio_from_text(
        text=text,
        output_file="output/neural_speech.mp3",
        voice_name="en-US-Neural2-F",  # Neural voice for better quality
        speaking_rate=1.1,
        pitch=0.5
    )

    # Uncomment to list available voices
    # list_available_voices()