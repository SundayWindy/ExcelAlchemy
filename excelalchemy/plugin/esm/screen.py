import logging
from collections import defaultdict
from collections.abc import Callable
from typing import Any
from typing import Awaitable
from typing import TypeVar
from typing import cast

from esm_sdk.models import ESMField
from esm_sdk.models import ESMFieldAccessConfig
from esm_sdk.models import ESMScreen
from esm_sdk.models import ESMScreenField
from esm_sdk.models import ESMWidgetType
from pydantic import BaseConfig
from pydantic import BaseModel
from pydantic import Extra
from pydantic import Field
from pydantic import create_model

from excelalchemy import DateRange
from excelalchemy import MultiOrganization
from excelalchemy import MultiStaff
from excelalchemy import NumberRange
from excelalchemy import SingleOrganization
from excelalchemy import SingleStaff
from excelalchemy.const import MAX_OPTIONS_COUNT
from excelalchemy.model.abstract import ABCValueType
from excelalchemy.model.abstract import DataRangeOption
from excelalchemy.model.abstract import DateFormat
from excelalchemy.model.abstract import FieldMetaInfo
from excelalchemy.model.abstract import Option
from excelalchemy.model.abstract import PatchFieldMeta
from excelalchemy.model.identity import OptionId
from excelalchemy.model.identity import UniqueKey
from excelalchemy.model.value_type.boolean import Boolean
from excelalchemy.model.value_type.date import Date
from excelalchemy.model.value_type.multi_checkbox import MultiCheckbox
from excelalchemy.model.value_type.number import Number
from excelalchemy.model.value_type.radio import Radio
from excelalchemy.model.value_type.string import String

EntityT = TypeVar('EntityT', bound=BaseModel)
T = TypeVar('T')


def transform_esm_to_importer(
    screen: ESMScreen,
    patch_field_meta: dict[UniqueKey, PatchFieldMeta] | None = None,
    field_selector: Callable[[ESMField, ESMFieldAccessConfig], bool] = lambda f, ac: ac
    is ESMFieldAccessConfig.EDITABLE,
) -> type[BaseModel]:
    """将自定义表单结构转换为 pydantic model"""
    entity_fields = _build_selected_validation_model(
        screen,
        field_selector,
    )
    if patch_field_meta is not None:
        for key, (_, field_meta) in entity_fields.items():
            if key in patch_field_meta:
                _patch_field_meta(field_meta, patch_field_meta[UniqueKey(key)])

    return create_model(  # type: ignore[call-overload, no-any-return]
        screen.name,
        **entity_fields,
    )


def make_esm_transformer(
    screen: ESMScreen,
    entity_type: type[EntityT],
) -> Callable[[BaseModel, Any], Awaitable[EntityT]]:
    # pylint: disable=unused-argument
    async def transformer(importer_instance: BaseModel, *args: Any, **kwargs: Any) -> EntityT:
        result = CommonEntity()

        id_to_screen_field_def = {field_def.id: field_def for sec in screen.sections for field_def in sec.fields}
        all_used_fields = [
            id_to_screen_field_def[field.field_id]
            for field in screen.fields
            if field.access_config is ESMFieldAccessConfig.EDITABLE
        ]

        for field in all_used_fields:
            if not hasattr(importer_instance, field.key):
                continue
            value = getattr(importer_instance, field.key)
            setattr(result, field.key, value)
            if not field.is_system_preset:
                result.field_data[field.id] = value

        old = entity_type.Config.extra
        entity_type.Config.extra = Extra.allow
        rst = cast(EntityT, entity_type.parse_obj(result))
        if not hasattr(rst, 'field_data'):
            setattr(rst, 'field_data', result.field_data)
        entity_type.Config.extra = old
        return rst

    return transformer


def _patch_field_meta(field_meta: FieldMetaInfo, patch: PatchFieldMeta) -> None:
    """将补丁信息应用到 FieldMeta 中, 原地修改"""
    field_meta.set_unique(patch.unique)
    field_meta.set_is_primary_key(patch.is_primary_key)
    field_meta.validate_state()

    field_meta.options = patch.options
    field_meta.hint = patch.hint
    if patch.options and len(patch.options) > MAX_OPTIONS_COUNT:
        logging.warning(
            '您为字段【%s】指定了 %s 个选项, 请考虑此数量是否合理，options 设计的本意不是为了处理大量数据',
            field_meta.label,
            len(patch.options),
        )


