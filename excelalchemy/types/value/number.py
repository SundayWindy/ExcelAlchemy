import logging
from decimal import ROUND_DOWN
from decimal import Context
from decimal import Decimal
from decimal import InvalidOperation
from typing import Any

from excelalchemy.types.abstract import ABCValueType
from excelalchemy.types.field import FieldMetaInfo


def canonicalize_decimal(d: Decimal, fraction_digits_limit: int | None) -> Decimal:
    if fraction_digits_limit is not None and abs(d.as_tuple().exponent) != fraction_digits_limit:
        try:
            d = Decimal(d).quantize(Decimal(f'0.{"0" * fraction_digits_limit}'), context=Context(rounding=ROUND_DOWN))
        except InvalidOperation as e:
            logging.warning('精度设置的过小，导致精度丢失，%s', e)
    return d


def transform_decimal(d: Decimal | int | float | None) -> float | int | None:
    if d is None:
        return None
    if isinstance(d, float):
        return d
    if isinstance(d, int):
        return d
    if d.as_tuple().exponent == 0:
        return int(d)
    else:
        return float(d)


class Number(Decimal, ABCValueType):
    __name__ = '数值输入'

    @classmethod
    def comment(cls, field_meta: FieldMetaInfo) -> str:
        required = '必填' if field_meta.required else '非必填'
        format_ = '数值'
        fraction_digits = field_meta.fraction_digits or 0
        if field_meta.importer_le is None and field_meta.importer_ge is None:
            range_ = '无限制'
        elif field_meta.importer_le is None:
            range_ = f'≥ {field_meta.importer_ge}'
        elif field_meta.importer_ge is None:
            range_ = f'≤ {field_meta.importer_le}'
        else:
            range_ = f'{field_meta.importer_ge}～{field_meta.importer_le}'
        unit = field_meta.unit or '无'
        extra_hint = f'\n提示：{field_meta.hint}' if field_meta.hint else ''
        return f"""必填性：{required}\n格式：{format_}\n小数位数：{fraction_digits}\n可输入范围：{range_}\n单位：{unit}""" + extra_hint

    @classmethod
    def serialize(cls, value: str | int | float, field_meta: FieldMetaInfo) -> Decimal | Any:
        if isinstance(value, str):
            value = value.strip()
        try:
            return transform_decimal(Decimal(value))
        except Exception as exc:
            logging.warning('ValueType 类型 <%s> 无法解析 Excel 输入, 返回原值:%s, 原因: %s', cls.__name__, value, exc)
            return str(value) if value is not None else ''

    @classmethod
    def __validate__(cls, v: Decimal | Any, field_meta: FieldMetaInfo) -> float | int:
        if not isinstance(v, Decimal):
            try:
                parsed = Decimal(str(v))
            except Exception as exc:
                raise ValueError('请输入数字') from exc
        else:
            parsed = v

        errors: list[str] = []

        # importer_le 取值 field_meta.importer_le 或者无穷大
        importer_le = field_meta.importer_le or Decimal('Infinity')
        # importer_ge 取值 field_meta.importer_ge 或者无穷小
        importer_ge = field_meta.importer_ge or Decimal('-Infinity')

        if not importer_ge <= parsed <= importer_le:
            if field_meta.importer_le and field_meta.importer_ge:
                errors.append(f'请输入{field_meta.importer_ge}～{field_meta.importer_le}范围内的数字')
            elif field_meta.importer_le:
                errors.append(f'请输入-∞～{field_meta.importer_le}范围内的数字')
            elif field_meta.importer_ge:
                errors.append(f'请输入{field_meta.importer_ge}～+∞范围内的数字')
            else:
                pass

        parsed = canonicalize_decimal(parsed, field_meta.fraction_digits)

        if errors:
            raise ValueError(*errors)
        else:
            v = transform_decimal(parsed)
            if v is None:
                raise ValueError('请输入数字')
            return v

    @classmethod
    def deserialize(cls, value: str | None | Any, field_meta: FieldMetaInfo) -> str:
        if value is None or value == '':
            return ''
        try:
            return str(transform_decimal(Decimal(value)))
        except Exception as exc:
            logging.warning('ValueType 类型 <%s> 无法解析 Excel 输入, 返回原值:%s, 原因: %s', cls.__name__, value, exc)
            return str(value)
