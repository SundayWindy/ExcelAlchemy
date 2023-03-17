from typing import Any

from excelalchemy.const import CharacterSet
from excelalchemy.exc import ProgrammaticError
from excelalchemy.types.abstract import ABCValueType
from excelalchemy.types.field import FieldMetaInfo

SPECIAL_SYMBOLS = set('!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~"。？！，、；：‘’“”（）《》〈〉【】〔〕｛｝｟｠〖〗〘〙〚〛〜〝〞〟〰–—‘‛“”„‟…‧﹏.')


def _is_chinese_character(character: str) -> bool:
    # https://www.unicode.org/versions/Unicode15.0.0/ch18.pdf
    #
    # Table 18-1. Blocks Containing Han Ideographs
    # # Block Range Comment
    # CJK Unified Ideographs 4E00–9FFF Common
    # CJK Unified Ideographs Extension A 3400–4DBF Rare
    # CJK Unified Ideographs Extension B 20000–2A6DF Rare, historic
    # CJK Unified Ideographs Extension C 2A700–2B73F Rare, historic
    # CJK Unified Ideographs Extension D 2B740–2B81F Uncommon, some in current use
    # CJK Unified Ideographs Extension E 2B820–2CEAF Rare, historic
    # CJK Unified Ideographs Extension F 2CEB0–2EBEF Rare, historic
    # CJK Unified Ideographs Extension G 30000–3134F Rare, historic
    # CJK Unified Ideographs Extension H 31350–323AF Rare, historic
    # CJK Compatibility Ideographs F900–FAFF Duplicates, unifiable variants, corporate characters
    # CJK Compatibility Ideographs Supplement 2F800–2FA1F Unifiable variant
    code_point = ord(character)
    return (
        (0x4E00 <= code_point <= 0x9FFF)
        or (0x3400 <= code_point <= 0x4DBF)
        or (0x20000 <= code_point <= 0x2A6DF)
        or (0x2A700 <= code_point <= 0x2B73F)
        or (0x2B740 <= code_point <= 0x2B81F)
        or (0x2B820 <= code_point <= 0x2CEAF)
        or (0x2CEB0 <= code_point <= 0x2EBEF)
        or (0x30000 <= code_point <= 0x3134F)
        or (0x31350 <= code_point <= 0x323AF)
        or (0xF900 <= code_point <= 0xFAFF)
        or (0x2F800 <= code_point <= 0x2FA1F)
    )


def _is_number_character(character: str) -> bool:
    return ord(character) in range(ord('0'), ord('9') + 1)


def _is_lowercase_letters(character: str) -> bool:
    return ord(character) in range(ord('a'), ord('z') + 1)


def _is_uppercase_letters(character: str) -> bool:
    return ord(character) in range(ord('A'), ord('Z') + 1)


def _is_special_symbols(character: str) -> bool:
    return character in SPECIAL_SYMBOLS


_CHARACTER_SET_TO_VALIDATOR = {
    CharacterSet.CHINESE: _is_chinese_character,
    CharacterSet.NUMBER: _is_number_character,
    CharacterSet.LOWERCASE_LETTERS: _is_lowercase_letters,
    CharacterSet.UPPERCASE_LETTERS: _is_uppercase_letters,
    CharacterSet.SPECIAL_SYMBOLS: _is_special_symbols,
}

_CHARACTER_SET_TO_NAME = {
    CharacterSet.CHINESE: '中文字符',
    CharacterSet.NUMBER: '数字',
    CharacterSet.LOWERCASE_LETTERS: '小写字母',
    CharacterSet.UPPERCASE_LETTERS: '大写字母',
    CharacterSet.SPECIAL_SYMBOLS: '特殊符号',
}


def _format_character_set_names(cs: set[CharacterSet]) -> str:
    return '、'.join(_CHARACTER_SET_TO_NAME[c] for c in cs)


class String(str, ABCValueType):
    @classmethod
    def comment(cls, field_meta: FieldMetaInfo) -> str:
        return '\n'.join(
            [
                field_meta.comment_unique,
                field_meta.comment_required,
                field_meta.comment_max_length,
                '可输入内容:中文、数字、大写字母、小写字母、符号',
                field_meta.comment_hint,
            ]
        )

    @classmethod
    def serialize(cls, value: Any, field_meta: FieldMetaInfo) -> str:
        return str(value).strip()

    @classmethod
    def deserialize(cls, value: str | None | Any, field_meta: FieldMetaInfo) -> str:
        return str(value).strip() if value is not None else ''

    # mccabe-complexity: 12
    @classmethod
    def __validate__(cls, value: str, field_meta: FieldMetaInfo) -> str:
        parsed = str(value)
        errors: list[str] = []

        if field_meta.importer_max_length is not None:
            if len(parsed) > field_meta.importer_max_length:
                errors.append(f'最长为{field_meta.importer_max_length}个字')

        errors.extend(cls.__check_character_set__(parsed, field_meta))

        if errors:
            raise ValueError(*errors)
        else:
            return parsed

    @classmethod
    def __check_character_set__(cls, value: str, field_meta: FieldMetaInfo) -> list[str]:
        errors: list[str] = []
        if field_meta.character_set is None:
            raise ProgrammaticError('character_set 未设置')

        for single_character in value:
            if not any(_CHARACTER_SET_TO_VALIDATOR[cs](single_character) for cs in field_meta.character_set):
                errors.append(f'仅允许输入{_format_character_set_names(field_meta.character_set)}')
                break

        return errors
