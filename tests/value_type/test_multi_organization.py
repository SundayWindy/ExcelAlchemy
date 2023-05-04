from typing import cast

from pydantic import BaseModel

from excelalchemy import FieldMeta
from excelalchemy import MultiOrganization
from excelalchemy import Option
from excelalchemy import OptionId
from tests import BaseTestCase


class TestMultiOrganization(BaseTestCase):
    async def test_comment(self):
        class Importer(BaseModel):
            multi_organization: MultiOrganization = FieldMeta(label='多选组织', order=1)

        alchemy = self.build_alchemy(Importer)
        field = alchemy.ordered_field_meta[0]
        field.value_type = cast(MultiOrganization, field.value_type)

        assert field.value_type.comment(field) == '必填性：必填\n提示：需按照组织架构树填写组织完整路径，如“XX公司/一级部门/二级部门”，多选时，选项之间用“、”连接'

    async def test_deserialize(self):
        class Importer(BaseModel):
            multi_organization: MultiOrganization = FieldMeta(
                label='多选组织',
                order=1,
                options=[
                    Option(id=OptionId(1), name='一级部门'),
                    Option(id=OptionId(2), name='三级部门'),
                ],
            )

        alchemy = self.build_alchemy(Importer)
        field = alchemy.ordered_field_meta[0]
        field.value_type = cast(MultiOrganization, field.value_type)

        assert field.value_type.deserialize('XX公司/一级部门/二级部门、XX公司/一级部门/三级部门', field) == 'XX公司/一级部门/二级部门、XX公司/一级部门/三级部门'
        assert field.value_type.deserialize([1, 2], field) == '一级部门，三级部门'
        assert field.value_type.deserialize([1, 2, 3], field) == '一级部门，三级部门，3'
