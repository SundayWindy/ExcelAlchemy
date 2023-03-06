import logging
from typing import Any

from excelalchemy.const import MULTI_CHECKBOX_SEPARATOR
from excelalchemy.types.field import FieldMetaInfo
from excelalchemy.types.identity import OptionId
from excelalchemy.types.value.multi_checkbox import MultiCheckbox
from excelalchemy.types.value.radio import Radio


class SingleStaff(Radio):
    __name__ = '人员单选'

    @classmethod
    def comment(cls, field_meta: FieldMetaInfo) -> str:
        required = '必填' if field_meta.required else '非必填'
        extra_hint = field_meta.hint or '请输入人员姓名和工号，如“张三/001”'
        return f"""必填性：{required} \n提示：{extra_hint}"""

    @classmethod
    def serialize(cls, value: Any, field_meta: FieldMetaInfo) -> Any:
        if isinstance(value, str):
            return value.strip()
        return value

    @classmethod
    def deserialize(cls, value: Any | None, field_meta: FieldMetaInfo) -> str:
        if value is None or value == '':
            return ''
        try:
            return field_meta.options_id_map[value.strip()].name
        except KeyError:
            logging.warning('类型【%s】无法为【%s】找到【%s】的选项, 返回原值', cls.__name__, field_meta.label, value)
        return value if value is not None else ''


class MultiStaff(MultiCheckbox):
    __name__ = '人员多选'

    @classmethod
    def comment(cls, field_meta: FieldMetaInfo) -> str:
        required = '必填' if field_meta.required else '非必填'
        extra_hint = field_meta.hint or '请输入人员姓名和工号，如“张三/001”'
        return f"""必填性：{required} \n提示：{extra_hint}"""

    @classmethod
    def serialize(cls, value: str | list[str] | Any, field_meta: FieldMetaInfo) -> Any:
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, list):
            return MULTI_CHECKBOX_SEPARATOR.join(str(x) for x in value)
        return value if value is not None else ''

    @classmethod
    def __validate__(cls, v: Any, field_meta: FieldMetaInfo) -> list[str]:
        return super().__validate__(v, field_meta)

    @classmethod
    def deserialize(cls, value: str | list[OptionId] | Any, field_meta: FieldMetaInfo) -> Any:
        if isinstance(value, str):
            return value

        if isinstance(value, list):
            if len(value) != len(set(value)):
                raise ValueError('选项有重复')

            option_names = field_meta.__option_ids_to_names__(value)
            return f'{MULTI_CHECKBOX_SEPARATOR}'.join(option_names)

        logging.warning('%s 反序列化失败', cls.__name__)
        return value
