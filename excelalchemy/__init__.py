"""A Python Library for Reading and Writing Excel Files"""

__version__ = '0.1.0b3'

from excelalchemy.const import CharacterSet
from excelalchemy.const import DataRangeOption
from excelalchemy.const import DateFormat
from excelalchemy.const import Option
from excelalchemy.core.alchemy import ExcelAlchemy
from excelalchemy.exc import ExcelCellError
from excelalchemy.exc import ProgrammaticError
from excelalchemy.helper.pydantic import extract_pydantic_model
from excelalchemy.types.alchemy import ExporterConfig
from excelalchemy.types.alchemy import ImporterConfig
from excelalchemy.types.alchemy import ImportMode
from excelalchemy.types.field import FieldMeta
from excelalchemy.types.field import PatchFieldMeta
from excelalchemy.types.identity import ColumnIndex
from excelalchemy.types.identity import Key
from excelalchemy.types.identity import Label
from excelalchemy.types.identity import OptionId
from excelalchemy.types.identity import RowIndex
from excelalchemy.types.identity import UniqueKey
from excelalchemy.types.identity import UniqueLabel
from excelalchemy.types.result import ImportResult
from excelalchemy.types.result import ValidateHeaderResult
from excelalchemy.types.result import ValidateResult
from excelalchemy.types.result import ValidateRowResult
from excelalchemy.types.value.boolean import Boolean
from excelalchemy.types.value.date import Date
from excelalchemy.types.value.date_range import DateRange
from excelalchemy.types.value.email import Email
from excelalchemy.types.value.money import Money
from excelalchemy.types.value.multi_checkbox import MultiCheckbox
from excelalchemy.types.value.number import Number
from excelalchemy.types.value.number_range import NumberRange
from excelalchemy.types.value.organization import MultiOrganization
from excelalchemy.types.value.organization import SingleOrganization
from excelalchemy.types.value.phone_number import PhoneNumber
from excelalchemy.types.value.radio import Radio
from excelalchemy.types.value.staff import MultiStaff
from excelalchemy.types.value.staff import SingleStaff
from excelalchemy.types.value.string import String
from excelalchemy.types.value.tree import MultiTreeNode
from excelalchemy.types.value.tree import SingleTreeNode
from excelalchemy.types.value.url import Url
from excelalchemy.util.file import flatten

__all__ = [
    'Boolean',
    'ColumnIndex',
    'Date',
    'DateRange',
    'Email',
    'ExcelAlchemy',
    'ExcelCellError',
    'ExporterConfig',
    'FieldMeta',
    'ImportMode',
    'ImportResult',
    'ImporterConfig',
    'Key',
    'Label',
    'Money',
    'MultiCheckbox',
    'MultiOrganization',
    'MultiStaff',
    'MultiTreeNode',
    'Number',
    'NumberRange',
    'Option',
    'OptionId',
    'PatchFieldMeta',
    'PhoneNumber',
    'ProgrammaticError',
    'Radio',
    'RowIndex',
    'SingleOrganization',
    'SingleStaff',
    'SingleTreeNode',
    'String',
    'UniqueKey',
    'UniqueLabel',
    'Url',
    'ValidateHeaderResult',
    'ValidateResult',
    'ValidateRowResult',
    'extract_pydantic_model',
    'flatten',
]
