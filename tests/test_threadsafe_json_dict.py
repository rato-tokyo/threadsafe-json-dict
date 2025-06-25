"""
ThreadSafe JSON Dict のテストケース
"""

import json
import tempfile
import threading
import time
import unittest
from pathlib import Path

from threadsafe_json_dict import ThreadSafeJsonDict


class TestThreadSafeJsonDict(unittest.TestCase):
    """ThreadSafeJsonDict のテストケース"""
    
    def setUp(self):
        """テストケースのセットアップ"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_dir = Path(self.temp_dir) / "test_dict"
        self.dict_instance = ThreadSafeJsonDict(str(self.test_dir))
    
    def tearDown(self):
        """テストケースのクリーンアップ"""
        self.dict_instance.close()
    
    def test_basic_operations(self):
        """基本的な辞書操作のテスト"""
        # 設定
        self.dict_instance["key1"] = "value1"
        self.dict_instance["key2"] = {"nested": "data"}
        
        # 取得
        self.assertEqual(self.dict_instance["key1"], "value1")
        self.assertEqual(self.dict_instance["key2"], {"nested": "data"})
        
        # 存在確認
        self.assertIn("key1", self.dict_instance)
        self.assertNotIn("nonexistent", self.dict_instance)
        
        # 長さ
        self.assertEqual(len(self.dict_instance), 2)
        
        # 削除
        del self.dict_instance["key1"]
        self.assertEqual(len(self.dict_instance), 1)
        self.assertNotIn("key1", self.dict_instance)
    
    def test_get_method(self):
        """get()メソッドのテスト"""
        self.dict_instance["existing"] = "value"
        
        # 存在するキー
        self.assertEqual(self.dict_instance.get("existing"), "value")
        
        # 存在しないキー
        self.assertIsNone(self.dict_instance.get("nonexistent"))
        
        # デフォルト値
        self.assertEqual(self.dict_instance.get("nonexistent", "default"), "default")
    
    def test_save_load(self):
        """save/loadメソッドのテスト"""
        # データを設定
        test_data = {
            "string": "test",
            "number": 42,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "japanese": "日本語テスト"
        }
        
        for key, value in test_data.items():
            self.dict_instance[key] = value
        
        # 保存
        save_path = Path(self.temp_dir) / "test_save.json"
        self.dict_instance.save(save_path)
        
        # ファイルが作成されたことを確認
        self.assertTrue(save_path.exists())
        
        # JSONファイルの内容を確認
        with open(save_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data, test_data)
        
        # 新しいインスタンスで読み込み
        new_dict = ThreadSafeJsonDict(str(self.test_dir) + "_new")
        try:
            new_dict.load(save_path)
            
            # データが正しく読み込まれたことを確認
            for key, expected_value in test_data.items():
                self.assertEqual(new_dict[key], expected_value)
        finally:
            new_dict.close()
    
    def test_context_manager(self):
        """コンテキストマネージャーのテスト"""
        with ThreadSafeJsonDict(str(self.test_dir) + "_context") as dict_cm:
            dict_cm["test"] = "value"
            self.assertEqual(dict_cm["test"], "value")
        # close()が自動的に呼ばれることを確認（例外が発生しないこと）
    
    def test_concurrent_access(self):
        """並行アクセスのテスト"""
        num_threads = 5
        items_per_thread = 10
        
        def writer_thread(thread_id):
            for i in range(items_per_thread):
                key = f"thread_{thread_id}_item_{i}"
                value = f"value_{thread_id}_{i}"
                self.dict_instance[key] = value
                time.sleep(0.001)  # 少し待機
        
        # 複数スレッドを起動
        threads = []
        for i in range(num_threads):
            t = threading.Thread(target=writer_thread, args=(i,))
            threads.append(t)
            t.start()
        
        # すべてのスレッドの完了を待機
        for t in threads:
            t.join()
        
        # 期待される総数を確認
        expected_total = num_threads * items_per_thread
        self.assertEqual(len(self.dict_instance), expected_total)
        
        # データの整合性を確認
        for thread_id in range(num_threads):
            for item_id in range(items_per_thread):
                key = f"thread_{thread_id}_item_{item_id}"
                expected_value = f"value_{thread_id}_{item_id}"
                self.assertEqual(self.dict_instance[key], expected_value)
    
    def test_concurrent_save(self):
        """並行保存のテスト"""
        # データを設定
        for i in range(10):
            self.dict_instance[f"key_{i}"] = f"value_{i}"
        
        save_count = 5
        
        def save_thread(save_id):
            save_path = Path(self.temp_dir) / f"concurrent_save_{save_id}.json"
            self.dict_instance.save(save_path)
            return save_path
        
        # 複数スレッドで並行保存
        threads = []
        for i in range(save_count):
            t = threading.Thread(target=save_thread, args=(i,))
            threads.append(t)
            t.start()
        
        # すべてのスレッドの完了を待機
        for t in threads:
            t.join()
        
        # すべてのファイルが正しく作成されたことを確認
        for i in range(save_count):
            save_path = Path(self.temp_dir) / f"concurrent_save_{i}.json"
            self.assertTrue(save_path.exists())
            
            # ファイルの内容を確認
            with open(save_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 期待されるデータ数
            self.assertEqual(len(data), 10)
    
    def test_error_handling(self):
        """エラーハンドリングのテスト"""
        # 存在しないキーへのアクセス
        with self.assertRaises(KeyError):
            _ = self.dict_instance["nonexistent"]
        
        # 存在しないキーの削除
        with self.assertRaises(KeyError):
            del self.dict_instance["nonexistent"]
        
        # 存在しないファイルの読み込み
        with self.assertRaises(FileNotFoundError):
            self.dict_instance.load("nonexistent_file.json")
    
    def test_clear(self):
        """clear()メソッドのテスト"""
        # データを設定
        self.dict_instance["key1"] = "value1"
        self.dict_instance["key2"] = "value2"
        self.assertEqual(len(self.dict_instance), 2)
        
        # クリア
        self.dict_instance.clear()
        self.assertEqual(len(self.dict_instance), 0)
        self.assertNotIn("key1", self.dict_instance)
        self.assertNotIn("key2", self.dict_instance)


if __name__ == "__main__":
    unittest.main() 