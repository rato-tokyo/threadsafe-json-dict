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


if __name__ == "__main__":
    main()
    demo_load_save() 