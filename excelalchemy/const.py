from excelalchemy.model.identity import Key
from excelalchemy.model.identity import Label

HEADER_HINT = """
导入填写须知：
1、填写数据时，请注意查看字段名称上的注释，避免导入失败。
2、表格中可能包含部分只读字段，可能是根据系统规则自动生成或是在编辑时禁止被修改，仅用于导出时查看，导入时不生效。
3、字段名称背景是红色的为必填字段，导入时必须根据注释的提示填写好内容。
4、请不要随意修改列的单元格格式，避免模板校验不通过。
5、导入前请删除示例数据。
"""

EXCEL_COMMENT_FORMAT = {'height': 100, 'width': 300, 'font_size': 7}
CHARACTER_WIDTH = 1.3
DEFAULT_SHEET_NAME = 'Sheet1'
# 连接符
UNIQUE_HEADER_CONNECTOR: str = '·'

# 数据导出结果列
RESULT_COLUMN_LABEL: Label = Label('校验结果\n重新上传前请删除此列')
RESULT_COLUMN_KEY: Key = Key('__result__')

# 数据导出原因列
REASON_COLUMN_LABEL: Label = Label('失败原因\n重新上传前请删除此列')
REASON_COLUMN_KEY: Key = Key('__reason__')

BACKGROUND_REQUIRED_COLOR = 'FDAFB5'
BACKGROUND_ERROR_COLOR = 'FEC100'
FONT_READ_COLOR = 'FF0000'

# 多选分隔符
MULTI_CHECKBOX_SEPARATOR = '，'

FIELD_DATA_KEY = Key('fieldData')

# 毫秒转换为秒
MILLISECOND_TO_SECOND = 1000

# options 最多允许的选项数量
MAX_OPTIONS_COUNT = 100

DEFAULT_FIELD_META_ORDER = -1
