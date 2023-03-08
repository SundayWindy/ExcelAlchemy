import logging
from typing import Any

from excelalchemy.const import MULTI_CHECKBOX_SEPARATOR
from excelalchemy.exc import ProgrammaticError
from excelalchemy.types.abstract import ABCValueType
from excelalchemy.types.field import FieldMetaInfo
from excelalchemy.types.identity import OptionId


class MultiCheckbox(ABCValueType, list[str]):
    __name__ = '复选框组'

    @classmethod
    def comment(cls, field_meta: FieldMetaInfo) -> str:
        # Determine whether the field is required or optional
        required_str = '必填' if field_meta.required else '非必填'

        # Join available options into a string with the separator MULTI_CHECKBOX_SEPARATOR
        options = MULTI_CHECKBOX_SEPARATOR.join(x.name for x in (field_meta.options or []))

        # Set 'is_multi' to always be '多选'
        is_multi = '多选'

        # Add a hint message and the multi-select separator if the field is multi-select
        hint = (field_meta.hint or '') + (
            f'多选时，请用“{MULTI_CHECKBOX_SEPARATOR}”连接多个选项，如“选项1，选项2”' if field_meta.options else ''
        )

        # Combine the four pieces of information into a formatted string
        comment = f"""必填性：{required_str}\n选项：{options}\n单/多选：{is_multi}\n提示：{hint}"""

        return comment

    @classmethod
    def serialize(cls, value: str | Any, field_meta: FieldMetaInfo) -> list[str] | str:
        # If the value is a list, convert all items to strings and strip whitespace
        if isinstance(value, list):
            return [str(item).strip() for item in value]

        # If the value is a string, split it into a list using MULTI_CHECKBOX_SEPARATOR and strip whitespace
        if isinstance(value, str):
            return [item.strip() for item in value.split(MULTI_CHECKBOX_SEPARATOR)]

        # If the value is of an unsupported type, log a warning and return the original value
        logging.warning('ValueType 类型 <%s> 无法解析 Excel 输入, 返回原值:%s', cls.__name__, value)
        return value

    @classmethod
    def __validate__(cls, value: list[str] | Any, field_meta: FieldMetaInfo) -> list[str]:  # OptionId
        if not isinstance(value, list):
            raise ValueError('选项不存在，请参照表头的注释填写')

        if field_meta.options is None:
            raise ProgrammaticError('options cannot be None when validate RADIO, MULTI_CHECKBOX and SELECT')

        if not field_meta.options:  # empty
            logging.warning('类型【%s】的字段【%s】的选项为空, 将返回原值', cls.__name__, field_meta.label)
            return value

        if len(value) != len(set(value)):
            raise ValueError('选项有重复')

        errors: list[str] = []
        result: list[str] = []
        for name in value:
            option = field_meta.options_name_map.get(name)
            if option is None:
                errors.append('选项不存在，请参照表头的注释填写')
            else:
                result.append(option.id)

        if errors:
            raise ValueError(*errors)
        else:
            return result

    @classmethod
    def deserialize(cls, value: str | list[OptionId] | None | Any, field_meta: FieldMetaInfo) -> Any:
        match value:
            case None | '':
                return ''
            case str():
                return value
            case list():
                option_names = field_meta.exchange_option_ids_to_names(value)
                return f'{MULTI_CHECKBOX_SEPARATOR}'.join(option_names)

        logging.warning('%s 反序列化失败', cls.__name__)
        return value if value is not None else ''
