from random import choice
from typing import Any
from typing import cast
from unittest import IsolatedAsyncioTestCase

from minio import Minio
from pydantic import BaseModel

from excelalchemy import ExcelAlchemy
from excelalchemy import ExporterConfig
from excelalchemy import FieldMeta
from excelalchemy import ImporterConfig
from excelalchemy import ImportMode
from excelalchemy import Key
from excelalchemy import Number
from excelalchemy import NumberRange
from excelalchemy import Option
from excelalchemy import OptionId
from excelalchemy import String
from excelalchemy import extract_pydantic_model


class ThingCreateSuccessImporter(BaseModel):
    name: String | None = FieldMeta(
        label='名称',
        max_length=10000,
        title='title',
        options=[
            Option(OptionId('yes'), '是'),
            Option(OptionId('no'), '否'),
        ],
        order=2,
    )
    age: Number | None = FieldMeta(
        label='年龄',
        ge=-100,
        order=3,
    )
    data_range: NumberRange = FieldMeta(
        label='数值范围',
        order=1,
    )


class ThingCreateFailedImporter(BaseModel):
    name: String | None = FieldMeta(
        label='名称',
        max_length=100,
        title='title',
        options=[
            Option(OptionId('yes'), '是'),
            Option(OptionId('no'), '否'),
        ],
        order=2,
    )
    age: Number | None = FieldMeta(
        label='年龄',
        ge=100,
        order=1,
    )
    data_range: NumberRange = FieldMeta(label='数值范围', order=3)


class ThingUpdaterSuccessImporter(BaseModel):
    code: String = FieldMeta(
        label='编码',
        options=[
            Option(OptionId('yes'), '是'),
            Option(OptionId('no'), '否'),
        ],
        order=2,
    )
    name: String | None = FieldMeta(
        label='名称',
        order=1,
    )
    data_range: NumberRange = FieldMeta(label='数值范围', order=3)


class UpdateThing(BaseModel):
    id: String = FieldMeta(label='编码', order=1)
    name: String | None = FieldMeta(label='名称', order=2)
    data_range: NumberRange = FieldMeta(label='数值范围', order=3)


async def create_thing_success(data: dict[Key, Any], ctx: dict[Key, Any] | None) -> bool:
    print(f'create_thing: {data}')
    return True


async def create_thing_failed(data: dict[Key, Any], ctx: dict[Key, Any] | None) -> Any:
    print(f'create_thing_failed: {data}')
    raise Exception('create_thing_failed')


async def update_thing_success(data: dict[Key, Any], ctx: dict[Key, Any] | None) -> bool:
    print(f'update_thing: {data}')
    return True


async def update_thing_converter(data: dict[Key, Any], ctx: dict[Key, Any] | None) -> UpdateThing:
    print(f'update_thing_converter: {data}')
    return UpdateThing(**data, id='id')


async def is_data_exist(data: dict[str, Any]) -> bool:
    print(f'is_data_exist: {data}')
    return choice([True, False])


class TestExcelAlchemy(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.instance = Minio(
            endpoint='minio.teletraan.io',
            access_key='admin',
            secret_key='teletraan',
            secure=True,
        )
        self.bucket_name = 'api'

    def test_extract_pydantic_model(self):
        field_metas = extract_pydantic_model(ThingCreateSuccessImporter)
        self.assertIsNotNone(field_metas)

        print(field_metas)

    async def test_create_import_no_error(self):
        alchemy = ExcelAlchemy[dict[Key, Any], ImporterConfig](
            ImporterConfig[dict[Key, Any], ThingCreateSuccessImporter, ThingUpdaterSuccessImporter](
                import_mode=ImportMode.CREATE,
                minio=self.instance,
                bucket_name='api',
                create_importer_model=ThingCreateSuccessImporter,
                creator=create_thing_success,
            )
        )
        template = alchemy.download_template(
            sample_data=cast(
                list[dict[Key, Any]],
                [
                    ThingCreateSuccessImporter(
                        name=String('name'),
                        age=111,
                        data_range=NumberRange(start=1, end=2),
                    ).dict()
                ],
            )
        )
        self.assertIsNotNone(template)
        validate_header = alchemy._validate_header('导入数据_成功.xlsx')
        self.assertListEqual(validate_header.missing_required, [])
        self.assertListEqual(validate_header.unrecognized, [])
        import_result = await alchemy.import_data('导入数据_成功.xlsx', '导入结果.xlsx')

        print(import_result)

    async def test_create_import_with_error(self):
        alchemy = ExcelAlchemy[dict[Key, Any], ImporterConfig](
            ImporterConfig[dict[Key, Any], ThingCreateFailedImporter, ThingUpdaterSuccessImporter](
                import_mode=ImportMode.CREATE,
                minio=self.instance,
                bucket_name='api',
                create_importer_model=ThingCreateFailedImporter,
                creator=create_thing_failed,
            )
        )
        template = alchemy.download_template()

        self.assertIsNotNone(template)
        validate_header = alchemy._validate_header('导入数据_失败.xlsx')
        import_result = await alchemy.import_data('导入数据_失败.xlsx', '导入数据_失败_结果.xlsx')
        print(template)
        print(validate_header)
        print(import_result)

    async def test_export_excel(self):
        alchemy = ExcelAlchemy[Any, ExporterConfig](
            ExporterConfig[ThingCreateFailedImporter](
                minio=self.instance,
                bucket_name='api',
                exporter_model=ThingCreateFailedImporter,
            )
        )
        download_result = alchemy.export_excel(
            output_excel_name='导出数据.xlsx',
            data=cast(
                list[dict[Key, Any]],
                [
                    ThingCreateFailedImporter(
                        name=String('name'),
                        age=111,
                        data_range=NumberRange(start=1, end=2),
                    ).dict()
                ],
            ),
        )

        print(download_result)
