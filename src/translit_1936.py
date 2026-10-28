#!/usr/bin/env python3
"""Транслитерация латиницы Жиркова (Аварско-русский словарь, 1936) в
аварскую кириллицу.

Источник — OCR с шумным распознаванием: один и тот же звук печатался
разными диакритическими знаками (напр. тӀ — это ṭ, ţ, ț, Ṭ, ṯ вперемешку).
Таблица ниже утверждена сверкой с носителем (см. CHANGELOG/коммит) и
покрывает все варианты, встреченные в data/av-ru.1936.jsonl на момент
написания. Применяется только к аварским полям (word/forms/examples.av/
see_also.target) — русский перевод (results[].translation) не трогаем.
"""
from __future__ import annotations

# Длинные (многосимвольные) цели сортируются по длине ключа при матчинге —
# порядок в словаре не важен, см. _sorted_keys().
MAPPING: dict[str, str] = {
    # Однозначные буквы без диакритики
    "a": "а", "b": "б", "d": "д", "e": "е", "f": "ф", "g": "г",
    "i": "и", "j": "й", "k": "к", "l": "л", "m": "м", "n": "н",
    "o": "о", "p": "п", "r": "р", "s": "с", "t": "т", "u": "у",
    "v": "в", "z": "з",
    "c": "ч", "h": "гь", "q": "къ", "x": "х",
    # тӀ — все варианты OCR одного и того же ejective t
    "ṭ": "тӀ", "ţ": "тӀ", "ț": "тӀ", "Ṭ": "тӀ", "ṯ": "тӀ",
    # кӀ — ejective k
    "ḳ": "кӀ", "ķ": "кӀ", "ƙ": "кӀ", "ⱪ": "кӀ",
    # хӀ / гӀ — два разных звука, легко путаются в OCR
    "ħ": "хӀ",
    "ḥ": "гӀ", "Ḥ": "гӀ", "ḩ": "гӀ",
    # ш
    "ş": "ш", "Ş": "ш",
    # чӀ
    "ç": "чӀ", "Ç": "чӀ",
    # лъ (ɫ/ḷ/ļ/ɭ — старые OCR-варианты, уже заменены sources на ł/ļ; оставлены
    # для совместимости со старыми кэшами/партиями jsonl)
    "ɫ": "лъ", "ł": "лъ", "ɬ": "лъ",
    "ḷ": "лъ", "ļ": "лъ", "ɭ": "лъ",
    # хъ
    "χ": "хъ",
    # гъ — ơ старый OCR-вариант, ƣ новый канонический (sources, 2026-10-28)
    "ơ": "гъ", "ƣ": "гъ",
    # щ — ṣ старый OCR-вариант; ꞩ (s со штрихом) — новый канонический для ц!
    "ṣ": "щ",
    "ꞩ": "ц",
    # ж — ẓ старый OCR-вариант; ƶ (z со штрихом) — новый канонический
    "ẓ": "ж", "ƶ": "ж",
    # цӀ — ⱬ (z с нижним росчерком) — новый канонический (sources, 2026-10-28)
    "ⱬ": "цӀ",
    # кь — ꝗ (q с перекладиной) — новый канонический, отдельная буква алфавита
    "ꝗ": "кь",
    # и (ещё один вариант начертания)
    "ı": "и",
    # ъ (апостроф у Жиркова)
    "'": "ъ",
    "’": "ъ",  # правая одинарная кавычка — тоже апостроф в OCR

    # --- OCR иногда не склеивал диакритик с буквой (base + отдельный
    # combining mark, 2 кодпойнта вместо одного precomposed символа).
    # Любой диакритик на этой базовой букве — тот же звук, что и у уже
    # решённых precomposed вариантов (см. выше), независимо от конкретного
    # знака: OCR путал точку/запятую/седиль/огонек друг с другом чаще, чем
    # путал сам звук.
    "ṭ": "тӀ", "ṫ": "тӀ", "ţ": "тӀ", "ț": "тӀ", "t̨": "тӀ",
    "ḳ": "кӀ", "k̇": "кӀ", "ķ": "кӀ", "k̦": "кӀ", "k̨": "кӀ",
    "x̧": "хь", "x̨": "хь", "x̦": "хь",  # x+седиль/огонэк/запятая снизу -> хь, не хъ
    "x̌": "хъ", "x̄": "хъ", "ẋ": "хъ", "x̣": "хъ", "x̵": "хъ",
    "z̧": "ж", "z̨": "ж", "ż": "ж", "z̉": "ж",
    "z̄": "ж", "ẓ": "ж", "z̦": "ж",
    "c̣": "чӀ", "c̨": "чӀ", "ç": "чӀ",
    "ç̧": "чӀ", "ç̇": "чӀ",
    "ṣ": "щ", "ş": "щ", "s̨": "щ",
    "ḥ": "гӀ", "ḩ": "гӀ",
    "ḷ": "лъ", "l̦": "лъ",
    "q̇": "къ", "q́": "къ",
    "ź": "з",  # редкий остаточный акут на z — не ударение, просто з

    # Единичные редкие precomposed-варианты (OCR-мусор), встреченные 1-2
    # раза — см. my_alphabet.csv (ⱨ — вариант гӀ) и визуальное сходство.
    "ⱨ": "гӀ", "ⱼ": "й",

    # Safety net: любой combining mark, не покрытый явной парой выше
    # (редкий OCR-мусор на непредусмотренной букве) — вырезаем, а не
    # протаскиваем в вывод как «подвисшую» диакритику.
    "̣": "", "̇": "", "̧": "", "̦": "", "̨": "",
    "̌": "", "̃": "", "̄": "", "̉": "", "́": "",
    "̂": "", "̵": "",
}

