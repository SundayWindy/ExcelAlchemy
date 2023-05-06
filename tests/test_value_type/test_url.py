from typing import cast

from pydantic import BaseModel

from excelalchemy import FieldMeta
from excelalchemy import Url
from tests import BaseTestCase


class TestUrl(BaseTestCase):
    async def test_comment(self):
        class Importer(BaseModel):
            url: Url = FieldMeta(label='url', order=1)

        alchemy = self.build_alchemy(Importer)
        field = alchemy.ordered_field_meta[0]
        field.value_type = cast(Url, field.value_type)

        assert field.value_type.comment(field) == '唯一性：非唯一\n必填性：必填\n最大长度：无限制\n可输入内容:中文、数字、大写字母、小写字母、符号\n'

    async def test_serialize(self):
        class Importer(BaseModel):
            url: Url = FieldMeta(label='url', order=1)

        alchemy = self.build_alchemy(Importer)
        field = alchemy.ordered_field_meta[0]
        field.value_type = cast(Url, field.value_type)

        assert field.value_type.serialize('http://www.baidu.com', field) == 'http://www.baidu.com'

    async def test_deserialize(self):
        class Importer(BaseModel):
            url: Url = FieldMeta(label='url', order=1)

        alchemy = self.build_alchemy(Importer)
        field = alchemy.ordered_field_meta[0]
        field.value_type = cast(Url, field.value_type)

        assert field.value_type.deserialize('http://www.baidu.com', field) == 'http://www.baidu.com'
        assert field.value_type.deserialize('1', field) == '1'

    async def test_validate(self):
        class Importer(BaseModel):
            url: Url = FieldMeta(label='url', order=1)

        alchemy = self.build_alchemy(Importer)
        field = alchemy.ordered_field_meta[0]
        field.value_type = cast(Url, field.value_type)

        assert field.value_type.__validate__('http://www.baidu.com', field) == 'http://www.baidu.com'
        self.assertRaises(ValueError, field.value_type.__validate__, '1', field)
