import logging
from typing import TYPE_CHECKING
from typing import Any

from excelalchemy.model.abstract import ABCValueType
from excelalchemy.model.abstract import FieldMetaInfo
from excelalchemy.model.value_type import excel_choice


@excel_choice
class Boolean(ABCValueType):

    __name__ = '布尔'

    @classmethod
    def comment(cls, field_meta: FieldMetaInfo) -> str:
        required = '必填' if field_meta.required else '选填'
        extra_hint = field_meta.hint
        return f'必填性: {required}\n可选值: 是、否' + (f'\n提示: {extra_hint}' if extra_hint else '')

    @classmethod
    def serialize(cls, value: Any, field_meta: FieldMetaInfo) -> str:
        return str(value).strip()

    @classmethod
    def _validate(cls, v: str | bool | Any, field_meta: FieldMetaInfo) -> bool:
        if isinstance(v, bool):
            return v

        try:
            parsed = str(v)
        except Exception as exc:
            raise ValueError('请输入“是”或“否”') from exc

        if parsed not in ('是', '否'):
            raise ValueError('请输入“是”或“否”')
        else:
            return parsed == '是'

    @classmethod
    def deserialize(cls, value: bool | str | None | Any, field_meta: FieldMetaInfo) -> str:
        if value is None or value == '':
            return '否'  # 产品要求，空值默认为否
        if isinstance(value, bool):
            return '是' if value else '否'

        elif isinstance(value, str):
            value = value.strip()
            if value not in ('是', '否'):
                logging.warning('无法识别布尔值 %s, 返回原值', value)
                return value
            return value
        else:
            logging.warning('类型【%s】无法为 %s 反序列化: %s, 返回默认值 "否" ', cls.__name__, field_meta.label, value)

        return '是' if str(value) == '是' else '否'


if TYPE_CHECKING:
    # pyright: reportGeneralTypeIssues=false
    Boolean = bool  # type: ignore
