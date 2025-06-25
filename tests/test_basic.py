"""
ThreadSafe JSON Dict の基本機能テスト
"""

import json
import pytest
from pathlib import Path

from threadsafe_json_dict import ThreadSafeJsonDict


class TestBasicOperations:
    """基本的な辞書操作のテスト"""
    
    def test_setitem_getitem(self, dict_instance):
        """設定と取得のテスト"""
        dict_instance["key"] = "value"
        assert dict_instance["key"] == "value"
    
    def test_delitem(self, dict_instance):
        """削除のテスト"""
        dict_instance["key"] = "value"
        del dict_instance["key"]
        with pytest.raises(KeyError):
            _ = dict_instance["key"]
    
    def test_contains(self, dict_instance):
        """存在確認のテスト"""
        dict_instance["key"] = "value"
        assert "key" in dict_instance
        assert "nonexistent" not in dict_instance
    
    def test_len(self, dict_instance):
        """長さのテスト"""
        assert len(dict_instance) == 0
        dict_instance["key1"] = "value1"
        dict_instance["key2"] = "value2"
        assert len(dict_instance) == 2
    
    def test_get_method(self, dict_instance):
        """get()メソッドのテスト"""
        dict_instance["existing"] = "value"
        assert dict_instance.get("existing") == "value"
        assert dict_instance.get("nonexistent") is None
        assert dict_instance.get("nonexistent", "default") == "default"
    
    def test_clear(self, dict_instance):
        """clear()メソッドのテスト"""
        dict_instance["key1"] = "value1"
        dict_instance["key2"] = "value2"
        dict_instance.clear()
        assert len(dict_instance) == 0
    
    def test_keys_values_items(self, dict_instance):
        """keys(), values(), items()のテスト"""
        test_data = {"key1": "value1", "key2": "value2"}
        for key, value in test_data.items():
            dict_instance[key] = value
        
        assert set(dict_instance.keys()) == set(test_data.keys())
        assert set(dict_instance.values()) == set(test_data.values())
        assert set(dict_instance.items()) == set(test_data.items())


class TestSaveLoad:
    """保存・読み込み機能のテスト"""
    
    def test_save_load_basic(self, dict_instance, temp_dir):
        """基本的な保存・読み込みのテスト"""
        test_data = {
            "string": "test",
            "number": 42,
            "list": [1, 2, 3],
            "dict": {"nested": "value"}
        }
        
        for key, value in test_data.items():
            dict_instance[key] = value
        
        save_path = temp_dir / "test.json"
        dict_instance.save(save_path)
        
        # ファイルが作成されたことを確認
        assert save_path.exists()
        
        # 新しいインスタンスで読み込み
        new_instance = ThreadSafeJsonDict(str(temp_dir / "new_dict"))
        try:
            new_instance.load(save_path)
            for key, expected_value in test_data.items():
                assert new_instance[key] == expected_value
        finally:
            new_instance.close()
    
    def test_save_options(self, dict_instance, temp_dir):
        """保存オプションのテスト"""
        dict_instance["test"] = "日本語"
        
        # デフォルト設定
        path1 = temp_dir / "default.json"
        dict_instance.save(path1)
        
        # ensure_ascii=True
        path2 = temp_dir / "ascii.json"
        dict_instance.save(path2, ensure_ascii=True)
        
        # indent=None
        path3 = temp_dir / "compact.json"
        dict_instance.save(path3, indent=None)
        
        # ファイルの内容を確認
        with open(path1, 'r', encoding='utf-8') as f:
            content1 = f.read()
        assert "日本語" in content1
        
        with open(path2, 'r', encoding='utf-8') as f:
            content2 = f.read()
        assert "\\u" in content2  # Unicode エスケープ
        
        with open(path3, 'r', encoding='utf-8') as f:
            content3 = f.read()
        assert content3.count('\n') == 0  # 改行なし
    
    def test_load_invalid_json(self, dict_instance, temp_dir):
        """無効なJSONファイルの読み込みテスト"""
        invalid_file = temp_dir / "invalid.json"
        with open(invalid_file, 'w') as f:
            f.write('{"invalid": json}')
        
        with pytest.raises(ValueError, match="無効なJSON形式"):
            dict_instance.load(invalid_file)
    
    def test_load_nonexistent_file(self, dict_instance):
        """存在しないファイルの読み込みテスト"""
        with pytest.raises(FileNotFoundError):
            dict_instance.load("nonexistent.json")


class TestContextManager:
    """コンテキストマネージャーのテスト"""
    
    def test_context_manager_basic(self, temp_dir):
        """基本的なコンテキストマネージャーのテスト"""
        with ThreadSafeJsonDict(str(temp_dir / "context_test")) as instance:
            instance["test"] = "value"
            assert instance["test"] == "value"
    
    def test_context_manager_exception(self, temp_dir):
        """例外発生時のコンテキストマネージャーのテスト"""
        with pytest.raises(ValueError):
            with ThreadSafeJsonDict(str(temp_dir / "exception_test")) as instance:
                instance["test"] = "value"
                raise ValueError("Test exception")


class TestErrorHandling:
    """エラーハンドリングのテスト"""
    
    def test_keyerror_on_missing_key(self, dict_instance):
        """存在しないキーでのKeyErrorテスト"""
        with pytest.raises(KeyError):
            _ = dict_instance["nonexistent"]
    
    def test_keyerror_on_delete_missing_key(self, dict_instance):
        """存在しないキーの削除でのKeyErrorテスト"""
        with pytest.raises(KeyError):
            del dict_instance["nonexistent"]
    
    def test_save_io_error(self, dict_instance, mocker):
        """保存時のIOErrorテスト"""
        dict_instance["test"] = "data"
        
        # json.dumpでエラーが発生する場合をシミュレート
        mocker.patch('json.dump', side_effect=OSError("Disk full"))
        
        with pytest.raises(IOError, match="JSON保存エラー"):
            dict_instance.save("test.json")
    
    def test_load_permission_error(self, dict_instance, temp_dir, mocker):
        """読み込み時のPermissionErrorテスト"""
        test_file = temp_dir / "permission_test.json"
        with open(test_file, 'w') as f:
            f.write('{"test": "data"}')
        
        mocker.patch('builtins.open', side_effect=PermissionError("Permission denied"))
        
        with pytest.raises(IOError, match="ファイル読み込みエラー"):
            dict_instance.load(test_file)


class TestRepr:
    """文字列表現のテスト"""
    
    def test_repr(self, dict_instance):
        """__repr__メソッドのテスト"""
        dict_instance["test"] = "value"
        repr_str = repr(dict_instance)
        assert "ThreadSafeJsonDict" in repr_str
        assert "size=1" in repr_str 