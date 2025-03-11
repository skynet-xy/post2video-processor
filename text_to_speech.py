import os
import json
import re
from google.cloud import texttospeech


def generate_audio_from_text(text, output_file="output.mp3",
                             language_code="en-US", voice_name="en-US-Standard-D",
                             speaking_rate=1.0, pitch=0.0,
                             credentials_path="./keys/capable-shape-452021-u9-06c66c66092c.json"):
    """
    Convert text to speech using Google Cloud TTS API and generate timestamp transcript

    Args:
        text (str): The text to convert to speech
        output_file (str): Path to save the audio file
        language_code (str): Language code (e.g., 'en-US')
        voice_name (str): Name of the voice to use
        speaking_rate (float): Speed of speech (1.0 is normal)
        pitch (float): Voice pitch (-20.0 to 20.0)
        credentials_path (str): Path to Google Cloud credentials

    Returns:
        tuple: (path to audio file, transcript with timestamps)
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

    # Generate transcript with timestamps
    transcript = generate_transcript(text, speaking_rate)

    # Save transcript
    transcript_file = os.path.splitext(output_file)[0] + "_transcript.json"
    with open(transcript_file, "w") as f:
        json.dump(transcript, f, indent=2)

    print(f"Transcript written to: {transcript_file}")

    return output_file, transcript


def generate_transcript(text, speaking_rate=1.0):
    """
    Generate timestamps for each sentence in the text

    Args:
        text (str): The input text
        speaking_rate (float): Speaking rate used for generation

    Returns:
        list: List of dictionaries with sentence and timestamp
    """
    # Split text into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    transcript = []
    current_time = 0.0

    for sentence in sentences:
        # Estimate duration based on character count and speaking rate
        # Approximately 15 characters per second for normal speech
        char_per_second = 15 * speaking_rate
        duration = len(sentence) / char_per_second

        # Add some padding between sentences
        duration += 0.5

        transcript.append({
            "text": sentence,
            "start_time": round(current_time, 2),
            "end_time": round(current_time + duration, 2)
        })

        current_time += duration

    return transcript


def save_transcript_as_srt(transcript, output_file):
    """Save transcript in SubRip (SRT) format"""
    with open(output_file, "w") as f:
        for i, entry in enumerate(transcript, 1):
            start = format_srt_time(entry["start_time"])
            end = format_srt_time(entry["end_time"])

            f.write(f"{i}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"{entry['text']}\n\n")

    print(f"SRT file written to: {output_file}")


def format_srt_time(seconds):
    """Convert seconds to SRT time format (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds - int(seconds)) * 1000)

    return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}"


if __name__ == "__main__":
    # Example usage
    text = [
        "This video is hilarious! I can't stop watching it over and over again.",
        "I think this deserves to go viral! So clever and well made.",
        "The way you edited this is amazing. What software did you use?",
        "Incredible! This is one of the best videos I've seen in a while.",
        "Wow, the editing here is on another level. Great job!",
        "Such a beautiful video. The scenes and music are perfect together.",
        "The soundtrack you chose fits perfectly with the visuals. Love it!",
        "This video makes me want to go on an adventure! So inspiring.",
        "I can't believe how good this video is. The food shots are mouth-watering.",
        "This is the motivation I needed today. Keep up the great work!",
    ]

    # Generate speech with transcript
    output_file, transcript = generate_audio_from_text(
        text=" ".join(text),
        output_file="output/speech.mp3"
    )

    # Save transcript in SRT format (for subtitles)
    srt_file = os.path.splitext(output_file)[0] + ".srt"
    save_transcript_as_srt(transcript, srt_file)
