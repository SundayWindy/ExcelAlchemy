import logging
from datetime import datetime
from typing import Any
from typing import cast

import pendulum
from pendulum import DateTime

from excelalchemy.const import DATA_RANGE_OPTION_TO_CHINESE
from excelalchemy.const import DATE_FORMAT_TO_HINT_MAPPING
from excelalchemy.const import DATE_FORMAT_TO_PYTHON_MAPPING
from excelalchemy.const import MILLISECOND_TO_SECOND
from excelalchemy.const import DataRangeOption
from excelalchemy.types.abstract import ABCValueType
from excelalchemy.types.field import FieldMetaInfo


class Date(ABCValueType, datetime):
    __name__ = '日期选择'

    @classmethod
    def comment(cls, field_meta: FieldMetaInfo) -> str:
        required_str = '必填' if field_meta.required else '选填'
        date_format = field_meta.date_format
        if not date_format:
            raise RuntimeError('日期格式未定义')
        date_hint = DATE_FORMAT_TO_HINT_MAPPING[date_format]
        date_range_option = field_meta.date_range_option
        range_hint = DATA_RANGE_OPTION_TO_CHINESE[date_range_option] if date_range_option else '无限制'
        extra_hint = f'\n提示：{field_meta.hint}' if field_meta.hint else ''

        return f"""必填性：{required_str}
                格式：日期（{date_hint}）
                范围：{range_hint}
                {extra_hint}
                """

    @classmethod
    def serialize(cls, value: str | DateTime | Any, field_meta: FieldMetaInfo) -> datetime | Any:
        if isinstance(value, DateTime):
            logging.info('类型【%s】无需序列化: %s, 返回原值 %s ', cls.__name__, field_meta.label, value)
            return value

        if not field_meta.date_format:
            raise RuntimeError('日期格式未定义')

        value = str(value).strip()
        try:
            # pyright: reportPrivateImportUsage=false
            # pyright: reportUnknownMemberType=false
            # pyright: reportGeneralTypeIssues=false
            v = value.replace('/', '-')  # pendulum 不支持 / 作为日期分隔符
            dt: DateTime = cast(DateTime, pendulum.parse(v))
            return dt.replace(tzinfo=field_meta.timezone)
        except Exception as exc:
            logging.warning('ValueType 类型 <%s> 无法解析 Excel 输入，返回原值：%s，原因：%s', cls.__name__, value, exc)
            return value

    @classmethod
    def deserialize(cls, value: str | datetime | None | Any, field_meta: FieldMetaInfo) -> str:
        match value:
            case None | '':
                return ''
            case datetime():
                python_date_format = DATE_FORMAT_TO_PYTHON_MAPPING[field_meta.date_format]
                return value.strftime(python_date_format)
            case int() | float():
                python_date_format = DATE_FORMAT_TO_PYTHON_MAPPING[field_meta.date_format]
                return datetime.fromtimestamp(int(value) / MILLISECOND_TO_SECOND).strftime(python_date_format)
            case _:
                return str(value) if value is not None else ''

    @classmethod
    def __validate__(cls, v: Any, field_meta: FieldMetaInfo) -> int:
        if field_meta.date_format is None:
            raise RuntimeError('日期格式未定义')

        if not isinstance(v, datetime):
            raise ValueError(f'请输入格式为{DATE_FORMAT_TO_HINT_MAPPING[field_meta.date_format]}的日期')

        parsed = cls._parse_date(v, field_meta)
        errors = cls._validate_date_range(parsed, field_meta)

        if errors:
            raise ValueError(*errors)
        else:
            return int(parsed.timestamp() * MILLISECOND_TO_SECOND)

    @staticmethod
    def _parse_date(v: datetime, field_meta: FieldMetaInfo) -> datetime:
        parsed = v.replace(tzinfo=field_meta.timezone)
        return parsed

    @staticmethod
    def _validate_date_range(parsed: datetime, field_meta: FieldMetaInfo) -> tuple[str]:
        now = datetime.now(tz=field_meta.timezone)
        errors = []

        match field_meta.date_range_option:
            case DataRangeOption.PRE:
                if parsed > now:
                    errors.append('需早于当前时间（含当前时间）')
            case DataRangeOption.NEXT:
                if parsed < now:
                    errors.append('需晚于当前时间（含当前时间）')
            case DataRangeOption.NONE | None:
                ...

        return tuple(errors)
