from fastapi import APIRouter

from app.api.dto.video_dto import LanguagesResponse, LanguageModelResponse, VoicesResponse, VoiceModel
from app.enum.voice import Gender, Language

router = APIRouter(prefix="/option", tags=["Option Operations"])


@router.get("/languages/", response_model=LanguagesResponse)
async def get_supported_languages() -> LanguagesResponse:
    """Get all supported languages for text-to-speech."""
    languages = [
        LanguageModelResponse(code=lang.value, name=lang.name)
        for lang in Language
    ]
    return LanguagesResponse(languages=languages)


@router.get("/voices/", response_model=VoicesResponse)
async def get_supported_languages() -> VoicesResponse:
    voices = [
        VoiceModel(code="en-US-Standard-B", name="Standard Male", language=Language.English, gender=Gender.FEMALE),
        VoiceModel(code="en-US-Standard-F", name="Standard Female", language=Language.English, gender=Gender.FEMALE),

        VoiceModel(code="fr-FR-Standard-B", name="Standard Male", language=Language.France, gender=Gender.FEMALE),
        VoiceModel(code="fr-FR-Standard-F", name="Standard Female", language=Language.France, gender=Gender.FEMALE),

        VoiceModel(code="vi-VN-Chirp3-HD-Orus", name="Standard Male", language=Language.Vietnamese, gender=Gender.MALE),
        VoiceModel(code="vi-VN-Chirp3-HD-Aoede", name="Standard Female", language=Language.Vietnamese, gender=Gender.FEMALE),
    ]
    return VoicesResponse(voices=voices)
