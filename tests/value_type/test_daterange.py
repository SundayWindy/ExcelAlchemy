from pydantic import BaseModel

from excelalchemy import DateRange
from excelalchemy import FieldMeta
from excelalchemy import ValidateResult
from tests import BaseTestCase
from tests.registry import FileRegistry


class TestDateRange(BaseTestCase):
    async def test_daterange(self):
        class Importer(BaseModel):
            date_range: DateRange = FieldMeta(label='日期范围', order=1)

        alchemy = self.build_alchemy(Importer)
        result = await alchemy.import_data(
            input_excel_name=FileRegistry.TEST_DATE_RANGE_INPUT, output_excel_name='result.xlsx'
        )
        assert result.result == ValidateResult.SUCCESS, '导入失败'

    async def test_daterange_missing_before(self):
        """对于合并的表头，如果后面缺失
            日期范围	｜    （这里合并了表头）｜
            开始日期	｜    （这里缺了一个值）｜
        DataFrame 不会读到第一行第二列的值，因此 ExcelAlchemy 不会认为有合并得表头
        """

        class Importer(BaseModel):
            date_range: DateRange = FieldMeta(label='日期范围', order=1)

        alchemy = self.build_alchemy(Importer)
        result = await alchemy.import_data(
            input_excel_name=FileRegistry.TEST_DATE_RANGE_MISSING_INPUT_BEFORE, output_excel_name='result.xlsx'
        )
        # ExcelAlchemy 任务需要的表头是 DateRange.model_items（开始日期，结束日期）
        # 但是 Excel 读到的表头是 日期范围
        assert result.result == ValidateResult.HEADER_INVALID, '导入失败'
        assert sorted(result.missing_required) == sorted(['开始日期', '结束日期'])
        assert result.unrecognized == ['日期范围']

    async def test_test_date_range_missing_input_after(self):
        """对于合并的表头，如果前面缺失
            日期范围	        ｜   （这里合并了表头）｜
            （这里缺了一个值）	｜    开始日期       ｜
        DataFrame 能正确读到四个值，因此 ExcelAlchemy 会认为有合并得表头
        """

        class Importer(BaseModel):
            date_range: DateRange = FieldMeta(label='日期范围', order=1)

        alchemy = self.build_alchemy(Importer)
        result = await alchemy.import_data(
            input_excel_name=FileRegistry.TEST_DATE_RANGE_MISSING_INPUT_AFTER, output_excel_name='result.xlsx'
        )
        assert result.result == ValidateResult.HEADER_INVALID, '导入失败'
        assert sorted(result.missing_required) == sorted(['结束日期'])
        assert result.unrecognized == ['日期范围']
