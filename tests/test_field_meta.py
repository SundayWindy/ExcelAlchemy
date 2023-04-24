from pydantic import BaseModel

from excelalchemy import ConfigError
from excelalchemy import DataRangeOption
from excelalchemy import Date
from excelalchemy import DateFormat
from excelalchemy import Email
from excelalchemy import FieldMeta
from excelalchemy import Number
from excelalchemy import Option
from excelalchemy import OptionId
from excelalchemy import Radio
from tests import BaseTestCase


class TestFieldMeta(BaseTestCase):
    async def test_set_is_primary_key(self):
        class Importer(BaseModel):
            email: Email = FieldMeta(
                label='邮箱',
                is_primary_key=True,
                order=1,
            )

        alchemy = self.build_alchemy(Importer)
        assert alchemy.ordered_field_meta[0].is_primary_key

        class Importer(BaseModel):
            email: Email = FieldMeta(
                label='邮箱',
                is_primary_key=False,
                order=1,
            )

        alchemy = self.build_alchemy(Importer)
        assert not alchemy.ordered_field_meta[0].is_primary_key
        alchemy.ordered_field_meta[0].set_is_primary_key(True)

        assert alchemy.ordered_field_meta[0].is_primary_key
        assert alchemy.ordered_field_meta[0].required and alchemy.ordered_field_meta[0].unique

    async def test_set_unique(self):
        class Importer(BaseModel):
            email: Email = FieldMeta(
                label='邮箱',
                unique=True,
                order=1,
            )

        alchemy = self.build_alchemy(Importer)
        assert alchemy.ordered_field_meta[0].unique

        class Importer(BaseModel):
            email: Email = FieldMeta(
                label='邮箱',
                unique=False,
                order=1,
            )

        alchemy = self.build_alchemy(Importer)
        assert not alchemy.ordered_field_meta[0].unique
        alchemy.ordered_field_meta[0].set_unique(True)

        assert alchemy.ordered_field_meta[0].unique
        assert alchemy.ordered_field_meta[0].required

    async def test_validate_state(self):
        class Importer(BaseModel):
            email: Email = FieldMeta(
                label='邮箱',
                order=1,
            )

        alchemy = self.build_alchemy(Importer)
        assert alchemy.ordered_field_meta[0].validate_state() is None

    async def test_exchange_option_ids_to_names(self):
        class Importer(BaseModel):
            sex: Radio = FieldMeta(
                label='邮箱',
                order=1,
                options=[Option(id=OptionId('male'), name='男'), Option(id=OptionId('female'), name='女')],
            )

        alchemy = self.build_alchemy(Importer)
        assert alchemy.ordered_field_meta[0].exchange_option_ids_to_names([OptionId('male')]) == ['男']
        assert alchemy.ordered_field_meta[0].exchange_option_ids_to_names([OptionId('not found')]) == ['not found']

    async def test_exchange_names_to_option_ids_with_errors(self):
        class Importer(BaseModel):
            sex: Radio = FieldMeta(
                label='邮箱',
                order=1,
                options=[Option(id=OptionId('male'), name='男'), Option(id=OptionId('female'), name='女')],
            )

        alchemy = self.build_alchemy(Importer)
        assert alchemy.ordered_field_meta[0].exchange_names_to_option_ids_with_errors(
            [OptionId('男'), OptionId('不存在')]
        ) == (['male'], ['选项不存在，请参照表头的注释填写'])

    async def test_unique_label(self):
        class Importer(BaseModel):
            email: Email = FieldMeta(
                label='邮箱',
                order=1,
            )
            email2: Email = FieldMeta(
                label='邮箱2',
                order=2,
            )

        alchemy = self.build_alchemy(Importer)
        assert alchemy.ordered_field_meta[0].unique_label == '邮箱'

        # this is a trick, in user's code, they should not do this
        alchemy.ordered_field_meta[1].parent_label = '父'
        assert alchemy.ordered_field_meta[1].unique_label == '父·邮箱2'

    async def test_unique_key(self):
        class Importer(BaseModel):
            email: Email = FieldMeta(
                label='邮箱',
                order=1,
            )
            email2: Email = FieldMeta(
                label='邮箱',
                order=2,
            )

        alchemy = self.build_alchemy(Importer)
        assert alchemy.ordered_field_meta[0].unique_key == 'email'

        # this is a trick, in user's code, they should not do this
        alchemy.ordered_field_meta[1].parent_key = 'parent'
        assert alchemy.ordered_field_meta[1].unique_key == 'parent·email2'

    async def test_options_id_map(self):
        class Importer(BaseModel):
            sex: Radio = FieldMeta(
                label='邮箱',
                order=1,
                options=[Option(id=OptionId('male'), name='男'), Option(id=OptionId('female'), name='女')],
            )

        alchemy = self.build_alchemy(Importer)
        assert alchemy.ordered_field_meta[0].options_id_map == {
            'male': Option(id=OptionId('male'), name='男'),
            'female': Option(id=OptionId('female'), name='女'),
        }

    async def test_options_name_map(self):
        class Importer(BaseModel):
            sex: Radio = FieldMeta(
                label='邮箱',
                order=1,
                options=[Option(id=OptionId('male'), name='男'), Option(id=OptionId('female'), name='女')],
            )

        alchemy = self.build_alchemy(Importer)
        assert alchemy.ordered_field_meta[0].options_name_map == {
            '男': Option(id=OptionId('male'), name='男'),
            '女': Option(id=OptionId('female'), name='女'),
        }

    async def test_comment_required(self):
        class Importer(BaseModel):
            email: Email = FieldMeta(
                label='邮箱',
                order=1,
            )
            email2: Email | None = FieldMeta(
                label='邮箱',
                order=2,
                required=False,
            )

        alchemy = self.build_alchemy(Importer)
        assert alchemy.ordered_field_meta[0].comment_required == '必填性：必填'
        assert alchemy.ordered_field_meta[1].comment_required == '必填性：选填'

    async def test_comment_date_format(self):
        class Importer(BaseModel):
            date: Date = FieldMeta(label='日期', order=1, date_format=DateFormat.DAY)
            date2: Date = FieldMeta(label='日期', order=2, date_format=DateFormat.MONTH)

        alchemy = self.build_alchemy(Importer)
        assert alchemy.ordered_field_meta[0].comment_date_format == '格式：日期（yyyy/mm/dd）'
        assert alchemy.ordered_field_meta[1].comment_date_format == '格式：日期（yyyy/mm）'

    async def test_comment_date_range_option(self):
        class Importer(BaseModel):
            ne: Date = FieldMeta(
                label='日期',
                order=1,
                date_range_option=DataRangeOption.NEXT,
            )
            no: Date = FieldMeta(
                label='日期',
                order=2,
                date_range_option=DataRangeOption.NONE,
            )
            pre: Date = FieldMeta(
                label='日期',
                order=3,
                date_range_option=DataRangeOption.PRE,
            )

        alchemy = self.build_alchemy(Importer)
        assert alchemy.ordered_field_meta[0].comment_date_range_option == '范围：晚于当前时间'
        assert alchemy.ordered_field_meta[1].comment_date_range_option == '范围：无限制'
        assert alchemy.ordered_field_meta[2].comment_date_range_option == '范围：早于当前时间'

    async def test_comment_hint(self):
        class Importer(BaseModel):
            email: Email = FieldMeta(
                label='邮箱',
                order=1,
                hint='请输入邮箱',
            )

        alchemy = self.build_alchemy(Importer)
        assert alchemy.ordered_field_meta[0].comment_hint == '提示：请输入邮箱'

    async def test_comment_options(self):
        class Importer(BaseModel):
            sex: Radio = FieldMeta(
                label='邮箱',
                order=1,
                options=[Option(id=OptionId('male'), name='男'), Option(id=OptionId('female'), name='女')],
            )

        alchemy = self.build_alchemy(Importer)
        assert alchemy.ordered_field_meta[0].comment_options == '选项：男，女'

    async def test_comment_fraction_digits(self):
        class Importer(BaseModel):
            decimal: Number = FieldMeta(
                label='邮箱',
                order=1,
                fraction_digits=2,
            )

        alchemy = self.build_alchemy(Importer)
        assert alchemy.ordered_field_meta[0].comment_fraction_digits == '小数位数：2'

    async def test_comment_unit(self):
        class Importer(BaseModel):
            decimal: Number = FieldMeta(
                label='邮箱',
                order=1,
                unit='元',
            )

        alchemy = self.build_alchemy(Importer)
        assert alchemy.ordered_field_meta[0].comment_unit == '单位：元'

    async def test_comment_unique(self):
        class Importer(BaseModel):
            email: Email = FieldMeta(
                label='邮箱',
                order=1,
                unique=True,
            )

        alchemy = self.build_alchemy(Importer)
        assert alchemy.ordered_field_meta[0].comment_unique == '唯一性：唯一'

    async def test_comment_max_length(self):
        class Importer(BaseModel):
            email: Email = FieldMeta(
                label='邮箱',
                order=1,
                max_length=10,
            )

        alchemy = self.build_alchemy(Importer)
        assert alchemy.ordered_field_meta[0].comment_max_length == '最大长度：10'

    async def test_must_date_format(self):
        class Importer(BaseModel):
            date: Date = FieldMeta(label='日期', order=1, date_format=DateFormat.DAY)
            date2: Date = FieldMeta(
                label='日期',
                order=2,
            )

        alchemy = self.build_alchemy(Importer)
        assert alchemy.ordered_field_meta[0].must_date_format == DateFormat.DAY

        with self.assertRaises(ConfigError):
            alchemy.ordered_field_meta[1].must_date_format  # noqa

    async def test_python_date_format(self):
        class Importer(BaseModel):
            date: Date = FieldMeta(label='日期', order=1, date_format=DateFormat.DAY)
            date2: Date = FieldMeta(
                label='日期',
                order=2,
            )

        alchemy = self.build_alchemy(Importer)
        assert alchemy.ordered_field_meta[0].python_date_format == '%Y-%m-%d'

        with self.assertRaises(ConfigError):
            alchemy.ordered_field_meta[1].python_date_format  # noqa
