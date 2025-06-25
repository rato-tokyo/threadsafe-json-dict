"""
ThreadSafe JSON Dict - 基本的な使用例
"""

from threadsafe_json_dict import ThreadSafeJsonDict


def main():
    """基本的な使用例のデモンストレーション"""
    
    # JSON保存機能付き辞書を作成
    with ThreadSafeJsonDict("example_data") as data:
        print("=== 基本的な使用例 ===")
        
        # 辞書ライクな設定
        data["user_info"] = {
            "name": "Alice",
            "age": 30,
            "email": "alice@example.com"
        }
        data["settings"] = {
            "theme": "dark",
            "notifications": True,
            "language": "ja"
        }
        data["numbers"] = [1, 2, 3, 4, 5]
        data["message"] = "Hello, World! 日本語もOK"
        
        print("データを設定しました")
        
        # 辞書ライクな読み取り
        print(f"ユーザー情報: {data['user_info']}")
        print(f"設定: {data['settings']}")
        
        # JSON形式で保存
        data.save("output/data.json")
        print("JSONファイルに保存しました")
        
        # データを変更
        data["user_info"]["age"] = 31
        data["new_field"] = "追加されたデータ"
        
        # 別のファイルに保存
        data.save("output/updated_data.json")
        
        # 保存されたファイルの内容を確認
        print("\n=== 保存されたJSONファイルの内容 ===")
        try:
            with open("output/data.json", 'r', encoding='utf-8') as f:
                print(f.read())
        except FileNotFoundError:
            print("ファイルが見つかりません")


def demo_load_save():
    """load/save機能のデモ"""
    print("\n=== load/save機能デモ ===")
    
    # 新しい辞書を作成
    with ThreadSafeJsonDict("demo1") as data1:
        # データを設定して保存
        data1["config"] = {"version": "1.0", "debug": True}
        data1["users"] = ["Alice", "Bob", "Charlie"]
        data1.save("demo_data.json")
        print("data1でデータを保存しました")
    
    # 別の辞書インスタンスで読み込み
    with ThreadSafeJsonDict("demo2") as data2:
        data2.load("demo_data.json")
        
        print(f"data2で読み込んだデータ: config = {data2['config']}")
        print(f"data2で読み込んだデータ: users = {data2['users']}")
        
        # データを変更して別名で保存
        data2["config"]["version"] = "1.1"
        data2["new_feature"] = "added in v1.1"
        data2.save("demo_data_v1.1.json")
        
        print("更新されたデータを別ファイルに保存しました")


def test_issue_report_scenario():
    """問題レポートで報告されたシナリオのテスト"""
    print("\n=== 問題レポート対応テスト ===")
    
    # テストデータ作成
    with ThreadSafeJsonDict("test_cache") as data:
        data["key1"] = "value1"
        data["key2"] = {"nested": "data"}
        data["key3"] = [1, 2, 3]
        # さらにデータを追加（問題レポートのような大量データを模擬）
        for i in range(20):
            data[f"company_{i}"] = {
                "name": f"会社{i}",
                "rating": 4.0 + (i % 10) * 0.1,
                "employees": 100 + i * 10
            }
    
    # 反復処理テスト（問題レポートのシナリオ）
    with ThreadSafeJsonDict("test_cache") as status_dict:
        try:
            count = 0
            print("=== items() 反復処理テスト ===")
            for key, value in status_dict.items():
                if count >= 10:
                    break
                print(f"Key: {key}, Value: {value}")
                count += 1
            print(f"✓ items()による反復処理成功: {count}件処理")
            
            # keys()の動作確認
            print("\n=== keys() 反復処理テスト ===")
            key_count = 0
            for key in status_dict.keys():
                if key_count >= 5:
                    break
                print(f"Key: {key}")
                key_count += 1
            print(f"✓ keys()による反復処理成功: {key_count}件処理")
            
            # values()の動作確認
            print("\n=== values() 反復処理テスト ===")
            value_count = 0
            for value in status_dict.values():
                if value_count >= 5:
                    break
                print(f"Value: {value}")
                value_count += 1
            print(f"✓ values()による反復処理成功: {value_count}件処理")
            
            # 直接反復処理の動作確認
            print("\n=== 直接反復処理テスト ===")
            direct_count = 0
            for key in status_dict:
                if direct_count >= 5:
                    break
                print(f"Key: {key}, Value: {status_dict[key]}")
                direct_count += 1
            print(f"✓ 直接反復処理成功: {direct_count}件処理")
            
            # enumerate使用テスト
            print("\n=== enumerate反復処理テスト ===")
            for index, key in enumerate(status_dict):
                if index >= 3:
                    break
                print(f"Index: {index}, Key: {key}, Value: {status_dict[key]}")
            print("✓ enumerate使用反復処理成功")
            
        except Exception as e:
            print(f"❌ エラー発生: {e}")
            raise
        finally:
            print("✓ すべての反復処理テスト完了")


if __name__ == "__main__":
    main()
    demo_load_save()
    test_issue_report_scenario() 