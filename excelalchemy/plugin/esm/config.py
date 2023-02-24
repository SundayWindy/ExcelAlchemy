import logging
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Awaitable
from typing import Callable
from typing import Generic
from typing import Mapping

from esm_sdk.models import ESMScreen
from minio import Minio
from pydantic import BaseModel

from excelalchemy.model.abstract import CreateImporterModelT
from excelalchemy.model.abstract import Option
from excelalchemy.model.abstract import UpdateImporterModelT
from excelalchemy.model.excel import ContextT
from excelalchemy.model.excel import ExcelExporterConfig
from excelalchemy.model.excel import ExcelImporterConfig
from excelalchemy.model.excel import ImportMode


@dataclass
class ESMExcelAlchemyImporterConfig(Generic[ContextT]):
    auth_headers: Mapping[str, Any]  # x-authenticated-userid

    primary_keys: list[str] = field(default_factory=list)  # 关键列
    unique_keys: list[str] | None = field(default=None)  # 唯一列，关键列必定唯一，不用重复声明
    # 对于支持 options 的类型字段，可以重新设置字段的 options, 如为人员和组织提供选项.
    key_options: dict[str, list[Option]] | None = field(default=None)

    # 创建模式下，字段的黑白名单。白名单字段必会导出，黑名单必会过滤
    create_whitelist_keys: list[str] = field(default_factory=list)  # 关键列
    create_blacklist_keys: list[str] = field(default_factory=list)  # 关键列

    import_mode: ImportMode = field(default=ImportMode.CREATE)  # 导入模式

    esm_url: str = field(default='http://esm-be:8000')  # esm url
    create_template_id: str | None = field(default=None)  # 创建表单 Screen 的表单id
    update_template_id: str | None = field(default=None)  # 更新表单 Screen 的模版id

    creator: Callable[[dict[str, Any], ContextT | None], Awaitable[Any]] | None = field(default=None)
    updater: Callable[[dict[str, Any], ContextT | None], Awaitable[Any]] | None = field(default=None)
    is_data_exist: Callable[[dict[str, Any], ContextT | None], Awaitable[bool]] | None = field(default=None)
    context: ContextT | None = field(default=None)

    exec_formatter: Callable[[Exception], str] = field(default=str)
    minio: Minio = field(default=None)
    bucket_name: str = field(default='excel')
    url_expires: int = field(default=3600)

    create_screen: ESMScreen | None = field(default=None)
    update_screen: ESMScreen | None = field(default=None)

    def __post_init__(self):
        if self.import_mode == ImportMode.CREATE:
            if self.create_template_id is None:
                raise ValueError('创建模式下，必须指定 create_template_id')
            if self.update_template_id is not None:
                logging.warning('创建模式下，指定 update_template_id 无效')
        if self.import_mode == ImportMode.UPDATE:
            if self.update_template_id is None:
                raise ValueError('更新模式下，必须指定 update_template_id')
            if self.create_template_id is not None:
                logging.warning('更新模式下，指定 create_template_id 无效')
        if self.import_mode == ImportMode.CREATE_OR_UPDATE:
            if self.create_template_id is None or self.update_template_id is None:
                raise ValueError('创建或更新模式下，必须指定 create_template_id 和 update_template_id ')

    def to_excel_importer_config(
        self,
        create_importer: type[CreateImporterModelT] | None,
        update_importer: type[UpdateImporterModelT] | None,
    ) -> ExcelImporterConfig[ContextT, CreateImporterModelT, UpdateImporterModelT]:
        return ExcelImporterConfig[ContextT, Any, Any](
            import_mode=self.import_mode,
            create_importer_model=create_importer,
            update_importer_model=update_importer,
            creator=self.creator,
            updater=self.updater,
            is_data_exist=self.is_data_exist,
            # pyright: reportUnknownMemberType=false
            # pyright: reportUnknownArgumentType=false
            minio=self.minio,
            bucket_name=self.bucket_name,
            exec_formatter=self.exec_formatter,
        )


@dataclass
class ESMExcelAlchemyExporterConfig(Generic[ContextT]):
    auth_headers: Mapping[str, Any]  # x-authenticated-userid
    template_id: str  # 导出 Screen 的表单id

    primary_keys: list[str] = field(default_factory=list)
    unique_keys: list[str] | None = field(default=None)
    key_options: dict[str, list[Option]] | None = field(default=None)

    esm_url: str = field(default='http://esm-be:8000')
    context: ContextT | None = field(default=None)

    minio: Minio = field(default=None)
    bucket_name: str = field(default='excel')
    url_expires: int = field(default=3600)

    def to_excel_exporter_config(self, exporter: type[BaseModel]) -> ExcelExporterConfig[BaseModel]:
        return ExcelExporterConfig[BaseModel](
            exporter_model=exporter,
            minio=self.minio,
            bucket_name=self.bucket_name,
        )
