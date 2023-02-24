import datetime
import logging
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from typing import AbstractSet
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Set
from typing import TypeVar
from typing import Union

from pydantic import BaseModel
from pydantic.fields import Field
from pydantic.fields import FieldInfo
from pydantic.fields import ModelField
from pydantic.fields import Undefined
from pydantic.typing import NoArgAnyCallable

from excelalchemy.const import DEFAULT_FIELD_META_ORDER
from excelalchemy.const import MAX_OPTIONS_COUNT
from excelalchemy.const import UNIQUE_HEADER_CONNECTOR
from excelalchemy.exception import ProgrammaticError
from excelalchemy.model.identity import Key
from excelalchemy.model.identity import Label
from excelalchemy.model.identity import OptionId
from excelalchemy.model.identity import UniqueKey
from excelalchemy.model.identity import UniqueLabel

DictStrAny = Dict[str, Any]
DictAny = Dict[Any, Any]
SetStr = Set[str]
ListStr = List[str]
IntStr = Union[int, str]

ExcelConfigT = TypeVar('ExcelConfigT')
ContextT = TypeVar('ContextT')
CreateImporterModelT = TypeVar('CreateImporterModelT', bound=BaseModel)
UpdateImporterModelT = TypeVar('UpdateImporterModelT', bound=BaseModel)
ExporterModelT = TypeVar('ExporterModelT', bound=BaseModel)
CreateModelT = TypeVar('CreateModelT', bound=BaseModel)
UpdateModelT = TypeVar('UpdateModelT', bound=BaseModel)


class CharacterSet(str, Enum):
    CHINESE = 'CHINESE'
    NUMBER = 'NUMBER'
    LOWERCASE_LETTERS = 'LOWERCASE_LETTERS'
    UPPERCASE_LETTERS = 'UPPERCASE_LETTERS'
    SPECIAL_SYMBOLS = 'SPECIAL_SYMBOLS'


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
        return cls._validate(v, FieldMetaInfo.extract_from(field))

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


class SystemReservedValueType(ABCValueType):
    __name__ = 'SystemReservedValueType'

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


class UndefinedValueType(ABCValueType):
    __name__ = 'ABCValueType'

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


class ABCExcelHeader(BaseModel):
    """用于表示用户输入的 Excel 表头信息

    对于两行合并的数据，下层为 None 时，label 取上层的值，parent_label 为 None
    """

    label: Label = Field(description='Excel 的列名')
    parent_label: Label = Field(description='Excel 的父列名')
    offset: int = Field(default=0, description='合并表头·子单元格所属父单元格的偏移量')


class DateFormat(str, Enum):
    YEAR = 'YEAR'
    MONTH = 'MONTH'
    DAY = 'DAY'
    MINUTE = 'MINUTE'


class DataRangeOption(str, Enum):
    NONE = 'NONE'
    PRE = 'PRE'
    NEXT = 'NEXT'


DATE_FORMAT_TO_PYTHON_MAPPING = {
    DateFormat.YEAR: '%Y',
    DateFormat.MONTH: '%Y-%m',
    DateFormat.DAY: '%Y-%m-%d',
    DateFormat.MINUTE: '%Y-%m-%d %H:%M',
}

DATE_FORMAT_TO_HINT_MAPPING = {
    DateFormat.YEAR: 'yyyy',
    DateFormat.MONTH: 'yyyy/mm',
    DateFormat.DAY: 'yyyy/mm/dd',
    DateFormat.MINUTE: 'yyyy/mm/dd hh:mm',
}

DATA_RANGE_OPTION_TO_CHINESE = {
    DataRangeOption.PRE: '早于当前时间',
    DataRangeOption.NEXT: '晚于当前时间',
    DataRangeOption.NONE: '无限制',
}


@dataclass
class Option:
    # For user's usage, the name is the most important symbol
    id: OptionId
    name: str

    def __eq__(self, other: Any) -> bool:
        # for convenience, use name rather then id
        if isinstance(other, str):
            return self.name == other
        else:
            return False

    def __hash__(self) -> int:
        # for convenience, use name rather then id
        return hash(self.name)


class PatchFieldMeta(BaseModel):
    unique: bool | None = False  # 当前列是否唯一，不用于校验，用于渲染 Excel 表头的注释
    is_primary_key: bool | None = False  # 当前列是否为主键，不用于校验，用于渲染 Excel 表头的注释
    hint: str | None = None  # 当前列的提示信息，不用于校验，用于渲染 Excel 表头的注释
    options: list[Option] | None = None


