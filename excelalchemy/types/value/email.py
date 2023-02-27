from typing import Any

from pydantic import EmailStr

from excelalchemy.types.field import FieldMetaInfo
from excelalchemy.types.value.string import String


class Email(String):
    @classmethod
    def _validate(cls, v: Any, field_meta: FieldMetaInfo) -> str:
        try:
            parsed = str(v)
        except Exception as exc:
            raise ValueError('请输入正确的邮箱') from exc

        try:
            EmailStr.validate(parsed)
        except Exception as exc:
            raise ValueError('请输入正确的邮箱') from exc

        return parsed
