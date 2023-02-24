import logging
from typing import Any

from excelalchemy.const import MULTI_CHECKBOX_SEPARATOR
from excelalchemy.exception import ProgrammaticError
from excelalchemy.model.abstract import ABCValueType
from excelalchemy.model.abstract import FieldMetaInfo
from excelalchemy.model.identity import OptionId


class MultiCheckbox(ABCValueType, list[str]):
    __name__ = '复选框组'

    @classmethod
    def comment(cls, field_meta: FieldMetaInfo) -> str:
        required = '必填' if field_meta.required else '非必填'
        option = f'{MULTI_CHECKBOX_SEPARATOR}'.join([x.name for x in (field_meta.options or [])])
        is_multi = '多选'
        hint = f'多选时，请用“{MULTI_CHECKBOX_SEPARATOR}”连接多个选项，如“选项1，选项2”' + (field_meta.hint or '')
        return f"""必填性：{required}\n选项：{option}\n单/多选：{is_multi}\n提示：{hint}"""

    @classmethod
    def serialize(cls, value: str | Any, field_meta: FieldMetaInfo) -> list[str] | str:
        if isinstance(value, list):
            return [str(x).strip() for x in value]
        if isinstance(value, str):
            return [x.strip() for x in value.split(MULTI_CHECKBOX_SEPARATOR)]
        logging.warning('ValueType 类型 <%s> 无法解析 Excel 输入, 返回原值:%s', cls.__name__, value)
        return value

    @classmethod
    def _validate(cls, v: list[str] | Any, field_meta: FieldMetaInfo) -> list[str]:  # OptionId
        if not isinstance(v, list):
            raise ValueError('选项不存在，请参照表头的注释填写')

        if field_meta.options is None:
            raise ProgrammaticError('options cannot be None when validate RADIO, MULTI_CHECKBOX and SELECT')

        if not field_meta.options:  # empty
            logging.warning('类型【%s】的字段【%s】的选项为空, 将返回原值', cls.__name__, field_meta.label)
            return v

        if len(v) != len(set(v)):
            raise ValueError('选项有重复')

        errors: list[str] = []
        result: list[str] = []
        for name in v:
            option = field_meta.options_name_map.get(name)
            if option is None:
                errors.append('选项不存在，请参照表头的注释填写')
            else:
                result.append(option.id)

        if errors:
            raise ValueError(*errors)
        else:
            return result

    @classmethod
    def deserialize(cls, value: str | list[OptionId] | None | Any, field_meta: FieldMetaInfo) -> Any:
        if value is None or value == '':
            return ''
        if isinstance(value, str):
            return value

        if isinstance(value, list):
            rst: list[str] = []
            # pyright: reportUnknownArgumentType=false
            for id_ in value:
                try:
                    rst.append(field_meta.options_id_map[id_].name)
                except KeyError:
                    logging.warning('类型【%s】无法为【%s】找到【%s】的选项, 返回原值', cls.__name__, field_meta.label, value)
                    rst.append(id_)
            return f'{MULTI_CHECKBOX_SEPARATOR}'.join(rst)

        logging.warning('%s 反序列化失败', cls.__name__)
        return value if value is not None else ''
