import logging
from decimal import Decimal
from typing import Any

from excelalchemy.types.abstract import ComplexABCValueType
from excelalchemy.types.field import FieldMetaInfo
from excelalchemy.types.identity import Key
from excelalchemy.types.value.number import Number
from excelalchemy.types.value.number import canonicalize_decimal
from excelalchemy.types.value.number import transform_decimal


class NumberRange(ComplexABCValueType):
    start: float | int | None
    end: float | int | None

    __name__ = '数值范围'

    def __init__(self, start: Decimal | int | float | None, end: Decimal | int | float | None):
        # pyright: reportUnknownMemberType=false
        # trick: for dict call to get the correct value
        super().__init__(start=transform_decimal(start), end=transform_decimal(end))
        self.start = transform_decimal(start)
        self.end = transform_decimal(end)

    @classmethod
    def model_items(cls) -> list[tuple[Key, FieldMetaInfo]]:
        return [
            (Key('start'), FieldMetaInfo(label='最小值')),
            (Key('end'), FieldMetaInfo(label='最大值')),
        ]

    @classmethod
    def comment(cls, field_meta: FieldMetaInfo) -> str:
        return Number.comment(field_meta)

    @classmethod
    def serialize(cls, value: dict[str, str] | str | Any, field_meta: FieldMetaInfo) -> Any:
        # Strip leading/trailing whitespace from a string value
        if isinstance(value, str):
            value = value.strip()

        # Return the given value if it is already a NumberRange object
        if isinstance(value, NumberRange):
            return value

        # Attempt to create a new NumberRange object from a dictionary
        try:
            # pyright: reportGeneralTypeIssues=false
            start, end = Decimal(value['start']), Decimal(value['end'])  # type: ignore[index]
            return NumberRange(start, end)
        except (KeyError, TypeError, ValueError) as exc:
            logging.warning('%s 类型无法解析 Excel 输入，返回原值 %s。原因：%s', cls.__name__, value, exc)

        # Return the original value if parsing fails
        return value

    @classmethod
    def deserialize(cls, value: Any | None, field_meta: FieldMetaInfo) -> str:
        if value is None or value == '':
            return ''
        try:
            return str(transform_decimal(canonicalize_decimal(Decimal(value), field_meta.fraction_digits)))
        except Exception as exc:
            logging.warning('ValueType 类型 <%s> 无法解析 Excel 输入, 返回原值:%s, 原因: %s', cls.__name__, value, exc)
            return str(value)

    @classmethod
    def __validate__(cls, value: Any, field_meta: FieldMetaInfo) -> 'NumberRange':
        parsed = cls.__maybe_number_range__(value, field_meta)
        errors: list[str] = []
        if parsed.start is not None and parsed.end is not None and parsed.start > parsed.end:
            errors.append('最小值不能大于最大值')

        if parsed.start is not None:
            errors.extend(Number.__check_range__(parsed.start, field_meta))
        if parsed.end is not None:
            errors.extend(Number.__check_range__(parsed.end, field_meta))

        if errors:
            raise ValueError(*errors)
        else:
            return parsed

    @staticmethod
    def __maybe_number_range__(value: dict[str, Decimal] | Any, field_meta: FieldMetaInfo) -> 'NumberRange':
        if isinstance(value, NumberRange):
            return value

        if isinstance(value, dict):
            try:
                value['start'] = canonicalize_decimal(Decimal(value['start']), field_meta.fraction_digits)
                value['end'] = canonicalize_decimal(Decimal(value['end']), field_meta.fraction_digits)
                return NumberRange(value['start'], value['end'])
            except Exception as exc:
                raise ValueError('请输入数字') from exc

        raise ValueError('请输入数字')
