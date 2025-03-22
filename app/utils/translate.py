import os
from typing import List
from logging import getLogger
import html
# Import the Comment class from your models
from app.api.dto.video_dto import Comment
# Set up logger
logger = getLogger(__name__)

from google.cloud import translate_v2 as translate

def translate_comments(comments: List[Comment],
                       target_language: str,
                       credentials_path="./keys/capable-shape-452021-u9-06c66c66092c.json") -> List[Comment]:
    """
    Translate comments from English to target language

    Args:
        comments: List of Comment objects
        target_language: Target language code (e.g. 'fr-FR', 'vi-VN')
        credentials_path: Credentials file path for Google Cloud Translation API

    Returns:
        List of Comment objects with translated text
    """

    if target_language.startswith("en-"):
        # No translation needed for English
        return comments

    try:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

        # Extract just the language code (e.g. 'fr' from 'fr-FR')
        target_lang_code = target_language.split('-')[0]

        # Initialize the client
        translate_client = translate.Client()

        # Get all texts that need translation
        texts_to_translate = [comment.text for comment in comments]

        # Batch translate all texts
        translations = translate_client.translate(
            texts_to_translate,
            target_language=target_lang_code,
            source_language='en'
        )

        # Update comments with translated text
        translated_comments = []
        for comment, translation in zip(comments, translations):
            # Create a copy of the comment with translated text
            translated_comment = Comment(
                username=comment.username,
                text=html.unescape(translation['translatedText']),
                start_time=comment.start_time,
                duration=comment.duration,
                avatar=comment.avatar
            )
            # Copy any additional attributes
            if hasattr(comment, 'is_title'):
                translated_comment.is_title = comment.is_title

            translated_comments.append(translated_comment)

        return translated_comments

    except Exception as e:
        logger.error(f"Translation failed: {str(e)}", exc_info=True)
        # Return original comments if translation fails
        return comments


def translate_text(text: str,
                   target_language: str,
                   credentials_path="./keys/capable-shape-452021-u9-06c66c66092c.json") -> str:
    """
    Translate a single text from English to target language

    Args:
        text: Text to translate
        target_language: Target language code (e.g. 'fr-FR', 'vi-VN')
        credentials_path: Credentials file path for Google Cloud Translation API

    Returns:
        Translated text
    """

    if target_language.startswith("en-"):
        # No translation needed for English
        return text

    try:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

        # Extract just the language code (e.g. 'fr' from 'fr-FR')
        target_lang_code = target_language.split('-')[0]

        # Initialize the client
        translate_client = translate.Client()

        # Translate the text
        translation = translate_client.translate(
            text,
            target_language=target_lang_code,
            source_language='en'
        )

        # Decode HTML entities in the translated text
        translated_text = html.unescape(translation['translatedText'])

        return translated_text

    except Exception as e:
        logger.error(f"Translation failed: {str(e)}", exc_info=True)
        # Return original text if translation fails
        return text