"""
ThreadSafeJsonDict の包括的テスト

1つの複雑なJSONファイルとの完全一致で全機能をテストする簡潔なアプローチ
"""

import json
import tempfile
from pathlib import Path

import pytest

from threadsafe_json_dict import ThreadSafeJsonDict


class TestThreadSafeJsonDict:
    """ThreadSafeJsonDictの包括的テスト"""

    def test_comprehensive_functionality(self):
        """
        包括的な機能テスト - 1つの複雑なJSONとの完全一致

        このテストでカバーする機能：
        - 基本的な辞書操作
        - ネストした辞書への代入（バグ修正の確認）
        - 深いネスト構造の変更
        - 複数のデータ型
        - リストの操作
        - JSON保存・読み込み
        """

        with tempfile.TemporaryDirectory() as tmpdir:
            dict_obj = ThreadSafeJsonDict(tmpdir)

            # 1. 初期データ設定（基本的な辞書操作）
            dict_obj["company_123"] = {
                "name": "テスト会社",
                "status": "active",
                "employees": [],
                "metadata": {
                    "created_at": "2024-01-01",
                    "version": 1,
                    "tags": [],
                    "settings": {"notifications": True, "backup_enabled": True},
                },
            }

            dict_obj["company_456"] = {
                "name": "サンプル株式会社",
                "status": "inactive",
                "employees": [],
                "metadata": {
                    "created_at": "2024-01-02",
                    "version": 1,
                    "tags": ["new"],
                    "settings": {"notifications": False, "backup_enabled": True},
                },
            }

            # 2. ネストした辞書への代入（重要：バグ修正の確認）
            dict_obj["company_123"]["status"] = "saving_user_list"
            dict_obj["company_123"]["metadata"]["version"] = 2
            dict_obj["company_123"]["metadata"]["tags"].extend(["important", "active"])
            dict_obj["company_123"]["metadata"]["settings"]["backup_enabled"] = False

            # 3. リストへの要素追加
            dict_obj["company_123"]["employees"].append(
                {"id": 1, "name": "田中太郎", "department": "開発部"}
            )
            dict_obj["company_123"]["employees"].append(
                {"id": 2, "name": "佐藤花子", "department": "営業部"}
            )

            # 4. 別の会社のステータス変更
            dict_obj["company_456"]["status"] = "processing"

            # 5. グローバル設定の追加（深いネスト構造）
            dict_obj["global_config"] = {
                "system_version": "1.0.0",
                "features": {
                    "nested_modification": True,
                    "auto_save": True,
                    "deep_nesting": {
                        "level1": {
                            "level2": {
                                "level3": {
                                    "value": "initial_value",
                                    "timestamp": "2024-01-01T09:00:00",
                                }
                            }
                        }
                    },
                },
                "limits": {"max_companies": 1000, "max_employees_per_company": 500},
            }

            # 6. 深いネストの値変更
            dict_obj["global_config"]["features"]["deep_nesting"]["level1"]["level2"][
                "level3"
            ]["value"] = "deep_value_modified"
            dict_obj["global_config"]["features"]["deep_nesting"]["level1"]["level2"][
                "level3"
            ]["timestamp"] = "2024-01-01T10:00:00"

            # 7. 統計情報の追加
            dict_obj["statistics"] = {
                "total_companies": 2,
                "total_employees": 2,
                "last_updated": "2024-01-01T12:00:00",
                "performance_metrics": {
                    "avg_response_time": 0.05,
                    "cache_hit_rate": 0.95,
                    "error_count": 0,
                },
            }

            # 8. 各種データ型のテスト
            dict_obj["test_data_types"] = {
                "string_value": "テスト文字列",
                "integer_value": 42,
                "float_value": 3.14159,
                "boolean_true": True,
                "boolean_false": False,
                "null_value": None,
                "empty_string": "",
                "empty_list": [],
                "empty_dict": {},
                "unicode_text": "🚀 Unicode テスト 📊",
            }

            # 9. JSONファイルに保存
            output_file = Path(tmpdir) / "test_output.json"
            dict_obj.save(output_file)

            # 10. 正解JSONファイルと比較
            expected_file = (
                Path(__file__).parent
                / "expected_results"
                / "comprehensive_test_expected.json"
            )

            # 保存されたJSONを読み込み
            with open(output_file, encoding="utf-8") as f:
                actual_data = json.load(f)

            # 正解JSONを読み込み
            with open(expected_file, encoding="utf-8") as f:
                expected_data = json.load(f)

            # 完全一致を確認
            assert actual_data == expected_data, (
                f"保存されたJSONが正解と一致しません。\n"
                f"期待値: {json.dumps(expected_data, indent=2, ensure_ascii=False)}\n"
                f"実際値: {json.dumps(actual_data, indent=2, ensure_ascii=False)}"
            )

            # リソースをクリーンアップ
            dict_obj.close()

    def test_load_and_modify_cycle(self):
        """
        JSONファイルの読み込み → 変更 → 保存サイクルのテスト
        """

        with tempfile.TemporaryDirectory() as tmpdir:
            # 正解JSONファイルを読み込み
            expected_file = (
                Path(__file__).parent
                / "expected_results"
                / "comprehensive_test_expected.json"
            )

            # 1. 新しいインスタンスで正解JSONを読み込み
            dict_obj = ThreadSafeJsonDict(tmpdir)
            dict_obj.load(expected_file)

            # 2. 読み込み後に変更を加える
            dict_obj["company_123"]["status"] = "updated_after_load"
            dict_obj["statistics"]["total_companies"] = 3

            # 3. 新しいファイルに保存
            output_file = Path(tmpdir) / "modified_output.json"
            dict_obj.save(output_file)

            # 4. 変更が正しく反映されているか確認
            with open(output_file, encoding="utf-8") as f:
                modified_data = json.load(f)

            assert modified_data["company_123"]["status"] == "updated_after_load"
            assert modified_data["statistics"]["total_companies"] == 3

            # 5. 他のデータは変更されていないことを確認
            assert modified_data["company_456"]["name"] == "サンプル株式会社"
            assert modified_data["global_config"]["system_version"] == "1.0.0"

            dict_obj.close()

    def test_error_cases(self):
        """エラーケースのテスト"""

        with tempfile.TemporaryDirectory() as tmpdir:
            dict_obj = ThreadSafeJsonDict(tmpdir)

            # 存在しないキーへのアクセス
            with pytest.raises(KeyError):
                _ = dict_obj["nonexistent_key"]

            # 存在しないキーの削除
            with pytest.raises(KeyError):
                del dict_obj["nonexistent_key"]

            # 存在しないファイルの読み込み
            with pytest.raises(FileNotFoundError):
                dict_obj.load("nonexistent_file.json")

            dict_obj.close()

    def test_basic_operations(self):
        """基本的な辞書操作のテスト"""

        with tempfile.TemporaryDirectory() as tmpdir:
            dict_obj = ThreadSafeJsonDict(tmpdir)

            # 設定と取得
            dict_obj["key1"] = "value1"
            assert dict_obj["key1"] == "value1"

            # in演算子
            assert "key1" in dict_obj
            assert "key2" not in dict_obj

            # get()メソッド
            assert dict_obj.get("key1") == "value1"
            assert dict_obj.get("key2") is None
            assert dict_obj.get("key2", "default") == "default"

            # len()
            assert len(dict_obj) == 1

            # 削除
            del dict_obj["key1"]
            assert len(dict_obj) == 0

            dict_obj.close()
