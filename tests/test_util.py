from unittest import IsolatedAsyncioTestCase

from excelalchemy import ExcelAlchemy, FieldMeta, ImporterConfig, String, extract_pydantic_model
from excelalchemy.util.convertor import export_data_converter, import_data_converter
from pydantic import BaseModel


class TestUtil(IsolatedAsyncioTestCase):
    class Importer(BaseModel):
        name: String = FieldMeta(label='名称', order=1)
        address: String | None = FieldMeta(label='地址', order=3)

    def test_template(self):
        alchemy = ExcelAlchemy(ImporterConfig(self.Importer))
        template = alchemy.download_template()
        assert template is not None and len(template) > 100

    def test_extract_pydantic_model(self):
        field_metas = extract_pydantic_model(self.Importer)
        self.assertIsNotNone(field_metas)
        assert len(field_metas) == 2
        assert field_metas[0].label == '名称'
        assert field_metas[1].label == '地址'

    @classmethod
    def test_import_data_converter(cls):
        input_data = {'Name': 'name', 'Address': 'address', 'FieldData': {'ID': 'id', 'Name': 'name'}}
        expected = {'name': 'name', 'address': 'address', 'field_data': {'ID': 'id', 'Name': 'name'}}
        assert import_data_converter(input_data) == expected

    @classmethod
    def test_export_data_converter(cls):
        input_data = {'name': 'name', 'address': 'address', 'field_data': {'ID': 'id', 'Name': 'name'}}
        expected = {'name': 'name', 'address': 'address', 'fieldData.ID': 'id', 'fieldData.Name': 'name'}
        assert export_data_converter(input_data) == expected
