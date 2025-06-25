"""
pytest共通フィクスチャ
"""

import tempfile
import pytest
import shutil
from pathlib import Path

from threadsafe_json_dict import ThreadSafeJsonDict


@pytest.fixture
def temp_dir():
    """一時ディレクトリのフィクスチャ"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def test_cache_dir():
    """プロジェクト直下のテスト用キャッシュディレクトリのフィクスチャ"""
    # プロジェクトルートディレクトリを取得
    project_root = Path(__file__).parent.parent
    cache_dir = project_root / "test_cache"

    # テスト前にディレクトリをクリーンアップ
    if cache_dir.exists():
        shutil.rmtree(cache_dir)

    yield cache_dir

    # テスト後のクリーンアップを削除（ディレクトリを残す）
    # if cache_dir.exists():
    #     shutil.rmtree(cache_dir)


@pytest.fixture
def dict_instance(test_cache_dir):
    """ThreadSafeJsonDictインスタンスのフィクスチャ"""
    instance = ThreadSafeJsonDict(str(test_cache_dir))
    yield instance
    try:
        instance.close()
    except:
        pass  # クローズエラーは無視
