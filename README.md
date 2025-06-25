# ThreadSafe JSON Dict

diskcacheライブラリを使用したスレッドセーフなJSON保存機能付き辞書クラスです。

## 特徴

### なぜ必要なのか？
既存のPython辞書やJSONファイル操作では、**スレッド間の競合状態**や**プロセス間でのデータ共有**が困難です。Redis等の外部ツールは設定が複雑で、軽量な用途には過剰です。

### このライブラリの解決策
✅ **ゼロ設定**: 外部サーバー不要、`pip install`だけで使用開始  
✅ **Pythonic API**: 標準辞書と完全互換のインターフェース  
✅ **マルチプロセス対応**: SQLiteベースの堅牢なプロセス間共有  
✅ **JSON互換性**: 標準的なJSON形式での入出力  
✅ **軽量**: 単一の依存関係のみ、最小限のオーバーヘッド  

**複雑な設定なしに、辞書ライクな操作でスレッドセーフ・プロセスセーフなデータ管理を実現。**

### 主な機能
- **辞書ライクなインターフェース**: 通常のPython辞書と同じように使用可能
- **JSON保存機能**: `save(path)`メソッドでJSON形式での保存
- **スレッドセーフ**: 複数スレッドからの同時アクセスに対応
- **プロセスセーフ**: 複数プロセス間での安全なデータ共有
- **SQLiteベース**: diskcacheによる高信頼性のデータ永続化
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

# 辞書を作成（diskcache内部ファイル保存先ディレクトリを指定）
data = ThreadSafeJsonDict("my_data_cache")

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

with ThreadSafeJsonDict("my_data_cache") as data:
    data["key1"] = "value1"
    data["key2"] = {"nested": "data"}
    data.save("output.json")
# 自動的にリソースがクリーンアップされます
```

### JSON読み込み

```python
from threadsafe_json_dict import ThreadSafeJsonDict

# 既存のJSONファイルから読み込み
data = ThreadSafeJsonDict("loaded_data_cache")
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

data = ThreadSafeJsonDict("concurrent_data_cache")

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

#### `__init__(directory, size_limit=2**30)`

- `directory`: diskcache内部ファイル（SQLiteデータベース等）の保存先ディレクトリのパス（**必須**）
  - 相対パス・絶対パス両方に対応
  - 指定したディレクトリに`cache.db`等のファイルが作成される
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

### 開発環境のセットアップ

```bash
git clone https://github.com/yourusername/threadsafe-json-dict.git
cd threadsafe-json-dict
pip install -e ".[dev]"
```

### テストの実行

pytestを使用したシンプルで効率的なテストスイート：

```bash
# 基本テストの実行
python -m pytest

# カバレッジレポート付きテスト
python -m pytest --cov=threadsafe_json_dict --cov-report=term-missing

# 詳細出力
python -m pytest -v
```

### テスト設計思想

- **diskcacheライブラリ自体は信頼できるライブラリとして扱い**、独自実装部分のみテスト
- **pytestとpytest-mock**を活用してシンプルで保守性の高いテストコード
- **モック使用**によるエラーシミュレーションで堅牢性を確保

### テストカバレッジ

現在のテストカバレッジ: **98%**

- **18のテストケース**で核心機能をカバー
- 基本機能、エラーハンドリング、コンテキストマネージャーを含む
- 過度に複雑なテストを避け、実用性を重視した設計

### テスト内容

✅ **基本的な辞書操作** - get/set/delete/len/keys/values/items  
✅ **JSON保存・読み込み機能** - 各種オプション、エラーハンドリング  
✅ **エラーハンドリング** - KeyError、IOError、無効JSON等  
✅ **コンテキストマネージャー** - with文での正常・異常系  
✅ **モック使用エラーシミュレーション** - ファイルアクセスエラー等

### コードフォーマット

```bash
black threadsafe_json_dict/
flake8 threadsafe_json_dict/
mypy threadsafe_json_dict/
```