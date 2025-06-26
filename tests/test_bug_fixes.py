#!/usr/bin/env python3
"""
バグ修正の検証テスト

このファイルは、報告されたバグや問題の修正を検証するためのテストを含みます。
新しいバグが報告・修正される度に、対応するテストケースを追加します。
"""

import tempfile
import unittest
from pathlib import Path

from threadsafe_json_dict import ThreadSafeJsonDict


class TestBugFixes(unittest.TestCase):
    """バグ修正の検証テストクラス"""

    def test_isinstance_compatibility_issue_dict(self):
        """
        Bug Fix: isinstance(nested_dict, dict) がFalseになる問題の修正検証
        
        問題: NestedDictProxyが dict を継承していないため、
              isinstance(company_data, dict) がFalseになっていた
        
        修正: NestedDictProxy を dict を継承するように変更し、
              isinstance() チェックがTrueになるようにした
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            json_file = Path(tmpdir) / "test.json"
            data = ThreadSafeJsonDict(json_file)
            
            # ネストした辞書を作成
            data["company"] = {
                "name": "テスト会社",
                "status": "active",
                "metadata": {
                    "version": 1,
                    "settings": {
                        "notifications": True
                    }
                }
            }
            
            # 各レベルのネストした辞書を取得
            company_data = data["company"]
            metadata = company_data["metadata"]
            settings = metadata["settings"]
            
            # isinstance(obj, dict) がすべてTrueになることを確認
            self.assertIsInstance(company_data, dict, 
                                "第1レベルのネストした辞書がdict型として認識されない")
            self.assertIsInstance(metadata, dict,
                                "第2レベルのネストした辞書がdict型として認識されない")
            self.assertIsInstance(settings, dict,
                                "第3レベルのネストした辞書がdict型として認識されない")
            
            # 型チェックも確認
            self.assertEqual(type(company_data).__bases__[0], dict,
                           "NestedDictProxyがdictを継承していない")
            
            # 辞書操作が正常に動作することも確認
            self.assertTrue("name" in company_data)
            self.assertEqual(company_data["name"], "テスト会社")
            self.assertEqual(len(company_data), 3)  # name, status, metadata
            
            # ネストした辞書への変更が正しく追跡されることも確認
            company_data["status"] = "updated"
            metadata["version"] = 2
            settings["notifications"] = False
            
            data.save()
            
            # 変更が保存されているか確認
            data2 = ThreadSafeJsonDict(json_file)
            data2.load()
            
            self.assertEqual(data2["company"]["status"], "updated")
            self.assertEqual(data2["company"]["metadata"]["version"], 2)
            self.assertFalse(data2["company"]["metadata"]["settings"]["notifications"])

    def test_isinstance_compatibility_issue_list(self):
        """
        Bug Fix: isinstance(nested_list, list) がFalseになる問題の修正検証
        
        問題: NestedListProxyが list を継承していないため、
              isinstance(employees_list, list) がFalseになっていた
        
        修正: NestedListProxy を list を継承するように変更し、
              isinstance() チェックがTrueになるようにした
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            json_file = Path(tmpdir) / "test.json"
            data = ThreadSafeJsonDict(json_file)
            
            # ネストしたリストを作成
            data["company"] = {
                "name": "テスト会社",
                "employees": [
                    {"name": "田中", "id": 1},
                    {"name": "佐藤", "id": 2}
                ],
                "departments": [
                    {
                        "name": "開発部",
                        "members": ["田中", "佐藤"]
                    }
                ]
            }
            
            # 各レベルのネストしたリストを取得
            employees_list = data["company"]["employees"]
            departments_list = data["company"]["departments"]
            members_list = departments_list[0]["members"]
            
            # isinstance(obj, list) がすべてTrueになることを確認
            self.assertIsInstance(employees_list, list,
                                "第1レベルのネストしたリストがlist型として認識されない")
            self.assertIsInstance(departments_list, list,
                                "第2レベルのネストしたリストがlist型として認識されない")
            self.assertIsInstance(members_list, list,
                                "第3レベルのネストしたリストがlist型として認識されない")
            
            # 型チェックも確認
            self.assertEqual(type(employees_list).__bases__[0], list,
                           "NestedListProxyがlistを継承していない")
            
            # リスト操作が正常に動作することも確認
            self.assertEqual(len(employees_list), 2)
            self.assertEqual(employees_list[0]["name"], "田中")
            
            # ネストしたリストへの変更が正しく追跡されることも確認
            employees_list.append({"name": "山田", "id": 3})
            members_list.extend(["山田"])
            
            data.save()
            
            # 変更が保存されているか確認
            data2 = ThreadSafeJsonDict(json_file)
            data2.load()
            
            self.assertEqual(len(data2["company"]["employees"]), 3)
            self.assertEqual(data2["company"]["employees"][2]["name"], "山田")
            self.assertIn("山田", data2["company"]["departments"][0]["members"])

    def test_isinstance_with_type_checking_functions(self):
        """
        isinstance() を使用する一般的なパターンでの動作確認
        
        実際のユースケースでisinstance()が期待通りに動作することを確認
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            json_file = Path(tmpdir) / "test.json"
            data = ThreadSafeJsonDict(json_file)
            
            data["mixed_data"] = {
                "dict_value": {"key": "value"},
                "list_value": [1, 2, 3],
                "string_value": "text",
                "int_value": 42,
                "bool_value": True,
                "none_value": None
            }
            
            mixed = data["mixed_data"]
            
            # 型チェック関数のシミュレーション
            def process_value(value):
                """実際のアプリケーションでよくある型チェックパターン"""
                if isinstance(value, dict):
                    return f"辞書: {len(value)}個のキー"
                elif isinstance(value, list):
                    return f"リスト: {len(value)}個の要素"
                elif isinstance(value, bool):  # boolはintのサブクラスなので先にチェック
                    return f"真偽値: {value}"
                elif isinstance(value, int):
                    return f"整数: {value}"
                elif isinstance(value, str):
                    return f"文字列: {value}"
                elif value is None:
                    return "None値"
                else:
                    return f"不明な型: {type(value)}"
            
            # 各値に対して型チェックが正しく動作することを確認
            self.assertEqual(process_value(mixed["dict_value"]), "辞書: 1個のキー")
            self.assertEqual(process_value(mixed["list_value"]), "リスト: 3個の要素")
            self.assertEqual(process_value(mixed["string_value"]), "文字列: text")
            self.assertEqual(process_value(mixed["int_value"]), "整数: 42")
            self.assertEqual(process_value(mixed["bool_value"]), "真偽値: True")
            self.assertEqual(process_value(mixed["none_value"]), "None値")

    def test_isinstance_preserves_functionality(self):
        """
        isinstance() 修正後も既存の機能が正常に動作することを確認
        
        バグ修正により既存機能が破綻していないことを確認
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            json_file = Path(tmpdir) / "test.json"
            data = ThreadSafeJsonDict(json_file)
            
            # 複雑なネスト構造を作成
            data["test"] = {
                "level1": {
                    "level2": {
                        "level3": {
                            "data": [1, 2, {"nested": "value"}]
                        }
                    }
                }
            }
            
            # isinstance() チェックと同時に操作を実行
            level1 = data["test"]["level1"]
            self.assertIsInstance(level1, dict)
            
            level2 = level1["level2"]
            self.assertIsInstance(level2, dict)
            
            level3 = level2["level3"]
            self.assertIsInstance(level3, dict)
            
            data_list = level3["data"]
            self.assertIsInstance(data_list, list)
            
            nested_dict = data_list[2]
            self.assertIsInstance(nested_dict, dict)
            
            # 変更操作
            level3["new_key"] = "new_value"
            data_list.append("new_item")
            nested_dict["new_nested"] = "nested_value"
            
            # 保存・読み込み
            data.save()
            data2 = ThreadSafeJsonDict(json_file)
            data2.load()
            
            # 変更が正しく保存されていることを確認
            self.assertEqual(
                data2["test"]["level1"]["level2"]["level3"]["new_key"], 
                "new_value"
            )
            self.assertEqual(
                data2["test"]["level1"]["level2"]["level3"]["data"][3], 
                "new_item"
            )
            self.assertEqual(
                data2["test"]["level1"]["level2"]["level3"]["data"][2]["new_nested"], 
                "nested_value"
            )


if __name__ == "__main__":
    unittest.main() 