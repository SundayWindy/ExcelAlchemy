from typing import cast

from pydantic import BaseModel

from excelalchemy import FieldMeta
from excelalchemy import Option
from excelalchemy import OptionId
from excelalchemy import SingleStaff
from tests import BaseTestCase


class TestSingleStaff(BaseTestCase):
    async def test_comment(self):
        class Importer(BaseModel):
            staff: SingleStaff = FieldMeta(label='员工', comment='员工')

        alchemy = self.build_alchemy(Importer)
        field = alchemy.ordered_field_meta[0]
        field.value_type = cast(SingleStaff, field.value_type)

        assert field.value_type.comment(field) == '必填性：必填 \n提示：请输入人员姓名和工号，如“张三/001”'

    async def test_serialize(self):
        class Importer(BaseModel):
            staff: SingleStaff = FieldMeta(
                label='员工',
                comment='员工',
                options=[
                    Option(id=OptionId(1), name='张三/001'),
                ],
            )

        alchemy = self.build_alchemy(Importer)
        field = alchemy.ordered_field_meta[0]
        field.value_type = cast(SingleStaff, field.value_type)

        assert field.value_type.serialize('张三/001', field) == '张三/001'
        assert field.value_type.serialize(OptionId(1), field) == '1'

    async def test_deserialize(self):
        class Importer(BaseModel):
            staff: SingleStaff = FieldMeta(
                label='员工',
                comment='员工',
                options=[
                    Option(id=OptionId(1), name='张三/001'),
                ],
            )

        alchemy = self.build_alchemy(Importer)
        field = alchemy.ordered_field_meta[0]
        field.value_type = cast(SingleStaff, field.value_type)

        assert field.value_type.deserialize('张三/001', field) == '张三/001'
        assert field.value_type.deserialize('1', field) == '张三/001'

    async def test_validate(self):
        class Importer(BaseModel):
            staff: SingleStaff = FieldMeta(
                label='员工',
                comment='员工',
                options=[
                    Option(id=OptionId(1), name='张三/001'),
                ],
            )

        alchemy = self.build_alchemy(Importer)
        field = alchemy.ordered_field_meta[0]
        field.value_type = cast(SingleStaff, field.value_type)

        assert field.value_type.__validate__('张三/001', field) == '1'
        assert field.value_type.__validate__('1', field) == '1'
