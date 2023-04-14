from typing import Any
from typing import cast
from unittest import IsolatedAsyncioTestCase

from minio import Minio
from pydantic import BaseModel

from excelalchemy import Boolean
from excelalchemy import ColumnIndex
from excelalchemy import ConfigError
from excelalchemy import Date
from excelalchemy import DateFormat
from excelalchemy import ExcelAlchemy
from excelalchemy import ExcelCellError
from excelalchemy import FieldMeta
from excelalchemy import ImporterConfig
from excelalchemy import RowIndex
from excelalchemy import ValidateResult
from tests.mock_minio import local_minio
from tests.registry import FileRegistry

# __all__ = [
#     'Boolean',
#     'ColumnIndex',
#     'Date',
#     'DateRange',
#     'Email',
#     'ExcelAlchemy',
#     'ExcelCellError',
#     'ExporterConfig',
#     'FieldMeta',
#     'ImportMode',
#     'ImportResult',
#     'ImporterConfig',
#     'Key',
#     'Label',
#     'Money',
#     'MultiCheckbox',
#     'MultiOrganization',
#     'MultiStaff',
#     'MultiTreeNode',
#     'Number',
#     'NumberRange',
#     'Option',
#     'OptionId',
#     'PatchFieldMeta',
#     'PhoneNumber',
#     'ProgrammaticError',
#     'Radio',
#     'RowIndex',
#     'SingleOrganization',
#     'SingleStaff',
#     'SingleTreeNode',
#     'String',
#     'UniqueKey',
#     'UniqueLabel',
#     'Url',
#     'ValidateHeaderResult',
#     'ValidateResult',
#     'ValidateRowResult',
#     'extract_pydantic_model',
#     'flatten',
# ]


class TestValueType(IsolatedAsyncioTestCase):
    minio = local_minio
    first_data_row: RowIndex = 0
    first_data_col: ColumnIndex = 2

    async def test_header_invalid(self):
        """测试导入时，表头不正确"""

        class Importer(BaseModel):
            is_active: Boolean = FieldMeta(label='是否启用', order=1)

        config = ImporterConfig(Importer, minio=cast(Minio, self.minio))
        alchemy = ExcelAlchemy(config)

        result = await alchemy.import_data(
            input_excel_name=FileRegistry.TEST_HEADER_INVALID_INPUT, output_excel_name='result.xlsx'
        )

        assert result.result == ValidateResult.HEADER_INVALID

    async def test_boolean(self):
        """测试导入时，布尔值正确读取"""

        class Importer(BaseModel):
            is_active: Boolean = FieldMeta(label='是否启用', order=1)

        async def create(data: dict[str, Any], context: dict[str, Any] | None) -> dict[str, Any]:
            assert 'is_active' in data
            return data

        config = ImporterConfig(Importer, creator=create, minio=cast(Minio, self.minio))
        alchemy = ExcelAlchemy(config)
        result = await alchemy.import_data(
            input_excel_name=FileRegistry.TEST_BOOLEAN_INPUT, output_excel_name='result.xlsx'
        )
        assert result.result == ValidateResult.SUCCESS, '导入失败'

    async def test_date_no_format(self):
        """测试导入时，日期格式未指定"""

        class Importer(BaseModel):
            birth_date: Date = FieldMeta(label='出生日期', order=6)

        config = ImporterConfig(Importer, minio=cast(Minio, self.minio))
        alchemy = ExcelAlchemy(config)

        with self.assertRaises(ConfigError):
            alchemy.download_template()

        with self.assertRaises(ConfigError):
            await alchemy.import_data(input_excel_name=FileRegistry.TEST_DATE_INPUT, output_excel_name='result.xlsx')

    async def test_date_wrong_format(self):
        class Importer(BaseModel):
            birth_date: Date = FieldMeta(label='出生日期', order=6, date_format=DateFormat.MONTH)

        async def create(data: dict[str, Any], context: dict[str, Any] | None) -> dict[str, Any]:
            assert 'birth_date' in data
            return data

        config = ImporterConfig(Importer, creator=create, minio=cast(Minio, self.minio))
        alchemy = ExcelAlchemy(config)

        result = await alchemy.import_data(
            input_excel_name=FileRegistry.TEST_DATE_INPUT_WRONG_FORMAT, output_excel_name='result.xlsx'
        )
        assert result.result == ValidateResult.DATA_INVALID
        error = alchemy.cell_errors[self.first_data_row][self.first_data_col][0]
        assert isinstance(error, ExcelCellError)
        assert error.label == '出生日期'
        assert error.message == '请输入格式为yyyy/mm的日期'
