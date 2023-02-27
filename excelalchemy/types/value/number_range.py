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
    def serialize(
        cls,
        value: dict[str, str] | str | Any,
        field_meta: FieldMetaInfo,
    ) -> Any:
        if isinstance(value, str):
            value = value.strip()

        if isinstance(value, NumberRange):
            return value
        try:
            # pyright: reportGeneralTypeIssues=false
            return NumberRange(Decimal(value['start']), Decimal(value['end']))  # type: ignore[index]
        except Exception as exc:
            logging.warning('ValueType 类型 <%s> 无法解析 Excel 输入, 返回原值:%s, 原因: %s', cls.__name__, value, exc)

        return value

    # pylint: disable=too-many-branches
    @classmethod
    def _validate(cls, v: Any, field_meta: FieldMetaInfo) -> 'NumberRange':
        if not isinstance(v, NumberRange):
            try:
                v['start'] = canonicalize_decimal(Decimal(v['start']), field_meta.fraction_digits)
                v['end'] = canonicalize_decimal(Decimal(v['end']), field_meta.fraction_digits)
                parsed = NumberRange(v['start'], v['end'])
            except Exception as exc:
                raise ValueError('请输入数字') from exc
        else:
            parsed = v

        errors: list[str] = []
        if parsed.start is not None and parsed.end is not None and parsed.start > parsed.end:
            errors.append('最小值不能大于最大值')

        # importer_le 取值 field_meta.importer_le 或者无穷大
        importer_le = field_meta.importer_le or Decimal('Infinity')
        # importer_ge 取值 field_meta.importer_ge 或者无穷小
        importer_ge = field_meta.importer_ge or Decimal('-Infinity')

        if parsed.start is not None:
            if not importer_ge <= parsed.start <= importer_le:
                if field_meta.importer_le and field_meta.importer_ge:
                    errors.append(f'请输入{field_meta.importer_ge}～{field_meta.importer_le}范围内的数字')
                elif field_meta.importer_le:
                    errors.append(f'请输入-∞～{field_meta.importer_le}范围内的数字')
                elif field_meta.importer_ge:
                    errors.append(f'请输入{field_meta.importer_ge}～+∞范围内的数字')
                else:
                    pass

        if parsed.end is not None:
            if not importer_ge <= parsed.end <= importer_le:
                if field_meta.importer_le and field_meta.importer_ge:
                    errors.append(f'请输入{field_meta.importer_ge}～{field_meta.importer_le}范围内的数字')
                elif field_meta.importer_le:
                    errors.append(f'请输入-∞～{field_meta.importer_le}范围内的数字')
                elif field_meta.importer_ge:
                    errors.append(f'请输入{field_meta.importer_ge}～+∞范围内的数字')
                else:
                    pass

        if errors:
            raise ValueError(*errors)
        else:
            return parsed

    @classmethod
    def deserialize(cls, value: Any | None, field_meta: FieldMetaInfo) -> str:
        if value is None or value == '':
            return ''
        try:
            return str(transform_decimal(canonicalize_decimal(Decimal(value), field_meta.fraction_digits)))
        except Exception as exc:
            logging.warning('ValueType 类型 <%s> 无法解析 Excel 输入, 返回原值:%s, 原因: %s', cls.__name__, value, exc)
            return str(value)
