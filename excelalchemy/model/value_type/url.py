from typing import Any

from pydantic import BaseModel
from pydantic import HttpUrl

from excelalchemy.model.abstract import FieldMetaInfo
from excelalchemy.model.value_type.string import String


class HttpUrlValidator(BaseModel):
    url: HttpUrl


class Url(String):
    @classmethod
    def _validate(cls, v: Any, field_meta: FieldMetaInfo) -> str:
        try:
            parsed = str(v)
        except Exception as exc:
            raise ValueError('请输入正确的网址') from exc

        errors: list[str] = []

        try:
            HttpUrlValidator.parse_obj({'url': parsed})
        except Exception:
            errors.append('请输入正确的网址')

        if errors:
            raise ValueError(*errors)
        else:
            return parsed
