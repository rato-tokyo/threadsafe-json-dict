"""
テスト用の共通設定
"""

import pytest


@pytest.fixture(autouse=True)
def cleanup_cache_files():
    """
    テスト後にキャッシュファイルを自動クリーンアップ
    """
    yield
    # テスト後のクリーンアップは各テストで個別に実行