_sorted_keys: list[str] | None = None


def _keys() -> list[str]:
    global _sorted_keys
    if _sorted_keys is None:
        _sorted_keys = sorted(MAPPING.keys(), key=len, reverse=True)
    return _sorted_keys


def translit_word(text: str) -> str:
    """Побуквенная (greedy longest-match) транслитерация одного слова/формы.

    Регистр: входное слово приводится к нижнему, первая буква результата
    делается заглавной, если было заглавным первое исходное (имена
    собственные у Жиркова пишутся с одной заглавной буквы).
    """
    if not text:
        return text
    capitalize = text[:1].isupper()
    lower = text.lower()
    keys = _keys()
    out: list[str] = []
    i = 0
    n = len(lower)
    while i < n:
        matched = False
        for key in keys:
            if lower.startswith(key, i):
                out.append(MAPPING[key])
                i += len(key)
                matched = True
                break
        if not matched:
            out.append(lower[i])
            i += 1
    result = "".join(out)
    if capitalize and result:
        result = result[0].upper() + result[1:]
    return result


def has_untranslated_latin(text: str) -> bool:
    """True, если после транслитерации в слове остались латинские буквы —
    значит в MAPPING не хватает какого-то символа."""
    return any("a" <= ch.lower() <= "z" for ch in text)


def transliterate_entry(raw: dict) -> dict:
    """Транслитерирует аварские (латинские) поля одной строки
    av-ru.1936.jsonl; русский перевод не трогает."""
    raw = dict(raw)
    if raw.get("word"):
        raw["word"] = translit_word(raw["word"])
    if raw.get("forms"):
        raw["forms"] = [translit_word(f) for f in raw["forms"]]
    senses = raw.get("senses")
    if senses:
        new_senses = []
        for sense in senses:
            if not isinstance(sense, dict):
                new_senses.append(sense)
                continue
            sense = dict(sense)
            if sense.get("forms"):
                sense["forms"] = [translit_word(f) for f in sense["forms"]]
            examples = sense.get("examples")
            if examples:
                new_examples = []
                for ex in examples:
                    ex = dict(ex)
                    if ex.get("av"):
                        ex["av"] = translit_word(ex["av"])
                    new_examples.append(ex)
                sense["examples"] = new_examples
            new_senses.append(sense)
        raw["senses"] = new_senses
    see_also = raw.get("see_also")
    if see_also:
        new_see = []
        for item in see_also:
            if isinstance(item, dict) and item.get("target"):
                item = dict(item)
                item["target"] = translit_word(item["target"])
            new_see.append(item)
        raw["see_also"] = new_see
    return raw
