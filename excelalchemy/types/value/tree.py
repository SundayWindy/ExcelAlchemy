import logging
from typing import Any

from excelalchemy.const import MULTI_CHECKBOX_SEPARATOR
from excelalchemy.types.column.field import FieldMetaInfo
from excelalchemy.types.identity import OptionId
from excelalchemy.types.value.multi_checkbox import MultiCheckbox
from excelalchemy.types.value.radio import Radio


class SingleTreeNode(Radio):
    __name__ = '树形单选'

    @classmethod
    def comment(cls, field_meta: FieldMetaInfo) -> str:
        required = '必填' if field_meta.required else '非必填'
        extra_hint = field_meta.hint or '请输入完整路径（包含根节点），层级之间用“/”连接，如“一级/二级/选项1”；多选时，选项之间用“，”连接'
        return f"""必填性：{required} \n提示：{extra_hint}"""

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
            logging.warning('无法找到树结点 %s 的选项, 返回原值', value)

        return value if value is not None else ''


class MultiTreeNode(MultiCheckbox):
    __name__ = '树形多选'

    @classmethod
    def comment(cls, field_meta: FieldMetaInfo) -> str:
        required = '必填' if field_meta.required else '非必填'
        extra_hint = field_meta.hint or '请输入完整路径（包含根节点），层级之间用“/”连接，如“一级/二级/选项1”；多选时，选项之间用“，”连接'
        return f"""必填性：{required} \n提示：{extra_hint}"""

    @classmethod
    def serialize(cls, value: Any, field_meta: FieldMetaInfo) -> Any:
        return super().serialize(value, field_meta)

    @classmethod
    def _validate(cls, v: Any, field_meta: FieldMetaInfo) -> list[str]:
        return super()._validate(v, field_meta)

    @classmethod
    def deserialize(cls, value: str | list[str] | None | Any, field_meta: FieldMetaInfo) -> str | Any:
        if value is None or value == '':
            return ''
        if isinstance(value, str):
            return value

        if isinstance(value, list):
            if len(value) != len(set(value)):
                raise ValueError('选项有重复')
            rst: list[str] = []
            for id_ in value:
                id_ = OptionId(id_)
                try:
                    rst.append(field_meta.options_id_map[id_].name)
                except KeyError:
                    logging.warning('无法找到树结点 %s 的选项, 返回原值', id_)
                    rst.append(id_)
            # pyright: reportUnknownArgumentType=false
            return f'{MULTI_CHECKBOX_SEPARATOR}'.join(rst)

        logging.warning('%s 反序列化失败', cls.__name__)
        return value
