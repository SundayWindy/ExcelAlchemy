import logging
from typing import Any

from excelalchemy.const import MULTI_CHECKBOX_SEPARATOR
from excelalchemy.exc import ProgrammaticError
from excelalchemy.types.abstract import ABCValueType
from excelalchemy.types.column.field import FieldMetaInfo
from excelalchemy.types.identity import OptionId


class Radio(ABCValueType, str):
    __name__ = '单选框组'

    @classmethod
    def comment(cls, field_meta: FieldMetaInfo) -> str:
        required = '必填' if field_meta.required else '非必填'
        options = f'{MULTI_CHECKBOX_SEPARATOR}'.join([x.name for x in (field_meta.options or [])])
        is_multi = '单选'
        if not options:
            logging.error('Radio 类型的字段 %s 必须设置 options', field_meta.label)
        extra_hint = field_meta.hint
        return f"""必填性：{required}\n选项：{options}\n单/多选：{is_multi}""" + (f'\n提示：{extra_hint}' if extra_hint else '')

    @classmethod
    def serialize(cls, value: Any, field_meta: FieldMetaInfo) -> str:
        return str(value).strip()

    @classmethod
    def _validate(cls, v: str, field_meta: FieldMetaInfo) -> OptionId | str:  # return Option.id
        if MULTI_CHECKBOX_SEPARATOR in v:
            raise ValueError('不允许多选')

        errors: list[str] = []
        parsed = v.strip()

        if field_meta.options is None:
            raise ProgrammaticError('options cannot be None when validate RADIO, MULTI_CHECKBOX and SELECT')

        if not field_meta.options:  # empty
            logging.warning('类型【%s】的字段【%s】的选项为空, 将返回原值', cls.__name__, field_meta.label)
            return parsed

        if parsed in field_meta.options_id_map:
            return parsed

        if parsed not in field_meta.options_name_map:
            errors.append('选项不存在，请参照表头的注释填写')

        if errors:
            raise ValueError(*errors)
        else:
            return field_meta.options_name_map[parsed].id

    @classmethod
    def deserialize(cls, value: Any | None, field_meta: FieldMetaInfo) -> str:
        if value is None or value == '':
            return ''

        try:
            return field_meta.options_id_map[value.strip()].name
        except Exception as exc:
            logging.warning(
                '类型【%s】无法为【%s】找到【%s】的选项, 返回原值, 原因 %s',
                cls.__name__,
                field_meta.label,
                value,
                exc,
            )
        return value if value is not None else ''
