import io
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

import pandas

from excelalchemy.const import HEADER_HINT
from tests.registry import FileRegistry


class LocalMockMinio:
    storage: dict[str, Any] = {}
    bucket_name: str = 'test'

    mock_excel_data: dict[str, Any] = {
        FileRegistry.TEST_HEADER_INVALID_INPUT: [
            {
                '不存在的表头': '是',
            },
        ],
        FileRegistry.TEST_BOOLEAN_INPUT: [
            {
                '是否启用': '是',
            },
        ],
        FileRegistry.TEST_DATE_INPUT: [
            {
                '出生日期': '2021-01-01',
            },
        ],
        FileRegistry.TEST_DATE_INPUT_WRONG_FORMAT: [
            {
                '出生日期': '2021-01-32',
            },
        ],
    }

    def __init__(self):
        """generate mock (NamedTemporaryFile) excel files from mock_excel_data

        automatically add HEADER_HINT to first row
        """
        for filename, data in self.mock_excel_data.items():
            f = NamedTemporaryFile(suffix='.xlsx')
            df = pandas.DataFrame(data)
            original_header = df.columns
            df.columns = range(len(df.columns))
            header_row = pandas.Series(original_header, index=df.columns)
            df = pandas.concat([header_row.to_frame().T, df], ignore_index=True)

            df.loc[-1] = None
            df.index = df.index + 1
            df = df.sort_index()
            df.iat[0, 0] = HEADER_HINT

            df.to_excel(f.name, index=False, header=False)
            f.seek(0)
            data = io.BytesIO(f.read())
            f.seek(0)
            length = len(f.read())
            self.put_object(self.bucket_name, filename, data, length, f)

    def put_object(self, bucket_name: str, filename: str, data: io.BytesIO, length: int, file: Any = None) -> None:
        self.storage[filename] = {
            'bucket_name': bucket_name,
            'filename': filename,
            'data': data,
            'length': length,
            'file': file,
        }

    @classmethod
    def presigned_get_object(cls, bucket_name: str, filename: str, expires: int) -> str:
        return f'{bucket_name}/{filename}'

    def get_object(self, bucket_name: str, filename: str) -> io.BytesIO:
        assert bucket_name is not None
        return self.storage[filename]['data']

    def __del__(self):
        for filename, data in self.storage.items():
            data['file'].close()


local_minio = LocalMockMinio()
