from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic

from excelalchemy.const import ContextT
from excelalchemy.const import CreateModelT
from excelalchemy.const import ExporterModelT
from excelalchemy.const import ImporterCreateModelT
from excelalchemy.const import ImporterUpdateModelT
from excelalchemy.const import UpdateModelT
from excelalchemy.types.identity import Base64Str
from excelalchemy.types.identity import Key
from excelalchemy.types.identity import UrlStr
from excelalchemy.types.result import ImportResult


class ABCExcelAlchemy(
    ABC,
    Generic[
        ContextT,
        ImporterCreateModelT,
        ImporterUpdateModelT,
        CreateModelT,
        UpdateModelT,
        ExporterModelT,
    ],
):
    @abstractmethod
    def download_template(self, sample_data: list[dict[str, Any]] | None = None) -> str:
        """下载导入模版, Excel 字段顺序与定义的导出模型一致"""

    @abstractmethod
    async def import_data(self, input_excel_name: str, output_excel_name: str) -> ImportResult:
        """导入数据"""

    @abstractmethod
    def export(self, data: list[dict[str, Any]], keys: list[Key] | None = None) -> Base64Str:
        """导出数据，返回 base64 编码的 excel 文件, 字段顺序与定义的导出模型一致"""

    @abstractmethod
    def export_upload(self, output_name: str, data: list[dict[str, Any]], keys: list[Key] | None = None) -> UrlStr:
        """导出数据, 自动将文件上传到 Minio，字段顺序与定义的导出模型一致"""

    @abstractmethod
    def add_context(self, context: ContextT):
        """添加上下文"""
