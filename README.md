# ThreadSafe JSON Dict

軽量で高速なスレッドセーフJSON保存機能付き辞書クラスです。外部依存なしの純粋なPython実装。

## 特徴

### なぜ必要なのか？
既存のPython辞書やJSONファイル操作では、**スレッド間の競合状態**や**ネストした辞書への変更追跡**が困難です。Redis等の外部ツールは設定が複雑で、軽量な用途には過剰です。

### このライブラリの解決策
✅ **ゼロ依存**: 外部ライブラリ不要、純粋なPython実装  
✅ **Pythonic API**: 標準辞書と完全互換のインターフェース  
✅ **ネスト操作対応**: 深いネスト構造への変更も正しく追跡  
✅ **JSON互換性**: 標準的なJSON形式での入出力  
✅ **軽量・高速**: 外部依存なし、メモリ内操作による高速化  
✅ **スレッドセーフ**: `threading.RLock`による安全な並行アクセス  

**複雑な設定なしに、辞書ライクな操作でスレッドセーフなデータ管理を実現。**

### 主な機能
- **辞書ライクなインターフェース**: 通常のPython辞書と同じように使用可能
- **ネスト操作の追跡**: `dict[key1][key2] = value`やリスト操作も正しく動作
- **JSON保存機能**: `save()`メソッドでJSON形式での保存
- **スレッドセーフ**: 複数スレッドからの同時アクセスに対応
- **軽量実装**: 外部依存なし、シンプルで理解しやすいコード
- **コンテキストマネージャー**: `with`文でのリソース管理

## インストール

### PyPIからのインストール（推奨）

```bash
pip install threadsafe-json-dict
```

### 開発版のインストール

```bash
git clone https://github.com/yourusername/threadsafe-json-dict.git
cd threadsafe-json-dict
pip install -e .
```

## 使用方法

### 基本的な使用例

```python
from threadsafe_json_dict import ThreadSafeJsonDict

# 辞書を作成（JSONファイルパスを指定）
data = ThreadSafeJsonDict("output/data.json")

# 辞書ライクな操作
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

# データの読み取り
print(data["user_info"])  # {'name': 'Alice', 'age': 30, 'email': 'alice@example.com'}
print(len(data))          # 2

# JSON形式で保存（初期化時に指定したパスに保存）
data.save()
```

### ネストした辞書・リストの操作

```python
from threadsafe_json_dict import ThreadSafeJsonDict

data = ThreadSafeJsonDict("company_data.json")

# 複雑なネスト構造
data["company"] = {
    "name": "テスト会社",
    "employees": [],
    "metadata": {
        "settings": {
            "notifications": True
        }
    }
}

# ネストした辞書への代入（重要：正しく追跡されます）
data["company"]["metadata"]["settings"]["notifications"] = False

# リストへの操作
data["company"]["employees"].append({"name": "田中太郎", "id": 1})
data["company"]["employees"].append({"name": "佐藤花子", "id": 2})

# 変更はすべて追跡され、保存時に反映されます
data.save()
```

### コンテキストマネージャーとしての使用

```python
from threadsafe_json_dict import ThreadSafeJsonDict

with ThreadSafeJsonDict("output.json") as data:
    data["key1"] = "value1"
    data["key2"] = {"nested": "data"}
    data.save()
# 自動的にリソースがクリーンアップされます
```

### JSON読み込み

```python
from threadsafe_json_dict import ThreadSafeJsonDict

# 既存のJSONファイルから読み込み
data = ThreadSafeJsonDict("modified_data.json")
data.load("input.json")  # 別のファイルから読み込み

# データの確認
for key, value in data.items():
    print(f"{key}: {value}")

# 読み込み後の変更も正しく追跡されます
data["new_key"] = "new_value"
data.save()  # modified_data.jsonに保存
```

### スレッドセーフな並行処理

```python
import threading
from threadsafe_json_dict import ThreadSafeJsonDict

data = ThreadSafeJsonDict("concurrent_output.json")

def worker_thread(thread_id):
    for i in range(10):
        data[f"thread_{thread_id}_item_{i}"] = f"value_{i}"
        
    # 保存先を変更してスレッドごとに保存
    data.set_json_file_path(f"thread_{thread_id}_output.json")
    data.save()

# 複数スレッドで並行実行
threads = []
for i in range(3):
    t = threading.Thread(target=worker_thread, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print(f"最終データ数: {len(data)}")
```

