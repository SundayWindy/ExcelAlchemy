import logging
from typing import Any

from excelalchemy.const import MULTI_CHECKBOX_SEPARATOR
from excelalchemy.types.field import FieldMetaInfo
from excelalchemy.types.identity import OptionId
from excelalchemy.types.value.multi_checkbox import MultiCheckbox
from excelalchemy.types.value.radio import Radio


class SingleOrganization(Radio):
    __name__ = '组织单选'

    @classmethod
    def comment(cls, field_meta: FieldMetaInfo) -> str:
        required_str = '必填' if field_meta.required else '非必填'
        extra_hint = field_meta.hint or "需按照组织架构树填写组织完整路径，例如 'XX公司/一级部门/二级部门'."
        return f"""必填性：{required_str}\n提示：{extra_hint}"""

    @classmethod
    def serialize(cls, value: Any, field_meta: FieldMetaInfo) -> Any:
        if isinstance(value, str):
            return value.strip()
        return value

    @classmethod
    def deserialize(cls, value: Any, field_meta: FieldMetaInfo) -> Any:
        try:
            return field_meta.options_id_map[value.strip()].name
        except KeyError:
            logging.warning('无法找到组织 %s 的选项, 返回原值', value)

        return value if value is not None else ''


class MultiOrganization(MultiCheckbox):
    __name__ = '组织多选'

    @classmethod
    def comment(cls, field_meta: FieldMetaInfo) -> str:
        required = '必填' if field_meta.required else '非必填'
        extra_hint = field_meta.hint or '需按照组织架构树填写组织完整路径，如“XX公司/一级部门/二级部门”，多选时，选项之间用“、”连接'
        return f"""必填性：{required} \n提示：{extra_hint}"""

    @classmethod
    def serialize(cls, value: Any, field_meta: FieldMetaInfo) -> Any:
        return super().serialize(value, field_meta)

    @classmethod
    def deserialize(cls, value: str | list[str] | None | Any, field_meta: FieldMetaInfo) -> str | Any:
        if value is None or value == '':
            return ''

        if isinstance(value, str):
            return value

        if isinstance(value, list):
            option_names = cls.__option_ids_to_names__(value, field_meta)
            return MULTI_CHECKBOX_SEPARATOR.join(map(str, option_names))

        logging.warning('%s 反序列化失败', cls.__name__)
        return value

    @staticmethod
    def __option_ids_to_names__(option_ids: list[str], field_meta: FieldMetaInfo) -> list[str]:
        option_names: list[str] = []
        for option_id in option_ids:
            option_id = OptionId(option_id)
            try:
                option_names.append(field_meta.options_id_map[option_id].name)
            except KeyError:
                logging.warning('无法找到组织 %s 的选项, 返回原值', option_id)
                option_names.append(option_id)
        return option_names

    @classmethod
    def __validate__(cls, value: Any, field_meta: FieldMetaInfo) -> list[str]:
        return super().__validate__(value, field_meta)
