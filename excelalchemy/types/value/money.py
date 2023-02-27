from typing import Any

from excelalchemy.types.field import FieldMetaInfo
from excelalchemy.types.value.number import Number


class Money(Number):
    @classmethod
    def _validate(cls, v: Any, field_meta: FieldMetaInfo) -> float | int:
        field_meta.fraction_digits = 2
        return super()._validate(v, field_meta)
