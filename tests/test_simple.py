from unittest import IsolatedAsyncioTestCase

from pydantic import BaseModel

from excelalchemy import ExcelAlchemy, extract_pydantic_model
from excelalchemy import FieldMeta
from excelalchemy import ImporterConfig
from excelalchemy import String


class SimpleTest(IsolatedAsyncioTestCase):
    class Importer(BaseModel):
        name: String = FieldMeta(label='名称', order=1)
        address: String | None = FieldMeta(label='地址', order=3)

    def test_simple(self):
        alchemy = ExcelAlchemy(ImporterConfig(self.Importer))
        template = alchemy.download_template()
        assert template is not None and len(template) > 100

    def test_extract_pydantic_model(self):
        field_metas = extract_pydantic_model(self.Importer)
        self.assertIsNotNone(field_metas)
        assert len(field_metas) == 2
        assert field_metas[0].label == '名称'
        assert field_metas[1].label == '地址'
