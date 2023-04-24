from pydantic import BaseModel

from excelalchemy import DateRange
from excelalchemy import FieldMeta
from excelalchemy import ValidateResult
from tests import BaseTestCase
from tests.registry import FileRegistry


class TestValueType(BaseTestCase):
    async def test_daterange(self):
        class Importer(BaseModel):
            date_range: DateRange = FieldMeta(label='日期范围', order=1)

        alchemy = self.build_alchemy(Importer)
        result = await alchemy.import_data(
            input_excel_name=FileRegistry.TEST_DATE_RANGE_INPUT, output_excel_name='result.xlsx'
        )
        assert result.result == ValidateResult.SUCCESS, '导入失败'
