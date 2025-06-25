"""
pytest共通フィクスチャ
"""

import tempfile
import pytest
from pathlib import Path

from threadsafe_json_dict import ThreadSafeJsonDict


@pytest.fixture
def temp_dir():
    """一時ディレクトリのフィクスチャ"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def dict_instance(temp_dir):
    """ThreadSafeJsonDictインスタンスのフィクスチャ"""
    instance = ThreadSafeJsonDict(str(temp_dir / "test_dict"))
    yield instance
    try:
        instance.close()
    except:
        pass  # クローズエラーは無視 