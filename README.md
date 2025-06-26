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
- **JSON保存機能**: `save(path)`メソッドでJSON形式での保存
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

# 辞書を作成
data = ThreadSafeJsonDict()

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
```

### ネストした辞書・リストの操作

```python
from threadsafe_json_dict import ThreadSafeJsonDict

data = ThreadSafeJsonDict()

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
data.save("company_data.json")
```

### コンテキストマネージャーとしての使用

```python
from threadsafe_json_dict import ThreadSafeJsonDict

with ThreadSafeJsonDict() as data:
    data["key1"] = "value1"
    data["key2"] = {"nested": "data"}
    data.save("output.json")
# 自動的にリソースがクリーンアップされます
```

### JSON読み込み

```python
from threadsafe_json_dict import ThreadSafeJsonDict

# 既存のJSONファイルから読み込み
data = ThreadSafeJsonDict()
data.load("input.json")

# データの確認
for key, value in data.items():
    print(f"{key}: {value}")

# 読み込み後の変更も正しく追跡されます
data["new_key"] = "new_value"
data.save("modified_data.json")
```

### スレッドセーフな並行処理

```python
import threading
from threadsafe_json_dict import ThreadSafeJsonDict

data = ThreadSafeJsonDict()

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
```

### 実際のユースケース例

```python
from threadsafe_json_dict import ThreadSafeJsonDict

# アプリケーション設定の管理
config = ThreadSafeJsonDict()

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
config.save("companies_config.json")
```

## API リファレンス

### ThreadSafeJsonDict

#### `__init__(directory=None)`

- `directory`: 互換性のために残されていますが、自前実装では使用されません

#### 辞書操作メソッド

- `dict[key]`: 値の取得（ネストした辞書・リストはプロキシオブジェクトとして返される）
- `dict[key] = value`: 値の設定  
- `del dict[key]`: 値の削除
- `key in dict`: キーの存在確認
- `len(dict)`: 要素数の取得
- `get(key, default=None)`: デフォルト値付きの取得
- `keys()`: キーのイテレータ
- `values()`: 値のイテレータ（プロキシオブジェクト経由）
- `items()`: キー・値ペアのイテレータ（プロキシオブジェクト経由）
- `clear()`: すべてのデータを削除

#### ネストオブジェクトの操作

ネストした辞書・リストは自動的にプロキシオブジェクト（`NestedDictProxy`、`NestedListProxy`）として返され、以下の操作が追跡されます：

**辞書操作**:
- `nested_dict[key] = value`: 代入
- `del nested_dict[key]`: 削除
- `nested_dict.update(other)`: 更新
- `nested_dict.pop(key)`: 取得と削除
- `nested_dict.setdefault(key, default)`: デフォルト値設定

**リスト操作**:
- `nested_list.append(item)`: 要素追加
- `nested_list.extend(items)`: 複数要素追加
- `nested_list.insert(index, item)`: 指定位置に挿入
- `nested_list.remove(item)`: 要素削除
- `nested_list.pop(index)`: 指定位置の要素取得と削除
- `nested_list[index] = value`: インデックス代入

#### ファイル操作メソッド

- `save(path, indent=2, ensure_ascii=False)`: JSON形式でファイルに保存
- `load(path)`: JSON形式のファイルから読み込み

#### リソース管理

- `close()`: リソースクリーンアップ（自前実装では何もしません）
- `__enter__()` / `__exit__()`: コンテキストマネージャーサポート

## バージョン履歴

### v0.2.0 (最新)
- **重要**: diskcacheから自前実装に完全移行
- ✅ 外部依存を完全削除（`dependencies = []`）
- ✅ ネストしたリスト操作のサポート追加
- ✅ パフォーマンス向上（メモリ内操作）
- ✅ Windowsでのファイルロック問題を解消
- ✅ より直感的で理解しやすいコード

### v0.1.x
- diskcacheベースの初期実装
- ネストした辞書への代入バグが存在

## 依存関係

- Python 3.8+
- **外部依存なし** (Pure Python実装)

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

```bash
# 基本テストの実行
python -m pytest

# カバレッジレポート付きテスト
python -m pytest --cov=threadsafe_json_dict --cov-report=term-missing

# 詳細出力
python -m pytest -v
```

### テスト構造

シンプルで効率的なテスト設計：
- `tests/test_basic.py`: 4つの包括的テスト
- `tests/expected_results/comprehensive_test_expected.json`: 正解JSON
- JSONファイルとの完全一致による品質保証

## トラブルシューティング

### よくある質問

**Q: ネストした辞書への代入が反映されません**  
A: v0.2.0で修正済みです。`dict[key1][key2] = value`形式の操作が正しく動作します。

**Q: リストの操作が保存されません**  
A: v0.2.0で`NestedListProxy`を追加し、`append()`, `extend()`等の操作が正しく追跡されます。

**Q: マルチプロセス対応はありますか？**  
A: 現在の自前実装はスレッドセーフですが、プロセス間共有は対応していません。必要に応じて将来のバージョンで検討します。

**Q: パフォーマンスはどうですか？**  
A: diskcacheのオーバーヘッドを排除し、メモリ内操作により大幅に高速化されました。