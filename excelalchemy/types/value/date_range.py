import logging
from datetime import datetime
from typing import Any
from typing import cast

import pendulum

# pyright: reportPrivateImportUsage=false
from pendulum import DateTime
from pydantic import BaseModel

from excelalchemy.const import DATE_FORMAT_TO_HINT_MAPPING
from excelalchemy.const import DATE_FORMAT_TO_PYTHON_MAPPING
from excelalchemy.const import MILLISECOND_TO_SECOND
from excelalchemy.const import DataRangeOption
from excelalchemy.types.abstract import ComplexABCValueType
from excelalchemy.types.column.field import FieldMetaInfo
from excelalchemy.types.identity import Key


class _DateRangeImpl(BaseModel):
    start: datetime | None
    end: datetime | None


class DateRange(ComplexABCValueType):
    start: datetime | None
    end: datetime | None

    __name__ = '日期范围'

    @classmethod
    def parse_obj(cls, obj: Any) -> 'DateRange':
        impl = _DateRangeImpl.parse_obj(obj)
        self = cls(impl.start, impl.end)
        return self

    def __init__(self, start: datetime | None, end: datetime | None):
        # pyright: reportUnknownMemberType=false
        # trick, BaseMode.dict() 会得到时间戳，而不是 datetime 对象，这是预期的行为
        _start = int(start.timestamp() * MILLISECOND_TO_SECOND) if start else None
        _end = int(end.timestamp() * MILLISECOND_TO_SECOND) if end else None
        super().__init__(start=_start, end=_end)
        self.start = start
        self.end = end

    @classmethod
    def model_items(cls) -> list[tuple[Key, FieldMetaInfo]]:
        return [
            (Key('start'), FieldMetaInfo(label='开始日期')),
            (Key('end'), FieldMetaInfo(label='结束日期')),
        ]

    @classmethod
    def comment(cls, field_meta: FieldMetaInfo) -> str:
        required = '必填' if field_meta.required else '选填'
        if field_meta.date_format is None:
            raise RuntimeError('日期格式未定义')
        extra_hint = field_meta.hint or ''
        date_hint = DATE_FORMAT_TO_HINT_MAPPING[field_meta.date_format]
        return f"""必填性：{required}\n格式：日期（{date_hint}）\n提示：开始日期不得晚于结束日期{extra_hint}"""

    @classmethod
    def serialize(cls, value: dict[str, str] | Any, field_meta: FieldMetaInfo) -> dict[str, DateTime | None] | Any:
        if isinstance(value, dict):
            try:
                _start = value['start']
                _end = value['end']

                start: DateTime | None = (
                    pendulum.parse(_start).replace(tzinfo=field_meta.timezone)  # type: ignore[union-attr,call-arg]
                    if _start
                    else None
                )
                end: DateTime | None = (
                    pendulum.parse(_end).replace(tzinfo=field_meta.timezone)  # type: ignore[union-attr,call-arg]
                    if _end
                    else None
                )
                # pyright: reportGeneralTypeIssues=false
                return {'start': start, 'end': end}
            except Exception as exc:
                logging.warning('ValueType 类型 <%s> 无法解析 Excel 输入, 返回原值:%s, 原因: %s', cls.__name__, value, exc)
                return value
        elif isinstance(value, datetime):
            return value
        elif isinstance(value, str):
            d: DateTime = cast(DateTime, pendulum.parse(value))
            return d.replace(tzinfo=field_meta.timezone)
        else:
            return value

    @classmethod
    def _validate(
        cls,
        v: dict[str, DateTime | None] | Any,
        field_meta: FieldMetaInfo,
    ) -> 'DateRange':
        try:
            parsed = DateRange.parse_obj(v)
            parsed.start = parsed.start.replace(tzinfo=field_meta.timezone) if parsed.start else parsed.start
            parsed.end = parsed.end.replace(tzinfo=field_meta.timezone) if parsed.end else parsed.end
        except Exception as exc:
            raise ValueError('无法识别的输入') from exc

        errors: list[str] = []
        now = datetime.now(tz=field_meta.timezone)

        if parsed.start and parsed.end and parsed.start > parsed.end:
            errors.append('开始日期不得晚于结束日期')

        match field_meta.date_range_option:
            case DataRangeOption.PRE:
                if (parsed.start and parsed.start > now) or (parsed.end and parsed.end > now):
                    errors.append('需早于当前时间（含当前时间）')
            case DataRangeOption.NEXT:
                if (parsed.start and parsed.start < now) or (parsed.end and parsed.end < now):
                    errors.append('需晚于当前时间（含当前时间）')
            case DataRangeOption.NONE | None:
                ...  # do nothing

        if errors:
            raise ValueError(*errors)
        else:
            return parsed

    @classmethod
    def deserialize(cls, value: dict[str, str] | str | Any | None, field_meta: FieldMetaInfo) -> str:
        if value is None or value == '':
            return ''
        date_format = field_meta.date_format
        if date_format is None:
            raise RuntimeError('日期格式未定义')
        py_date_format = DATE_FORMAT_TO_PYTHON_MAPPING[date_format]
        if isinstance(value, str):
            return value

        if isinstance(value, datetime):
            return value.strftime(py_date_format)

        if isinstance(value, dict):
            start = value['start']
            end = value['end']
            if isinstance(start, (int, float)):
                start = datetime.fromtimestamp(start / MILLISECOND_TO_SECOND).strftime(py_date_format)
            if isinstance(end, (int, float)):
                end = datetime.fromtimestamp(end / MILLISECOND_TO_SECOND).strftime(py_date_format)
            return start + ' - ' + end

        logging.warning('%s 反序列化失败，返回原值', cls.__name__)
        return value if value is not None else ''
