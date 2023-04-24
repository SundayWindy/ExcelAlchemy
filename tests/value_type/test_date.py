from typing import cast

from minio import Minio
from pydantic import BaseModel

from excelalchemy import ConfigError
from excelalchemy import Date
from excelalchemy import DateFormat
from excelalchemy import ExcelAlchemy
from excelalchemy import ExcelCellError
from excelalchemy import FieldMeta
from excelalchemy import ImporterConfig
from excelalchemy import ValidateResult
from tests import BaseTestCase
from tests.registry import FileRegistry


class TestValueType(BaseTestCase):
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

    async def test_date_wrong_range(self):
        class Importer(BaseModel):
            birth_date: Date = FieldMeta(label='出生日期', order=6, date_format=DateFormat.MONTH)

        alchemy = self.build_alchemy(Importer)

        result = await alchemy.import_data(
            input_excel_name=FileRegistry.TEST_DATE_INPUT_WRONG_RANGE,
            output_excel_name='result.xlsx',
        )
        assert result.result == ValidateResult.DATA_INVALID
        error = alchemy.cell_errors[self.first_data_row][self.first_data_col][0]
        assert isinstance(error, ExcelCellError)
        assert error.label == '出生日期'
        assert error.message == '请输入格式为yyyy/mm的日期'  # may be more accurate to say "请输入格式为yyyy/mm的日期，如2021/01"
        assert repr(error) == "ExcelCellError(label='出生日期', message='请输入格式为yyyy/mm的日期')"
        assert str(error) == '【出生日期】请输入格式为yyyy/mm的日期'

    async def test_date_wrong_format(self):
        class Importer(BaseModel):
            birth_date: Date = FieldMeta(label='出生日期', order=6, date_format=DateFormat.DAY)

        alchemy = self.build_alchemy(Importer)
        result = await alchemy.import_data(
            input_excel_name=FileRegistry.TEST_DATE_INPUT_WRONG_FORMAT,
            output_excel_name='result.xlsx',
        )

        assert result.result == ValidateResult.DATA_INVALID
        error = alchemy.cell_errors[self.first_data_row][self.first_data_col][0]
        assert isinstance(error, ExcelCellError)
        assert error.label == '出生日期'
        assert error.message == '请输入格式为yyyy/mm/dd的日期'
