from typing import cast

from pydantic import BaseModel

from excelalchemy import FieldMeta
from excelalchemy import MultiCheckbox
from excelalchemy import OptionId
from excelalchemy import ProgrammaticError
from excelalchemy.const import MULTI_CHECKBOX_SEPARATOR
from excelalchemy.const import Option
from tests import BaseTestCase


class TestMultiCheckbox(BaseTestCase):
    async def test_comment(self):
        class Importer(BaseModel):
            multi_checkbox: MultiCheckbox = FieldMeta(label='多选框', order=1)

        alchemy = self.build_alchemy(Importer)
        field = alchemy.ordered_field_meta[0]
        field.value_type = cast(MultiCheckbox, field.value_type)

        assert field.value_type.comment(field) == '必填性：必填\n\n单/多选：多选\n'

    async def test_serialize(self):
        class Importer(BaseModel):
            multi_checkbox: MultiCheckbox = FieldMeta(label='多选框', order=1)

        alchemy = self.build_alchemy(Importer)
        field = alchemy.ordered_field_meta[0]
        field.value_type = cast(MultiCheckbox, field.value_type)

        assert field.value_type.serialize(['a', 'b'], field) == ['a', 'b']
        assert field.value_type.serialize(f'a{MULTI_CHECKBOX_SEPARATOR}b', field) == ['a', 'b']
        assert field.value_type.serialize('a', field) == ['a']
        assert field.value_type.serialize(None, field) is None
        assert field.value_type.serialize('', field) == ['']

    async def test_validate(self):
        class Importer(BaseModel):
            multi_checkbox: MultiCheckbox = FieldMeta(
                label='多选框',
                order=1,
                options=[
                    Option(id=OptionId('a'), name='a'),
                    Option(id=OptionId('b'), name='b'),
                ],
            )

        alchemy = self.build_alchemy(Importer)
        field = alchemy.ordered_field_meta[0]
        field.value_type = cast(MultiCheckbox, field.value_type)

        self.assertRaises(ValueError, field.value_type.__validate__, None, field)
        self.assertRaises(ValueError, field.value_type.__validate__, 'ddd', field)
        assert field.value_type.__validate__(['a', 'b'], field) == ['a', 'b']
        self.assertRaises(ValueError, field.value_type.__validate__, ['a', 'b', 'c'], field)
        self.assertRaises(ValueError, field.value_type.__validate__, ['a', 'b', 'c', 'c'], field)
        self.assertRaises(ValueError, field.value_type.__validate__, ['a', 'b', 'c', ''], field)

        field.options = None
        self.assertRaises(ProgrammaticError, field.value_type.__validate__, ['a', 'b'], field)

    async def test_deserialize(self):
        class Importer(BaseModel):
            multi_checkbox: MultiCheckbox = FieldMeta(
                label='多选框',
                order=1,
                options=[
                    Option(id=OptionId('age'), name='年龄'),
                    Option(id=OptionId('sex'), name='性别'),
                ],
            )

        alchemy = self.build_alchemy(Importer)
        field = alchemy.ordered_field_meta[0]
        field.value_type = cast(MultiCheckbox, field.value_type)

        assert field.value_type.deserialize([OptionId('age'), OptionId('性别')], field) == '年龄，性别'
        assert field.value_type.deserialize(f'a{MULTI_CHECKBOX_SEPARATOR}b', field) == 'a，b'
        assert field.value_type.deserialize('a', field) == 'a'
        assert field.value_type.deserialize(None, field) == ''
        assert field.value_type.deserialize('', field) == ''
