"""ExcelAlchemy, a Python library for reading and writing Excel files."""

__version__ = '0.1a2'

from excelalchemy.alchemy import ExcelAlchemy
from excelalchemy.exception import ExcelCellError
from excelalchemy.exception import ProgrammaticError
from excelalchemy.model.abstract import CharacterSet
from excelalchemy.model.abstract import DataRangeOption
from excelalchemy.model.abstract import DateFormat
from excelalchemy.model.abstract import FieldMeta
from excelalchemy.model.abstract import Option
from excelalchemy.model.abstract import PatchFieldMeta
from excelalchemy.model.excel import ExcelExporterConfig
from excelalchemy.model.excel import ExcelImporterConfig
from excelalchemy.model.excel import ImportMode
from excelalchemy.model.identity import ColumnIndex
from excelalchemy.model.identity import Key
from excelalchemy.model.identity import Label
from excelalchemy.model.identity import OptionId
from excelalchemy.model.identity import RowIndex
from excelalchemy.model.identity import UniqueKey
from excelalchemy.model.identity import UniqueLabel
from excelalchemy.model.result import ImportDataResult
from excelalchemy.model.result import ImportExcelResult
from excelalchemy.model.result import ImportRowResult
from excelalchemy.model.result import ValidateHeaderResult
from excelalchemy.model.value_type.boolean import Boolean
from excelalchemy.model.value_type.date import Date
from excelalchemy.model.value_type.date_range import DateRange
from excelalchemy.model.value_type.email import Email
from excelalchemy.model.value_type.money import Money
from excelalchemy.model.value_type.multi_checkbox import MultiCheckbox
from excelalchemy.model.value_type.number import Number
from excelalchemy.model.value_type.number_range import NumberRange
from excelalchemy.model.value_type.organization import MultiOrganization
from excelalchemy.model.value_type.organization import SingleOrganization
from excelalchemy.model.value_type.phone_number import PhoneNumber
from excelalchemy.model.value_type.radio import Radio
from excelalchemy.model.value_type.staff import MultiStaff
from excelalchemy.model.value_type.staff import SingleStaff
from excelalchemy.model.value_type.string import String
from excelalchemy.model.value_type.tree import MultiTreeNode
from excelalchemy.model.value_type.tree import SingleTreeNode
from excelalchemy.model.value_type.url import Url
from excelalchemy.util import flatten

__all__ = [
    'ExcelAlchemy',
    'ExcelCellError',
    'ProgrammaticError',
    'CharacterSet',
    'DataRangeOption',
    'DateFormat',
    'FieldMeta',
    'Option',
    'PatchFieldMeta',
    'ExcelExporterConfig',
    'ExcelImporterConfig',
    'ImportMode',
    'ColumnIndex',
    'Key',
    'Label',
    'OptionId',
    'RowIndex',
    'UniqueKey',
    'UniqueLabel',
    'ImportDataResult',
    'ImportExcelResult',
    'ImportRowResult',
    'ValidateHeaderResult',
    'Boolean',
    'Date',
    'DateRange',
    'Email',
    'Money',
    'MultiCheckbox',
    'Number',
    'NumberRange',
    'MultiOrganization',
    'SingleOrganization',
    'PhoneNumber',
    'Radio',
    'MultiStaff',
    'SingleStaff',
    'String',
    'Url',
    'flatten',
    'SingleTreeNode',
    'MultiTreeNode',
]
