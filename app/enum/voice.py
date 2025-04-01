from enum import Enum


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class Language(str, Enum):
    English = "en-US"
    France = "fr-FR"
    Vietnamese = "vi-VN"
