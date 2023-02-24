from typing import Any

from esm_sdk.client import EsmClient
from esm_sdk.models import ESMFieldAccessConfig
from pydantic import BaseModel

from excelalchemy.alchemy import ExcelAlchemy
from excelalchemy.model.abstract import ContextT
from excelalchemy.model.abstract import PatchFieldMeta
from excelalchemy.model.excel import ExcelExporterConfig
from excelalchemy.model.excel import ExcelImporterConfig
from excelalchemy.model.identity import UniqueKey
from excelalchemy.plugin.esm.config import ESMExcelAlchemyExporterConfig
from excelalchemy.plugin.esm.config import ESMExcelAlchemyImporterConfig
from excelalchemy.plugin.esm.screen import transform_esm_to_importer


async def build_esm_importer(
    config: ESMExcelAlchemyImporterConfig[ContextT],
) -> ExcelAlchemy[ContextT, ExcelImporterConfig[ContextT, Any, Any]]:
    esm_client = EsmClient(config.esm_url)
    patch_field_meta = _patch_field_meta_from_config(config)

    create_screen, update_screen, create_importer, update_importer = None, None, None, None
    if config.create_template_id:
        create_screen = await esm_client.query__esm_screen_of_single_scheme(
            config.auth_headers,
            config.create_template_id,
        )
        create_importer = transform_esm_to_importer(
            create_screen,
            patch_field_meta,
            lambda f, ac: (f.key in config.create_whitelist_keys or ac is ESMFieldAccessConfig.EDITABLE)
            and f.key not in config.create_blacklist_keys,
        )
    if config.update_template_id:
        update_screen = await esm_client.query__esm_screen_of_single_scheme(
            config.auth_headers,
            config.update_template_id,
        )

        unique_keys: set[UniqueKey] = {UniqueKey(x) for x in config.unique_keys or []}
        for section in update_screen.sections:
            for field in section.fields:
                field.config.required = field.key in unique_keys
        update_importer = transform_esm_to_importer(
            update_screen,
            patch_field_meta,
            lambda f, ac: f.key in config.primary_keys or ac is ESMFieldAccessConfig.EDITABLE,
        )

    importer_config = config.to_excel_importer_config(create_importer, update_importer)
    importer = ExcelAlchemy[ContextT, ExcelImporterConfig[ContextT, Any, Any]](importer_config)
    config.create_screen = create_screen
    config.update_screen = update_screen

    if config.context:
        importer.add_context(config.context)

    return importer


async def build_esm_exporter(
    config: ESMExcelAlchemyExporterConfig[ContextT],
) -> ExcelAlchemy[ContextT, ExcelExporterConfig[BaseModel]]:
    esm_client = EsmClient(config.esm_url)
    screen = await esm_client.query__esm_screen_of_single_scheme(
        config.auth_headers,
        config.template_id,
    )
    patch_field_meta = _patch_field_meta_from_config(config)
    exporter_model = transform_esm_to_importer(
        screen,
        patch_field_meta,
        lambda f, ac: True,
    )

    exporter_config = config.to_excel_exporter_config(exporter_model)
    exporter = ExcelAlchemy[ContextT, ExcelExporterConfig[BaseModel]](exporter_config)
    if config.context:
        exporter.add_context(config.context)

    return exporter


def _patch_field_meta_from_config(
    config: ESMExcelAlchemyImporterConfig[Any] | ESMExcelAlchemyExporterConfig[Any],
) -> dict[UniqueKey, PatchFieldMeta]:
    rst: dict[UniqueKey, PatchFieldMeta] = {}
    key_options = config.key_options or {}
    for primary_key in config.primary_keys:
        rst[UniqueKey(primary_key)] = PatchFieldMeta(
            unique=True,
            is_primary_key=True,
            options=key_options.get(primary_key, []),
        )
    for unique_key in config.unique_keys or []:
        if unique_key in rst:  # primary key is also unique
            continue
        rst[UniqueKey(unique_key)] = PatchFieldMeta(unique=True, options=key_options.get(unique_key, []))

    for key in key_options:
        if key not in rst:
            rst[UniqueKey(key)] = PatchFieldMeta(options=key_options.get(key, []))
    return rst