class FieldMetaInfo(FieldInfo):
    """用于表示后端真实期望的 Excel 表头信息"""

    label: Label  # 字段用于展示给用户的名称, 必有
    is_primary_key: bool = False  # 是否为主键(产品定义的关键列）

    # 不使用自定义表单时，下面字段可以不用填写
    parent_label: Label | None = None  # 字段的父字段, 运行时必有, parent_label 等于 label

    key: Key | None = None  # 字段存储在数据库的名称, 运行时必有
    parent_key: Key | None = None  # 字段存储在数据库中的父级名称, 运行时必有

    offset: int = DEFAULT_FIELD_META_ORDER  # 合并表头·子单元格所属父单元格的偏移量, 运行时必有
    value_type: type[ABCValueType] = UndefinedValueType  # 字段的数据类型, 运行时必有
    unique: bool | None = False  # 当前列是否唯一，不用于校验，用于渲染 Excel 表头的注释

    required: bool | None = False  # 当前列是否必填，不用于校验，用于渲染 Excel 表头的注释
    ignore_import: bool | None = False  # 当前列是否忽略导入，不用于校验，用于渲染 Excel 表头的注释

    order: int = 0  # 字段的顺序, 运行时必有

    # 若增加属性，需要同步修改 helper.pydantic._complete_field_info 方法
    # TEXT相关配置
    character_set: set[CharacterSet] | None = None

    # NUMBER相关配置
    fraction_digits: int | None = None

    # DATE相关配置
    timezone: datetime.timezone
    date_format: DateFormat | None = None
    date_range_option: DataRangeOption | None = None

    # RADIO, MULTI_CHECKBOX, SELECT相关配置
    options: list[Option] | None = None

    unit: str | None = None  # 单位

    # 废弃
    agg_key: str | None = None  # 聚合字段的 key, 可选

    # pylint: disable=too-many-locals
    def __init__(
        self,
        default: Any = Undefined,
        *,
        # 导入模块增加的字段·必填
        label: str,
        # 是否为主键(产品定义的关键列）
        is_primary_key: bool = False,
        # 导入模块增加的字段·从 pydantic 模型中获取
        unique: bool = False,
        ignore_import: bool = False,
        order: int = DEFAULT_FIELD_META_ORDER,
        # TEXT
        character_set: set[CharacterSet] | None = None,
        # NUMBER
        fraction_digits: int | None = None,
        # DATE
        timezone: datetime.timezone | None = None,
        date_format: DateFormat | None = None,
        date_range_option: DataRangeOption | None = None,
        # RADIO, MULTI_CHECKBOX, SELECT
        options: list[Option] | None = None,
        unit: str | None = None,
        hint: str | None = None,
        # 导入模块增加的字段·结束
        default_factory: Optional[NoArgAnyCallable] = None,
        alias: str | None = None,
        title: str | None = None,
        description: str | None = None,
        exclude: Union[AbstractSet[IntStr], AbstractSet[IntStr], Any] = None,
        include: Union[AbstractSet[IntStr], AbstractSet[IntStr], Any] = None,
        const: bool | None = None,
        ge: float | None = None,
        le: float | None = None,
        multiple_of: float | None = None,
        allow_inf_nan: bool | None = None,
        max_digits: int | None = None,
        decimal_places: int | None = None,
        min_items: int | None = None,
        max_items: int | None = None,
        unique_items: bool | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
        allow_mutation: bool | None = True,
        regex: str | None = None,
        discriminator: str | None = None,
        repr: bool = True,
        **extra: Any,
    ) -> None:
        super().__init__(
            default,
            default_factory=default_factory,
            alias=alias,
            title=title,
            description=description,
            exclude=exclude,
            include=include,
            const=const,
            gt=None,
            lt=None,
            multiple_of=multiple_of,
            allow_inf_nan=allow_inf_nan,
            allow_mutation=allow_mutation,
            regex=regex,
            discriminator=discriminator,
            repr=repr,
            **extra,
        )
        self.importer_ge = ge
        self.importer_le = le
        self.importer_max_digits = max_digits
        self.importer_decimal_places = decimal_places
        self.importer_min_length = min_length
        self.importer_max_length = max_length
        self.importer_min_items = min_items
        self.importer_max_items = max_items
        self.importer_unique_items = unique_items

        self._validate()
        self.label = Label(label)
        self.is_primary_key = is_primary_key
        self.unique = unique or is_primary_key  # 主键一定唯一
        self.ignore_import = ignore_import
        self.order = order

        self.character_set = character_set or set(CharacterSet)
        self.fraction_digits = fraction_digits
        self.timezone = timezone or datetime.timezone(datetime.timedelta(hours=8), 'CST')
        self.date_format = date_format
        self.date_range_option = date_range_option
        self.options = options
        self.unit = unit
        self.hint = hint

        # 下列属性从 pydantic 配置中获取，不允许手动设置
        self.is_primary_key = False
        self.unique = False
        self.required = False

    def set_is_primary_key(self, is_primary_key: bool | None) -> None:
        if is_primary_key is None:
            return
        self.is_primary_key = is_primary_key
        if self.is_primary_key:
            self.unique = True
            self.required = True

    def set_unique(self, unique: bool | None) -> None:
        if unique is None:
            return
        self.unique = unique
        if self.unique:
            self.required = True

    def validate_state(self) -> None:
        if self.is_primary_key and not self.unique:
            raise ValueError('主键必须唯一')
        if (self.is_primary_key or self.unique) and self.required is False:
            raise ValueError('主键或唯一字段必须必填')

    @property
    def unique_label(self) -> UniqueLabel:
        if self.parent_label is None:
            raise RuntimeError('运行时 parent_label 不能为空')
        label = (
            f'{self.parent_label}{UNIQUE_HEADER_CONNECTOR}{self.label}'
            if self.parent_label != self.label
            else self.label
        )
        return UniqueLabel(label)

    @property
    def unique_key(self) -> UniqueKey:
        if self.parent_key is None:
            raise RuntimeError('运行时 parent_key 不能为空')
        key = f'{self.parent_key}{UNIQUE_HEADER_CONNECTOR}{self.key}' if self.parent_key != self.key else self.key
        return UniqueKey(key)

    @cached_property
    def options_id_map(self) -> dict[OptionId, Option]:
        if self.options is None:
            return {}
        if len(self.options) > MAX_OPTIONS_COUNT:
            logging.warning(
                '您为字段【%s】指定了 %s 个选项, 请考虑此数量是否合理，options 设计的本意不是为了处理大量数据',
                self.label,
                len(self.options),
            )
        return {option.id: option for option in self.options}

    @cached_property
    def options_name_map(self) -> dict[str, Option]:
        if self.options is None:
            return {}
        if len(self.options) > MAX_OPTIONS_COUNT:
            logging.warning(
                '您为字段【%s】指定了 %s 个选项, 请考虑此数量是否合理，options 设计的本意不是为了处理大量数据',
                self.label,
                len(self.options),
            )
        return {option.name: option for option in self.options}

    @staticmethod
    def extract_from(model_field: ModelField) -> 'FieldMetaInfo':
        field_info = model_field.field_info
        if not isinstance(field_info, FieldMetaInfo):
            raise ProgrammaticError('field definition must be an instance of FieldMeta')

        return field_info

    def __repr__(self):
        return f'{self.__class__.__name__}({self.label})'

    __str__ = __repr__