class CommonEntity(BaseModel):
    class Config(BaseConfig):
        extra = Extra.allow

    field_data: dict[str, Any] = Field(default_factory=dict)


def _maybe_optional(field_def: ESMField, value_type: type[ABCValueType]) -> Any:
    if field_def.config.required:
        return value_type
    else:
        return value_type | None


def _assert_label(field_def: ESMField) -> str:
    if field_def.config.label is None:
        raise Exception(f'field {field_def.key} label must be valid')
    else:
        return field_def.config.label


def _assert_not_null(v: T | None) -> T:
    if v is None:
        raise Exception('value cannot be null')
    else:
        return v


def _build_field_type__fallback(_: ESMField) -> tuple[Any, FieldMetaInfo] | None:
    return None  # skip this field


def _build_field_type__checkbox(field_def: ESMField) -> tuple[Any, FieldMetaInfo] | None:
    return (
        _maybe_optional(field_def, Radio),
        FieldMetaInfo(
            label=_assert_label(field_def),
            options=[Option(id=OptionId(o.id), name=o.label) for o in _assert_not_null(field_def.config.options)],
        ),
    )


def _build_field_type__date(field_def: ESMField) -> tuple[Any, FieldMetaInfo] | None:
    if field_def.config.view is not None:
        date_format = DateFormat(field_def.config.view)
    else:
        date_format = None

    if field_def.config.date_range_option:
        date_range_option = DataRangeOption(field_def.config.date_range_option)
    else:
        date_range_option = None

    return _maybe_optional(field_def, Date), FieldMetaInfo(
        label=_assert_label(field_def),
        date_format=date_format,
        date_range_option=date_range_option,
    )


def _build_field_type__date_range(field_def: ESMField) -> tuple[Any, FieldMetaInfo] | None:
    if field_def.config.view is not None:
        date_format = DateFormat(field_def.config.view)
    else:
        date_format = None

    if field_def.config.date_range_option:
        date_range_option = DataRangeOption(field_def.config.date_range_option)
    else:
        date_range_option = None

    return _maybe_optional(field_def, DateRange), FieldMetaInfo(
        label=_assert_label(field_def),
        date_format=date_format,
        date_range_option=date_range_option,
    )


def _build_field_type__multi_checkbox(field_def: ESMField) -> tuple[Any, FieldMetaInfo] | None:
    return (
        _maybe_optional(field_def, MultiCheckbox),
        FieldMetaInfo(
            label=_assert_label(field_def),
            options=[Option(id=OptionId(o.id), name=o.label) for o in _assert_not_null(field_def.config.options)],
        ),
    )


def _build_field_type__number(field_def: ESMField) -> tuple[Any, FieldMetaInfo] | None:
    return (
        _maybe_optional(field_def, Number),
        FieldMetaInfo(
            label=_assert_label(field_def),
            fraction_digits=field_def.config.fraction_digits,
            ge=field_def.config.number_range.start if field_def.config.number_range else None,
            le=field_def.config.number_range.end if field_def.config.number_range else None,
        ),
    )


def _build_field_type__number_range(field_def: ESMField) -> tuple[Any, FieldMetaInfo] | None:
    return (
        _maybe_optional(field_def, NumberRange),
        FieldMetaInfo(
            label=_assert_label(field_def),
            fraction_digits=field_def.config.fraction_digits,
            ge=field_def.config.number_range.start if field_def.config.number_range else None,
            le=field_def.config.number_range.end if field_def.config.number_range else None,
        ),
    )


def _build_field_type__radio(field_def: ESMField) -> tuple[Any, FieldMetaInfo] | None:
    return (
        _maybe_optional(field_def, Radio),
        FieldMetaInfo(
            label=_assert_label(field_def),
            options=[Option(id=OptionId(o.id), name=o.label) for o in _assert_not_null(field_def.config.options)],
        ),
    )


def _build_field_type__staff(field_def: ESMField) -> tuple[Any, FieldMetaInfo] | None:
    field_meta = FieldMetaInfo(
        label=_assert_label(field_def),
        options=[Option(id=OptionId(o.id), name=o.label) for o in _assert_not_null(field_def.config.options)],
    )

    if field_def.config.multiple is True:
        return _maybe_optional(field_def, MultiStaff), field_meta
    else:
        return _maybe_optional(field_def, SingleStaff), field_meta


