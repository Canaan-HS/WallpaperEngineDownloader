from ..bootstrap import os, ctypes, locale, logging, SysPlat

from .en_US import en_US
from .zh_TW import zh_TW
from .zh_CN import zh_CN

Default = "en_US"
Words = {"en_US": en_US, "zh_TW": zh_TW, "zh_CN": zh_CN}
Locale = {
    "950": "zh_TW",
    "936": "zh_CN",
    "1252": "en_US",
}


def _detect_system_language(lang) -> str:
    """檢測系統語言"""

    try:
        if SysPlat == "Windows":
            buffer = ctypes.create_unicode_buffer(85)
            ctypes.windll.kernel32.GetUserDefaultLocaleName(buffer, len(buffer))
            lang = buffer.value.replace("-", "_")
        elif SysPlat in ("Linux", "Darwin"):
            lang = os.environ.get("LANG", "").split(".")[0]
        else:
            locale.setlocale(locale.LC_ALL, "")
            lang = locale.getlocale()[1].replace("cp", "")
    except Exception as e:
        logging.info(e)
        lang = Default

    return lang


def translator(lang=None):
    """獲取翻譯器"""

    Transl = {}
    SetLang = ""

    lang = _detect_system_language(lang) if lang is None else lang

    if isinstance(lang, str) and lang in Words:
        Transl, SetLang = Words.get(lang), lang
    elif lang in Locale:
        Transl, SetLang = Words.get(Locale.get(lang)), Locale.get(lang)
    else:
        Transl, SetLang = Words.get(Default), Default

    return (lambda text: Transl.get(text, text), SetLang)