# pylint: disable=invalid-name
# pylint: disable=too-many-locals
def FieldMeta(
    default: Any = Undefined,
    *,
    # 导入模块增加的字段·必填
    label: str,
    # 是否为主键(产品定义的关键列）
    is_primary_key: bool = False,
    # 导入模块增加的字段·从 pydantic 模型中获取
    unique: bool = False,
    ignore_import: bool = False,
    order: int = DEFAULT_FIELD_META_ORDER,
    # TEXT
    character_set: set[CharacterSet] | None = None,
    # NUMBER
    fraction_digits: int | None = None,
    # DATE
    timezone: datetime.timezone | None = None,
    date_format: DateFormat | None = None,
    date_range_option: DataRangeOption | None = None,
    # RADIO, MULTI_CHECKBOX, SELECT
    options: list[Option] | None = None,
    unit: str | None = None,
    hint: str | None = None,
    # 导入模块增加的字段·结束
    default_factory: Optional[NoArgAnyCallable] = None,
    alias: str | None = None,
    title: str | None = None,
    description: str | None = None,
    exclude: Union[AbstractSet[IntStr], AbstractSet[IntStr], Any] = None,
    include: Union[AbstractSet[IntStr], AbstractSet[IntStr], Any] = None,
    const: bool | None = None,
    ge: float | None = None,
    le: float | None = None,
    multiple_of: float | None = None,
    allow_inf_nan: bool | None = None,
    max_digits: int | None = None,
    decimal_places: int | None = None,
    min_items: int | None = None,
    max_items: int | None = None,
    unique_items: bool | None = None,
    min_length: int | None = None,
    max_length: int | None = None,
    allow_mutation: bool | None = True,
    regex: str | None = None,
    discriminator: str | None = None,
    repr: bool = True,
    **extra: Any,
) -> Any:  # return any to ignore the annotation type
    # pyright: reportUnnecessaryIsInstance=false
    if fraction_digits is not None and not isinstance(fraction_digits, int):
        raise ValueError('fraction_digits 必须是整数')
    return FieldMetaInfo(
        default=default,
        label=label,
        is_primary_key=is_primary_key,
        unique=unique,
        ignore_import=ignore_import,
        order=order,
        character_set=character_set,
        fraction_digits=fraction_digits,
        timezone=timezone,
        date_format=date_format,
        date_range_option=date_range_option,
        options=options,
        unit=unit,
        hint=hint,
        default_factory=default_factory,
        alias=alias,
        title=title,
        description=description,
        exclude=exclude,
        include=include,
        const=const,
        ge=ge,
        le=le,
        multiple_of=multiple_of,
        allow_inf_nan=allow_inf_nan,
        max_digits=max_digits,
        decimal_places=decimal_places,
        min_items=min_items,
        max_items=max_items,
        unique_items=unique_items,
        min_length=min_length,
        max_length=max_length,
        allow_mutation=allow_mutation,
        regex=regex,
        discriminator=discriminator,
        repr=repr,
        **extra,
    )