def _build_field_type__organize(field_def: ESMField) -> tuple[Any, FieldMetaInfo] | None:
    field_meta = FieldMetaInfo(
        label=_assert_label(field_def),
        options=[Option(id=OptionId(o.id), name=o.label) for o in _assert_not_null(field_def.config.options)],
    )

    if field_def.config.multiple is True:
        return _maybe_optional(field_def, MultiOrganization), field_meta
    else:
        return _maybe_optional(field_def, SingleOrganization), field_meta


def _build_field_type__select(field_def: ESMField) -> tuple[Any, FieldMetaInfo] | None:
    field_meta = FieldMetaInfo(
        label=_assert_label(field_def),
        options=[Option(id=OptionId(o.id), name=o.label) for o in _assert_not_null(field_def.config.options)],
    )

    if field_def.config.multiple is True:
        return _maybe_optional(field_def, MultiCheckbox), field_meta
    else:
        return _maybe_optional(field_def, Radio), field_meta


def _build_field_type__switch(field_def: ESMField) -> tuple[Any, FieldMetaInfo] | None:
    return _maybe_optional(field_def, Boolean), FieldMetaInfo(
        label=_assert_label(field_def),
    )


def _build_field_type__text(field_def: ESMField) -> tuple[Any, FieldMetaInfo] | None:
    return _maybe_optional(field_def, String), FieldMetaInfo(
        label=_assert_label(field_def),
        max_length=field_def.config.max_length,
    )


def _build_field_type__attachment(_: ESMField) -> tuple[Any, FieldMetaInfo] | None:
    return None  # do not support attachment currently


_TYPE_BUILDER: dict[ESMWidgetType, Callable[[ESMField], tuple[Any, FieldMetaInfo] | None,],] = defaultdict(
    lambda: _build_field_type__fallback,
    {
        ESMWidgetType.CHECKBOX: _build_field_type__switch,
        ESMWidgetType.DATE: _build_field_type__date,
        ESMWidgetType.DATE_RANGE: _build_field_type__date_range,
        ESMWidgetType.MULTI_CHECKBOX: _build_field_type__multi_checkbox,
        ESMWidgetType.NUMBER: _build_field_type__number,
        ESMWidgetType.NUMBER_RANGE: _build_field_type__number_range,
        ESMWidgetType.RADIO: _build_field_type__radio,
        ESMWidgetType.SELECT: _build_field_type__select,
        ESMWidgetType.STAFF: _build_field_type__staff,
        ESMWidgetType.ORGANIZE: _build_field_type__organize,
        ESMWidgetType.SWITCH: _build_field_type__switch,
        ESMWidgetType.TEXT: _build_field_type__text,
        ESMWidgetType.ATTACHMENT: _build_field_type__attachment,
    },
)


def _build_field_type(field_def: ESMField, index: int) -> tuple[Any, FieldMetaInfo] | None:
    filed_type = _TYPE_BUILDER[field_def.widget_type](field_def)
    if filed_type is not None:
        filed_type[1].order = index
    return filed_type


def _build_selected_validation_model(
    screen: ESMScreen,
    field_selector: Callable[[ESMField, ESMFieldAccessConfig], bool],
) -> dict[str, tuple[Any, FieldMetaInfo]]:
    # expand field definitions
    scr_field_defs = [field_def for sec in screen.sections for field_def in sec.fields]
    id_to_screen_field_ref: dict[str, ESMScreenField] = {
        scr_field_ref.field_id: scr_field_ref for scr_field_ref in screen.fields
    }

    # build validation fields' definitions
    validation_fields_defs: dict[str, tuple[Any, FieldMetaInfo]] = {}

    for idx, scr_field_def in enumerate(scr_field_defs):
        scr_field_ref = id_to_screen_field_ref.get(scr_field_def.id)

        if scr_field_ref is None:
            continue

        if not field_selector(scr_field_def, scr_field_ref.access_config):
            continue

        field_type = _build_field_type(scr_field_def, idx)
        if field_type is None:
            # this field is skipped!
            continue

        key = scr_field_def.key
        if not scr_field_def.is_system_preset:
            key = f'fieldData.{key}'
        validation_fields_defs[key] = (
            field_type[0],
            field_type[1],
        )

    return validation_fields_defs
