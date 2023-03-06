import logging
from typing import TYPE_CHECKING
from typing import Any

from excelalchemy.types.abstract import ABCValueType
from excelalchemy.types.field import FieldMetaInfo
from excelalchemy.types.value import excel_choice


@excel_choice
class Boolean(ABCValueType):
    __name__ = '布尔'

    @classmethod
    def comment(cls, field_meta: FieldMetaInfo) -> str:
        required = '必填' if field_meta.required else '选填'

        if field_meta.hint:
            extra_hint = f'提示: {field_meta.hint}'
        else:
            extra_hint = ''

        comment = f'必填性: {required}\n可选值: 是、否'

        if extra_hint:
            comment += f'\n{extra_hint}'

        return comment

    @classmethod
    def serialize(cls, value: Any, field_meta: FieldMetaInfo) -> str:
        return str(value).strip()

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

    @classmethod
    def __validate__(cls, value: str | bool | Any, field_meta: FieldMetaInfo) -> bool:
        if isinstance(value, bool):
            return value

        try:
            value_str = str(value)
        except Exception as error:
            raise ValueError('请输入“是”或“否”') from error

        if value_str not in ('是', '否'):
            raise ValueError('请输入“是”或“否”')

        return value_str == '是'


if TYPE_CHECKING:
    # pyright: reportGeneralTypeIssues=false
    Boolean = bool  # type: ignore
