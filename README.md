# ThreadSafe JSON Dict

diskcacheライブラリを使用したスレッドセーフなJSON保存機能付き辞書クラスです。

## 特徴

- **辞書ライクなインターフェース**: 通常のPython辞書と同じように使用可能
- **JSON保存機能**: `save(path)`メソッドでJSON形式での保存
- **スレッドセーフ**: 複数スレッドからの同時アクセスに対応
- **プロセスセーフ**: 複数プロセス間での安全なデータ共有
- **SQLiteベース**: diskcacheによる高信頼性のデータ永続化
- **コンテキストマネージャー**: `with`文でのリソース管理

## インストール

```bash
pip install threadsafe-json-dict
```

## 使用方法

### 基本的な使用例

```python
from threadsafe_json_dict import ThreadSafeJsonDict

# 辞書を作成
data = ThreadSafeJsonDict("my_data")

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

# JSON形式で保存
data.save("output/data.json")

# リソースをクリーンアップ
data.close()
```

### コンテキストマネージャーとしての使用

```python
from threadsafe_json_dict import ThreadSafeJsonDict

with ThreadSafeJsonDict("my_data") as data:
    data["key1"] = "value1"
    data["key2"] = {"nested": "data"}
    data.save("output.json")
# 自動的にリソースがクリーンアップされます
```

### JSON読み込み

```python
from threadsafe_json_dict import ThreadSafeJsonDict

# 既存のJSONファイルから読み込み
data = ThreadSafeJsonDict("loaded_data")
data.load("input.json")

# データの確認
for key, value in data.items():
    print(f"{key}: {value}")

data.close()
```

### スレッドセーフな並行処理

```python
import threading
from threadsafe_json_dict import ThreadSafeJsonDict

data = ThreadSafeJsonDict("concurrent_data")

def worker_thread(thread_id):
    for i in range(10):
        data[f"thread_{thread_id}_item_{i}"] = f"value_{i}"
        
    # スレッドセーフな保存
    data.save(f"thread_{thread_id}_output.json")

# 複数スレッドで並行実行
threads = []
for i in range(3):
    t = threading.Thread(target=worker_thread, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print(f"最終データ数: {len(data)}")
data.close()
```

## API リファレンス

### ThreadSafeJsonDict

#### `__init__(directory="threadsafe_json_dict", size_limit=2**30)`

- `directory`: データ保存用ディレクトリのパス
- `size_limit`: キャッシュサイズの上限（バイト、デフォルト: 1GB）

#### 辞書操作メソッド

- `dict[key]`: 値の取得
- `dict[key] = value`: 値の設定  
- `del dict[key]`: 値の削除
- `key in dict`: キーの存在確認
- `len(dict)`: 要素数の取得
- `get(key, default=None)`: デフォルト値付きの取得
- `keys()`: キーのイテレータ
- `values()`: 値のイテレータ
- `items()`: キー・値ペアのイテレータ
- `clear()`: すべてのデータを削除

#### ファイル操作メソッド

- `save(path, indent=2, ensure_ascii=False)`: JSON形式でファイルに保存
- `load(path)`: JSON形式のファイルから読み込み

#### リソース管理

- `close()`: リソースを明示的にクローズ
- `__enter__()` / `__exit__()`: コンテキストマネージャーサポート

## 依存関係

- Python 3.7+
- diskcache >= 5.0.0

## ライセンス

MIT License

## 開発

開発環境のセットアップ:

```bash
git clone https://github.com/yourusername/threadsafe-json-dict.git
cd threadsafe-json-dict
pip install -e ".[dev]"
```

テストの実行:

```bash
pytest
```

コードフォーマット:

```bash
black threadsafe_json_dict/
```