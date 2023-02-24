# ExcelAlchemy 开发指南

## 1. 项目介绍

* ExcelAlchemy 负责从 Excel 解析用户的输入，转换、生成对应的数据结构，给后端使用。
* ExcelAlchemy 负责将数据验证的
* ExcelAlchemy 负责将后端给定的数据，转换、生成对应的 Excel，给用户下载。

## 2. 核心设计

### 2.1 ABCValueType

负责实现表头的渲染，用户输入值的解析，反向解析，数据验证。

* comment： 用于生成表头的注释
* serialize： 将用户输入在 Excel 的值，转换为 Python 的值。需要注意的类型如时间。
* deserialize： 将 Python 的值，转换为 Excel 的值。如  datatime 转换成 str 类型。
* _validate： 私有方法，对数据进行验证，OptionId/name 的转换逻辑在这里完成。

### 2.2 Writer 文件

负责将捕获到的错误正确的填写到 Excel 的单元表格（cell）中，核心是计算单元格横纵坐标。
注意以下两点即可

* pandas 的横纵坐标从 0 开始，而 openpyxl 的横纵坐标从 1 开始。
* 对于合并的单元格，合并之后，无法再写入值，无法再写入格式，因此一定要先写入值和格式，再合并单元格（对于合并的单元格，本质上值在左上角第一个）。

### 2.3 如何捕捉中文错误

pydantic 支持自定义 validate 函数， 通过不同的 ValueType 实现不同的 validate 函数，从而捕捉不同的错误。


### 2.4 FieldMetaInfo

* 用于描述 Excel 的表头，包括表头的名称，表头的类型，表头的注释，后续很多地方，都会用到这个类。


## 3、重难点解释

### 3.1 如何解析表头是否有合并

这是通过观察 pandas 读取 Excel 时的行为，而得出的结论。

对于有合并的表头，pandas 会将合并的单元格的值，赋值给合并的单元格的第一个单元格，而其他的单元格的值为 None。
因此，我们可以通过判断是否为 None 来判断是否有合并。

### 3.2 如何记录错误

`ExcelCellError` 和 `ExcelRowError` 用于记录错误，其中 `ExcelCellError` 记录单元格错误，`ExcelRowError` 记录行错误。
`ExcelAlchemy.cell_errors` 用于记录单元格错误的横纵坐标信息。
`ExcelAlchemy.row_errors`  用于记录单元格错误的横坐标信息。
