import hashlib
import os

from google.cloud import texttospeech
from moviepy.audio.io.AudioFileClip import AudioFileClip

from app.api.dto.reddit_dto import Comment
from app.core.config import settings


def generate_audio_from_text(text, language_code="en-US", voice_name="en-US-Standard-D",
                             speaking_rate=1.0, pitch=0.0,
                             credentials_path="./keys/capable-shape-452021-u9-06c66c66092c.json",
                             output_dir=None):
    """
    Convert text to speech using Google Cloud TTS API

    Args:
        text (str): The text to convert to speech
        language_code (str): Language code (e.g., 'en-US')
        voice_name (str): Name of the voice to use
        speaking_rate (float): Speed of speech (1.0 is normal)
        pitch (float): Voice pitch (-20.0 to 20.0)
        credentials_path (str): Path to Google Cloud credentials
        output_dir (str):

    Returns:
        str: Path to audio file
    """
    # Create a hash based on text and voice parameters
    content_hash = hashlib.md5(
        f"{text}_{language_code}_{voice_name}_{speaking_rate}_{pitch}".encode()
    ).hexdigest()

    if output_dir is None:
        output_dir = settings.CACHE_DIR
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"tts_{content_hash}.mp3")

    # Check if file already exists
    if os.path.exists(output_file):
        print(f"Using existing audio file: {output_file}")
        return output_file

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

    # Write the audio file
    with open(output_file, "wb") as out:
        out.write(response.audio_content)
        print(f"Audio content written to: {output_file}")

    return output_file


def generate_comment_audio(comment: Comment, language="en-US", voice="en-US-Standard-D"):
    """Generate audio for a comment using text-to-speech.

    Args:
        comment (dict): Comment data including 'text'
        language (str): language code (e.g., 'en-US')
        voice (str): voice name (e.g., 'en-US-Standard-D')

    Returns:
        tuple: (audio_clip, audio_path)
    """

    # Generate the audio file
    audio_path = generate_audio_from_text(
        text=comment.text,
        language_code=language,
        voice_name=voice,
        speaking_rate=1.0
    )

    # Create AudioFileClip
    audio_clip = AudioFileClip(audio_path)

    return audio_clip, audio_path