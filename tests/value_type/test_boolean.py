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

    async def test_boolean_deserialize(self):
        class Importer(BaseModel):
            is_active: Boolean = FieldMeta(label='是否启用', order=1)

        alchemy = self.build_alchemy(Importer)
        field = alchemy.ordered_field_meta[0]
        assert field.value_type.deserialize(None, field) == '否'
        assert field.value_type.deserialize(True, field) == '是'
        assert field.value_type.deserialize(False, field) == '否'
        assert field.value_type.deserialize('是', field) == '是'
        assert field.value_type.deserialize('否', field) == '否'
        assert field.value_type.deserialize('任何无法识别的值', field) == '任何无法识别的值'
        assert field.value_type.deserialize('', field) == '否'
