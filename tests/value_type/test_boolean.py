from pydantic import BaseModel

from excelalchemy import Boolean
from excelalchemy import FieldMeta
from excelalchemy import ValidateResult
from tests import BaseTestCase
from tests.registry import FileRegistry


class TestBoolean(BaseTestCase):
    async def test_boolean(self):
        """测试导入时，布尔值正确读取"""

        class Importer(BaseModel):
            is_active: Boolean = FieldMeta(label='是否启用', order=1)

        alchemy = self.build_alchemy(Importer)
        result = await alchemy.import_data(
            input_excel_name=FileRegistry.TEST_BOOLEAN_INPUT, output_excel_name='result.xlsx'
        )
        assert result.result == ValidateResult.SUCCESS, '导入失败'