### 実際のユースケース例

```python
from threadsafe_json_dict import ThreadSafeJsonDict

# アプリケーション設定の管理
config = ThreadSafeJsonDict("companies_config.json")

# 複数の会社データを管理
config["companies"] = {}

# 会社データの追加
company_id = "company_123"
config["companies"][company_id] = {
    "name": "サンプル会社",
    "status": "active",
    "employees": []
}

# ステータスの更新（ネストした辞書への代入）
config["companies"][company_id]["status"] = "processing"

# 従業員の追加（ネストしたリストへの操作）
config["companies"][company_id]["employees"].append({
    "id": 1,
    "name": "田中太郎",
    "department": "開発部"
})

# すべての変更が追跡され、正しく保存されます
config.save()
```

## API リファレンス

### ThreadSafeJsonDict

#### `__init__(json_file_path: str | Path)`

ThreadSafeJsonDictインスタンスを初期化します。

**パラメータ:**
- `json_file_path`: JSONファイルの保存先パス

**例:**
```python
data = ThreadSafeJsonDict("data.json")
data = ThreadSafeJsonDict(Path("output") / "config.json")
```

#### `save(indent: int = 2, ensure_ascii: bool = False) -> None`

現在のデータを初期化時に指定したJSONファイルに保存します。

**パラメータ:**
- `indent`: JSONインデント（可読性のため）
- `ensure_ascii`: ASCII文字のみで出力するか

**例:**
```python
data.save()
data.save(indent=4)
```

#### `load(path: str | Path | None = None) -> None`

JSONファイルからデータを読み込みます。

**パラメータ:**
- `path`: 読み込み元ファイルパス（省略時は初期化時に指定したパス）

**例:**
```python
data.load()  # 初期化時のパスから読み込み
data.load("other_file.json")  # 別ファイルから読み込み
```

#### `set_json_file_path(new_path: str | Path) -> None`

JSONファイルパスを変更します。

**パラメータ:**
- `new_path`: 新しいJSONファイルパス

**例:**
```python
data.set_json_file_path("new_output.json")
data.save()  # 新しいパスに保存
```

#### `get_json_file_path() -> Path`

現在のJSONファイルパスを取得します。

**戻り値:**
- 現在のJSONファイルパス

**例:**
```python
current_path = data.get_json_file_path()
print(f"現在の保存先: {current_path}")
```

### 辞書操作メソッド

ThreadSafeJsonDictは標準的なPython辞書のすべてのメソッドをサポートしています：

- `get(key, default=None)`: キーの値を取得
- `keys()`: すべてのキーを取得
- `values()`: すべての値を取得
- `items()`: すべてのキー・値ペアを取得
- `update(other)`: 他の辞書でデータを更新
- `pop(key, default=None)`: キーを削除して値を返す
- `setdefault(key, default=None)`: キーが存在しない場合にデフォルト値を設定
- `clear()`: すべてのデータを削除

### プロキシオブジェクト

ネストした辞書やリストは自動的にプロキシオブジェクトでラップされ、変更が追跡されます：

```python
data = ThreadSafeJsonDict("test.json")
data["nested"] = {"inner": {"value": 1}}

# これらの操作はすべて追跡されます
data["nested"]["inner"]["value"] = 2
data["nested"]["new_key"] = "new_value"

# リスト操作も追跡されます
data["list"] = [1, 2, 3]
data["list"].append(4)
data["list"].extend([5, 6])
```

## パフォーマンス

- **メモリ使用量**: 軽量、標準辞書とほぼ同等
- **速度**: 純粋なPython実装による高速動作
- **スレッドセーフティ**: `threading.RLock`による最小限のオーバーヘッド
- **外部依存**: なし（Python標準ライブラリのみ使用）

## ライセンス

MIT License

## 貢献

プルリクエストやイシューの報告を歓迎します。

## 変更履歴

### v0.2.0
- 初期化時にJSONファイルパスを指定する新しいAPI
- `save()`メソッドでパラメータなしでの保存
- パス変更メソッドの追加（`set_json_file_path()`, `get_json_file_path()`）
- `load()`メソッドのオプション引数対応
- 自前実装による外部依存の完全削除
- ネストした辞書・リスト操作の完全サポート
- より直感的なAPI設計

### v0.1.0
- 初回リリース
- 基本的な辞書操作とJSON保存機能