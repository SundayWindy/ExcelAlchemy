from typing import cast

from pydantic import BaseModel

from excelalchemy import FieldMeta
from excelalchemy import NumberRange
from tests import BaseTestCase


class TestNumberRange(BaseTestCase):
    def test_comment(self):
        class Importer(BaseModel):
            number: NumberRange = FieldMeta(label='数字', order=1, comment='数字')

        alchemy = self.build_alchemy(Importer)
        field = alchemy.ordered_field_meta[0]
        field.value_type = cast(NumberRange, field.value_type)

        assert field.value_type.comment(field) == '必填性：必填\n格式：数值\n小数位数：0\n可输入范围：无限制\n单位：无'
        assert len(field.value_type.model_items()) == 2

    async def test_serialize(self):
        class Importer(BaseModel):
            number: NumberRange = FieldMeta(label='数字', order=1)

        alchemy = self.build_alchemy(Importer)
        field = alchemy.ordered_field_meta[0]
        field.value_type = cast(NumberRange, field.value_type)

        assert field.value_type.serialize(1.23, field) == 1.23
        assert field.value_type.serialize(
            {
                'start': 1.23,
                'end': 1.23,
            },
            field,
        ) == {
            'start': 1.23,
            'end': 1.23,
        }
        assert field.value_type.serialize(
            NumberRange(start=1.23, end=1.23),
            field,
        ) == {
            'start': 1.23,
            'end': 1.23,
        }
