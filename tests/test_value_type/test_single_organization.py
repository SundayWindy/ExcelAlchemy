from typing import cast

from pydantic import BaseModel

from excelalchemy import FieldMeta
from excelalchemy import Option
from excelalchemy import OptionId
from excelalchemy import SingleOrganization
from tests import BaseTestCase


class TestSingleOrganization(BaseTestCase):
    async def test_comment(self):
        class Importer(BaseModel):
            single_organization: SingleOrganization = FieldMeta(label='单选组织', order=1)

        alchemy = self.build_alchemy(Importer)
        field = alchemy.ordered_field_meta[0]
        field.value_type = cast(SingleOrganization, field.value_type)

        assert field.value_type.comment(field) == "必填性：必填\n提示：需按照组织架构树填写组织完整路径，例如 'XX公司/一级部门/二级部门'."

    async def test_serialize(self):
        class Importer(BaseModel):
            single_organization: SingleOrganization = FieldMeta(label='单选组织', order=1)

        alchemy = self.build_alchemy(Importer)
        field = alchemy.ordered_field_meta[0]
        field.value_type = cast(SingleOrganization, field.value_type)

        assert field.value_type.serialize('XX公司/一级部门/二级部门', field) == 'XX公司/一级部门/二级部门'

    async def test_deserialize(self):
        class Importer(BaseModel):
            single_organization: SingleOrganization = FieldMeta(
                label='单选组织',
                order=1,
                options=[
                    Option(id=OptionId(1), name='XX公司/一级部门/二级部门'),
                ],
            )

        alchemy = self.build_alchemy(Importer)
        field = alchemy.ordered_field_meta[0]
        field.value_type = cast(SingleOrganization, field.value_type)

        assert field.value_type.deserialize('XX公司/一级部门/二级部门', field) == 'XX公司/一级部门/二级部门'
        assert field.value_type.deserialize('1', field) == 'XX公司/一级部门/二级部门'
