from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Any
from typing import Awaitable
from typing import Callable
from typing import Generic
from typing import Literal
from typing import Type

from minio import Minio
from pydantic import Field

from excelalchemy.const import UNIQUE_HEADER_CONNECTOR
from excelalchemy.model.abstract import ABCExcelHeader
from excelalchemy.model.abstract import ContextT
from excelalchemy.model.abstract import CreateImporterModelT
from excelalchemy.model.abstract import ExporterModelT
from excelalchemy.model.abstract import UpdateImporterModelT
from excelalchemy.model.identity import Label
from excelalchemy.model.identity import UniqueLabel
from excelalchemy.tool.convertor import export_data_converter
from excelalchemy.tool.convertor import import_data_converter


class ExcelHeader(ABCExcelHeader):
    """用于表示用户输入的 Excel 表头信息"""

    label: Label = Field(description='Excel 的列名')
    parent_label: Label = Field(description='Excel 的父列名, 如果没有父列名, parent_label 等于 label')
    offset: int = Field(default=0, description='合并表头·子单元格所属父单元格的偏移量')

    @property
    def unique_label(self) -> UniqueLabel:
        """返回唯一标签"""
        label = (
            f'{self.parent_label}{UNIQUE_HEADER_CONNECTOR}{self.label}'
            if self.parent_label != self.label
            else self.label
        )
        return UniqueLabel(label)


class ExcelMode(str, Enum):
    """Excel 模式"""

    IMPORT = 'IMPORT'
    EXPORT = 'EXPORT'


class ImportMode(str, Enum):
    CREATE = 'CREATE'  # 创建
    UPDATE = 'UPDATE'  # 更新
    CREATE_OR_UPDATE = 'CREATE_OR_UPDATE'  # 创建或更新


@dataclass
class ExcelImporterConfig(Generic[ContextT, CreateImporterModelT, UpdateImporterModelT]):
    import_mode: ImportMode = field(default=ImportMode.CREATE)

    create_importer_model: Type[CreateImporterModelT] | None = field(default=None)
    update_importer_model: Type[UpdateImporterModelT] | None = field(default=None)

    # Callable function receive Key as dict key instead of Label.
    data_converter: Callable[[dict[str, Any]], dict[str, Any]] | None = field(default=import_data_converter)
    creator: Callable[[dict[str, Any], ContextT | None], Awaitable[Any]] | None = field(default=None)
    updater: Callable[[dict[str, Any], ContextT | None], Awaitable[Any]] | None = field(default=None)

    context: ContextT | None = field(default=None)
    is_data_exist: Callable[[dict[str, Any], ContextT | None], Awaitable[bool]] | None = field(default=None)
    exec_formatter: Callable[[Exception], str] = field(default=str)

    minio: Minio = field(default=None)
    bucket_name: str = field(default='excel')
    url_expires: int = field(default=3600)

    sheet_name: Literal['Sheet1'] = field(default='Sheet1')

    def validate_model(self):
        if self.import_mode not in ImportMode.__members__.values():
            raise ValueError(f'导入模式 {self.import_mode} 不合法')

        match self.import_mode:
            case ImportMode.CREATE:
                self._validate_create()
            case ImportMode.UPDATE:
                self._validate_update()
            case ImportMode.CREATE_OR_UPDATE:
                self._validate_create_or_update()
            case _:
                raise ValueError(f'导入模式 {self.import_mode} 不合法')

        return self

    # 创建模式验证
    def _validate_create(self):
        if self.import_mode != ImportMode.CREATE:
            raise ValueError(f'导入模式 {self.import_mode} 不合法')
        if not self.create_importer_model:
            raise ValueError('当选择【创建模式】时，创建模型不能为空')

    # 更新模式验证
    def _validate_update(self):
        if self.import_mode != ImportMode.UPDATE:
            raise ValueError(f'导入模式 {self.import_mode} 不合法')
        if not self.update_importer_model:
            raise ValueError('当选择【更新模式】时，更新模型不能为空')

    # 创建或更新模式验证
    def _validate_create_or_update(self):
        if self.import_mode != ImportMode.CREATE_OR_UPDATE:
            raise ValueError(f'导入模式 {self.import_mode} 不合法')

        if not self.create_importer_model:
            raise ValueError('当选择【创建或更新模式】时，创建模型不能为空')
        if not self.update_importer_model:
            raise ValueError('当选择【创建或更新模式】时，更新模型不能为空')
        if not self.is_data_exist:
            raise ValueError('当选择【创建或更新模式】时，数据存在判断函数不能为空')
        # 创建模型和更新模型的字段必须一致
        if self.create_importer_model.__fields__.keys() != self.update_importer_model.__fields__.keys():
            raise ValueError('创建模型和更新模型的字段名称必须一致')

    def __post_init__(self):
        self.validate_model()


@dataclass
class ExcelExporterConfig(Generic[ExporterModelT]):
    exporter_model: Type[ExporterModelT]
    # Callable function receive Key as dict key instead of Label.
    data_converter: Callable[[dict[str, Any]], dict[str, Any]] | None = field(default=export_data_converter)

    minio: Minio = field(default=None)
    bucket_name: str = field(default='excel')
    url_expires: int = field(default=3600)

    sheet_name: Literal['Sheet1'] = field(default='Sheet1')

    def validate_model(self):
        if not self.exporter_model:
            raise ValueError('导出模型不能为空')
        return self

    def __post_init__(self):
        self.validate_model()
