from excelalchemy import ExcelCellError
from excelalchemy import Label
from excelalchemy.exc import ExcelRowError
from tests import BaseTestCase


class TestException(BaseTestCase):
    async def test_equal(self):
        exc1 = ExcelCellError(label=Label('邮箱'), message='请输入正确的邮箱')
        exc2 = ExcelCellError(label=Label('邮箱'), message='请输入正确的邮箱')
        assert exc1 == exc2

        exc1 = ExcelCellError(label=Label('邮箱'), message='请输入正确的邮箱')
        exc2 = ExcelCellError(label=Label('邮箱1'), message='请输入正确的邮箱')

        assert exc1 != exc2

    async def test_repr(self):
        exc1 = ExcelCellError(label=Label('邮箱'), message='请输入正确的邮箱')
        assert repr(exc1) == "ExcelCellError(label=Label('邮箱'), message='请输入正确的邮箱')"

    async def test_str(self):
        exc1 = ExcelCellError(label=Label('邮箱'), message='请输入正确的邮箱')
        assert str(exc1) == '【邮箱】请输入正确的邮箱'

    async def test_wrong_init(self):
        self.assertRaises(ValueError, ExcelCellError, label=Label(''), message='请输入正确的邮箱')

    async def test_unique_label(self):
        exc1 = ExcelCellError(label=Label('邮箱'), message='请输入正确的邮箱')
        assert exc1.unique_label == '邮箱'

        exc1 = ExcelCellError(label=Label('邮箱'), message='请输入正确的邮箱', parent_label=Label('父'))
        assert exc1.unique_label == '父·邮箱'

    async def test_eq(self):
        exc1 = ExcelCellError(label=Label('邮箱'), message='请输入正确的邮箱')
        exc2 = ExcelCellError(label=Label('邮箱'), message='请输入正确的邮箱')
        assert exc1 == exc2

        exc1 = ExcelCellError(label=Label('邮箱'), message='请输入正确的邮箱')
        exc2 = ExcelCellError(label=Label('邮箱1'), message='请输入正确的邮箱')
        assert exc1 != exc2

        exc1 = ExcelCellError(label=Label('邮箱'), message='请输入正确的邮箱')
        other = 'other'

        assert exc1 != other
        assert other != exc1

    async def test_row_error(self):
        exc1 = ExcelRowError(message='导入 Excel 发生行错误')
        assert exc1.message == '导入 Excel 发生行错误'

        exc1 = ExcelRowError(message='请输入正确的邮箱')
        assert exc1.message == '请输入正确的邮箱'

        exc1 = ExcelRowError(message='请输入正确的邮箱')
        assert str(exc1) == '请输入正确的邮箱'

        exc1 = ExcelRowError(message='请输入正确的邮箱')
        assert repr(exc1) == "ExcelRowError(message='请输入正确的邮箱')"
