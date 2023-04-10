import asyncio
from typing import Any, cast
from unittest import IsolatedAsyncioTestCase
from minio import Minio
from excelalchemy import (
    Boolean,
    Date,
    DateRange,
    Email,
    ExcelAlchemy,
    FieldMeta,
    ImporterConfig,
    Money,
    MultiCheckbox,
    MultiOrganization,
    MultiStaff,
    MultiTreeNode,
    Number,
    NumberRange,
    Option,
    PhoneNumber,
    Radio,
    SingleOrganization,
    SingleStaff,
    SingleTreeNode,
    String, Url, ProgrammaticError,
)
from pydantic import BaseModel
from tests.mock_minio import LocalMockMinio


class TestImport(IsolatedAsyncioTestCase):
    class Importer(BaseModel):
        age: Number = FieldMeta(label='年龄', order=1)
        name: String = FieldMeta(label='名称', order=2)
        address: String | None = FieldMeta(label='地址', order=4)
        is_active: Boolean = FieldMeta(label='是否激活', order=5)
        birth_date: Date = FieldMeta(label='出生日期', order=6)
        max_stay_date: DateRange = FieldMeta(label='最大停留日期', order=7)
        email: Email = FieldMeta(label='邮箱', order=8)
        price: Money = FieldMeta(label='价格', order=9)
        hobby: MultiCheckbox = FieldMeta(label='爱好', order=10)
        company: MultiOrganization = FieldMeta(label='公司', order=11)
        manager: MultiStaff = FieldMeta(label='经理', order=12)
        department: MultiTreeNode = FieldMeta(label='部门', order=13)
        salary: NumberRange = FieldMeta(label='工资', order=14)
        phone: PhoneNumber = FieldMeta(label='电话', order=15)
        radio: Radio = FieldMeta(label='单选', order=16)
        boss: SingleOrganization = FieldMeta(label='老板', order=17)
        leader: SingleStaff = FieldMeta(label='领导', order=18)
        team: SingleTreeNode = FieldMeta(label='团队', order=19)
        web: Url = FieldMeta(label='网址', order=20)

    @staticmethod
    async def create(data: dict[str, Any], context: dict[str, Any] | None) -> dict[str, Any]:
        if context is None:
            context = {}
        company_id = context.get('company_id')
        await asyncio.sleep(1)
        data['company_id'] = company_id
        return data

    minio = LocalMockMinio()

    async def test_none_field_meta(self):
        class Importer(BaseModel):
            option: Option = FieldMeta(label='选项', order=15)

        config = ImporterConfig(Importer, creator=self.create, minio=cast(Minio, self.minio))
        with self.assertRaises(ProgrammaticError):
            ExcelAlchemy(config)

    async def test_date(self):
        class Importer(BaseModel):
            birth_date: Date = FieldMeta(label='出生日期', order=6)

        config = ImporterConfig(Importer, creator=self.create, minio=cast(Minio, self.minio))
        with self.assertRaises(RuntimeError):
            alchemy = ExcelAlchemy(config)
            alchemy.download_template()

    async def test_import_success(self):
        class Importer(BaseModel):
            max_stay_date: DateRange = FieldMeta(label='最大停留日期', order=7)

        config = ImporterConfig(self.Importer, creator=self.create, minio=cast(Minio, self.minio))
        alchemy = ExcelAlchemy(config)
        # template = alchemy.download_template()
        # assert template is not None
