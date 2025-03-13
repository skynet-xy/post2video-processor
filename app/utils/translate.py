import os

from google.cloud import translate_v2 as translate

# Path to your key file
key_path = os.path.join("../../keys", "capable-shape-452021-u9-06c66c66092c.json")

# Set environment variable to point to your credentials file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path

def translate_text(text, target_language="en"):
    """Translates text into the target language.

    Args:
        text: The text to translate.
        target_language: The target language code (e.g., 'en' for English, 'es' for Spanish).

    Returns:
        The translated text.
    """
    # Initialize the client
    translate_client = translate.Client()

    # Translate text
    result = translate_client.translate(text, target_language=target_language)

    return result

def main():
    # Example usage
    text_to_translate = "Hello, world!"
    target_language = "es"  # Spanish

    print(f"Original text: {text_to_translate}")
    print(f"Translating to: {target_language}")

    result = translate_text(text_to_translate, target_language)

    print(f"Translated text: {result['translatedText']}")
    print(f"Source language: {result['detectedSourceLanguage']}")

if __name__ == "__main__":
    main()