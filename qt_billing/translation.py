from modeltranslation.translator import TranslationOptions, translator

from .models import UniqueSellingPoint


class UniqueSellingPointTranslationOptions(TranslationOptions):
    fields = ("description",)


translator.register(UniqueSellingPoint, UniqueSellingPointTranslationOptions)
