import logging
from typing import Any

from excelalchemy.const import MULTI_CHECKBOX_SEPARATOR
from excelalchemy.exc import ProgrammaticError
from excelalchemy.types.abstract import ABCValueType
from excelalchemy.types.field import FieldMetaInfo
from excelalchemy.types.identity import OptionId


class Radio(ABCValueType, str):
    __name__ = '单选框组'

    @classmethod
    def comment(cls, field_meta: FieldMetaInfo) -> str:
        required = '必填' if field_meta.required else '非必填'
        options = f'{MULTI_CHECKBOX_SEPARATOR}'.join([x.name for x in (field_meta.options or [])])
        is_multi = '单选'
        if not options:
            logging.error('%s 类型的字段 %s 必须设置 options', cls.__name__, field_meta.label)
        extra_hint = f'\n提示：{field_meta.hint}' if field_meta.hint else ''
        return f"""必填性：{required}
                选项：{options}
                单/多选：{is_multi}{extra_hint}"""

    @classmethod
    def serialize(cls, value: Any, field_meta: FieldMetaInfo) -> str:
        return str(value).strip()

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

    @classmethod
    def __validate__(cls, v: str, field_meta: FieldMetaInfo) -> OptionId | str:  # return Option.id
        if MULTI_CHECKBOX_SEPARATOR in v:
            raise ValueError('多选不支持')

        parsed = v.strip()

        if field_meta.options is None:
            raise ProgrammaticError('当验证【RADIO / MULTI_CHECKBOX / SELECT】类型字段时，选项不得为空！')

        if not field_meta.options:  # empty
            logging.warning(f'{cls.__name__}类型字段"{field_meta.label}"的选项为空，将返回原值')
            return parsed

        if parsed in field_meta.options_id_map:
            return parsed

        if parsed not in field_meta.options_name_map:
            raise ValueError('选项不存在，请参照字段注释填写')

        return field_meta.options_name_map[parsed].id
