from typing import cast

from pydantic import BaseModel

from excelalchemy import FieldMeta
from excelalchemy import Money
from tests import BaseTestCase


class TestMoney(BaseTestCase):
    async def test_validate(self):
        class Importer(BaseModel):
            money: Money = FieldMeta(label='金额', order=1)

        alchemy = self.build_alchemy(Importer)
        field = alchemy.ordered_field_meta[0]

        field.value_type = cast(Money, field.value_type)
        self.assertRaises(ValueError, field.value_type.__validate__, 'ddd', field)

        assert field.value_type.__validate__(1.23, field) == 1.23
        assert field.value_type.__validate__(1.234, field) == 1.23
