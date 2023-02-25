from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Any
from typing import Iterable

from pydantic import BaseModel
from pydantic import Field
from pydantic.fields import FieldInfo
from pydantic.fields import ModelField

from excelalchemy.types.identity import Key
from excelalchemy.types.identity import Label

if TYPE_CHECKING:
    from excelalchemy.types.column.field import FieldMetaInfo
else:
    FieldMetaInfo = Any


class ABCValueType(ABC):
    """
    raw_data --> serialize --> _validate
    raw_data--> deserialize
    """

    @classmethod
    @abstractmethod
    def comment(cls, field_meta: 'FieldMetaInfo') -> str:
        """用于渲染 Excel 表头的注释"""

    @classmethod
    @abstractmethod
    def serialize(cls, value: Any, field_meta: 'FieldMetaInfo') -> Any:  # value is always not None
        """用于把用户填入 Excel 的数据，转换成后端代码入口可接收的数据
        如果转换失败，返回原值，用户后续捕获更准确的错误
        """

    @classmethod
    @abstractmethod
    def _validate(cls, v: Any, field_meta: 'FieldMetaInfo') -> Any:
        """验证用户输入的值是否符合约束. 接收 serialize 后的值"""

    @classmethod
    @abstractmethod
    def deserialize(cls, value: Any, field_meta: 'FieldMetaInfo') -> Any:
        """用于把 pandas 读取的 Excel 之后的数据，转回用户可识别的数据, 处理聚合之前的数据"""

    @classmethod
    def _wrapped_validate(cls, v: Any, field: ModelField) -> Any:
        return cls._validate(v, field.field_info)

    @classmethod
    def __get_validators__(cls) -> Iterable[Any]:
        yield cls._wrapped_validate


class ComplexABCValueType(ABCValueType, dict):  # pyright: reportMissingTypeArgument=false
    """用于生成 pydantic 的模型时，用于标记字段的类型"""

    @classmethod
    @abstractmethod
    def comment(cls, field_meta: 'FieldMetaInfo') -> str:
        """用于渲染 Excel 表头的注释"""

    @classmethod
    @abstractmethod
    def serialize(cls, value: Any, field_meta: 'FieldMetaInfo') -> Any:
        """用于把用户填入 Excel 的数据，转换成后端代码入口可接收的数据
        如果转换失败，返回原值，用户后续捕获更准确的错误
        serialize 是聚合之后的数据
        """

    @classmethod
    @abstractmethod
    def deserialize(cls, value: Any, field_meta: 'FieldMetaInfo') -> Any:
        """用于把 pandas 读取的 Excel 之后的数据，转回用户可识别的数据, 处理聚合之前的数据"""

    @classmethod
    @abstractmethod
    def model_items(cls) -> list[tuple[Key, 'FieldMetaInfo']]:
        """用于获取模型的所有字段名"""


class ABCExcelHeader(BaseModel):
    """用于表示用户输入的 Excel 表头信息

    对于两行合并的数据，下层为 None 时，label 取上层的值，parent_label 为 None
    """

    label: Label = Field(description='Excel 的列名')
    parent_label: Label = Field(description='Excel 的父列名')
    offset: int = Field(default=0, description='合并表头·子单元格所属父单元格的偏移量')


class SystemReserved(ABCValueType):
    __name__ = 'SystemReserved'

    @classmethod
    def comment(cls, field_meta: 'FieldMetaInfo') -> str:
        return ''

    @classmethod
    def serialize(cls, value: Any, field_meta: 'FieldMetaInfo') -> Any:
        return value

    @classmethod
    def deserialize(cls, value: Any, field_meta: 'FieldMetaInfo') -> Any:
        return value

    @classmethod
    def _validate(cls, v: Any, field_meta: 'FieldMetaInfo') -> Any:
        return v


class Undefined(ABCValueType):
    __name__ = 'Undefined'

    @classmethod
    def comment(cls, field_meta: 'FieldMetaInfo') -> str:
        return ''

    @classmethod
    def serialize(cls, value: Any, field_meta: 'FieldMetaInfo') -> Any:
        return value

    @classmethod
    def deserialize(cls, value: Any, field_meta: 'FieldMetaInfo') -> Any:
        return value

    @classmethod
    def _validate(cls, v: Any, field_meta: 'FieldMetaInfo') -> Any:
        return v
