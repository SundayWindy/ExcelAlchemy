from typing import Any


class LocalMockMinio:
    storage: dict[str, Any] = {}

    def put_object(self, bucket_name: str, filename: str, data: bytes, length: int) -> None:
        self.storage[filename] = {
            "bucket_name": bucket_name,
            "filename": filename,
            "data": data,
            "length": length,
        }

    def get_object(self, bucket_name: str, filename: str) -> dict[str, Any]:
        assert bucket_name is not None
        return self.storage[filename]
