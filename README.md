# ThreadSafeJsonDict

[![PyPI version](https://badge.fury.io/py/threadsafe-json-dict.svg)](https://badge.fury.io/py/threadsafe-json-dict)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**外部依存なしの純粋なPython実装**によるスレッドセーフなJSON保存機能付き辞書クラスです。

## 特徴

- 🔒 **スレッドセーフ**: `threading.RLock()`による安全な並行アクセス
- 💾 **自動JSON保存**: 辞書操作と連動したJSONファイル保存
- 🏗️ **ネスト対応**: ネストした辞書・リストの変更も正しく追跡
- 🔧 **isinstance互換**: `isinstance(obj, dict)`や`isinstance(obj, list)`が正常動作
- 🚀 **外部依存なし**: 標準ライブラリのみを使用
- 📦 **簡単インストール**: `pip install threadsafe-json-dict`

## インストール

```bash
pip install threadsafe-json-dict
```

## 基本的な使用方法

```python
from threadsafe_json_dict import ThreadSafeJsonDict

# JSONファイルパスを指定して初期化
data = ThreadSafeJsonDict("data.json")

# 辞書のように使用
data["user_id"] = 12345
data["settings"] = {
    "theme": "dark",
    "notifications": True
}

# JSONファイルに保存
data.save()

# ファイルから読み込み
data.load()
print(data["user_id"])  # 12345
```

## ネストした辞書・リストの操作

```python
# ネストした辞書への代入（重要な機能）
data["company_123"] = {
    "name": "テスト会社",
    "status": "active",
    "employees": []
}

# ネストした辞書の値を直接変更
company_data = data["company_123"]
company_data["status"] = "processing"  # 正しく追跡される

# ネストしたリストへの操作
employees = company_data["employees"]
employees.append({"id": 1, "name": "田中太郎"})
employees.extend([
    {"id": 2, "name": "佐藤花子"},
    {"id": 3, "name": "山田次郎"}
])

# すべての変更が自動的に元のデータに反映される
data.save()  # 全ての変更がJSONファイルに保存される
```

## isinstance() 互換性

プロキシオブジェクトは元の型として正しく認識されます：

```python
data["config"] = {"key": "value"}
data["items"] = [1, 2, 3]

config = data["config"]
items = data["items"]

# isinstance() チェックが正常に動作
print(isinstance(config, dict))  # True
print(isinstance(items, list))   # True

# 型チェック関数での使用例
def process_value(value):
    if isinstance(value, dict):
        return f"辞書: {len(value)}個のキー"
    elif isinstance(value, list):
        return f"リスト: {len(value)}個の要素"
    else:
        return f"その他: {value}"

print(process_value(config))  # "辞書: 1個のキー"
print(process_value(items))   # "リスト: 3個の要素"
```

## 実際のユースケース例

```python
# 会社データ管理システムの例
companies = ThreadSafeJsonDict("companies.json")

# 初期データ設定
companies["company_123"] = {
    "name": "テクノロジー株式会社",
    "status": "active",
    "employees": [],
    "metadata": {
        "created_at": "2024-01-01",
        "version": 1,
        "settings": {
            "notifications": True,
            "backup_enabled": True
        }
    }
}

# ステータス更新（重要：この操作が正しく追跡される）
companies["company_123"]["status"] = "processing"

# 従業員追加
employees = companies["company_123"]["employees"]
employees.append({
    "id": 1,
    "name": "田中太郎",
    "department": "開発部",
    "hire_date": "2024-01-15"
})

# 設定変更
settings = companies["company_123"]["metadata"]["settings"]
settings["backup_enabled"] = False
settings["auto_save"] = True

# メタデータ更新
companies["company_123"]["metadata"]["version"] = 2
companies["company_123"]["metadata"]["last_updated"] = "2024-01-20"

# 全ての変更を保存
companies.save()

# 別のプロセスで読み込み
companies2 = ThreadSafeJsonDict("companies.json")
companies2.load()
print(companies2["company_123"]["status"])  # "processing"
```

## 並行処理での使用

```python
import threading
from threadsafe_json_dict import ThreadSafeJsonDict

# 共有データ
shared_data = ThreadSafeJsonDict("shared.json")
shared_data["counter"] = 0
shared_data["users"] = {}

def worker_thread(thread_id):
    # スレッドセーフな操作
    shared_data["counter"] += 1
    shared_data["users"][f"user_{thread_id}"] = {
        "id": thread_id,
        "active": True
    }
    shared_data.save()

# 複数スレッドで同時実行
threads = []
for i in range(10):
    t = threading.Thread(target=worker_thread, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print(shared_data["counter"])  # 10
print(len(shared_data["users"]))  # 10
```

## API リファレンス

### ThreadSafeJsonDict

#### 初期化
```python
ThreadSafeJsonDict(json_file_path: str | Path)
```

#### 主要メソッド

- `save(indent=2, ensure_ascii=False)`: データをJSONファイルに保存
- `load(path=None)`: JSONファイルからデータを読み込み
- `get(key, default=None)`: 安全な値取得
- `keys()`, `values()`, `items()`: 辞書メソッド
- `clear()`: 全データクリア

#### プロキシオブジェクト

ネストした辞書やリストは以下のプロキシオブジェクトとして返されます：

- **NestedDictProxy**: `dict`を継承し、辞書操作をすべてサポート
- **NestedListProxy**: `list`を継承し、リスト操作をすべてサポート

両プロキシとも変更を自動的に追跡し、元のデータに反映します。

## バージョン履歴

### v0.2.0 (最新)
- ✅ **isinstance() 互換性の修正**: `isinstance(obj, dict)`や`isinstance(obj, list)`が正常動作
- ✅ **プロキシクラスの改善**: `NestedDictProxy`と`NestedListProxy`が適切な型を継承
- ✅ **バグ対応テストの追加**: `tests/test_bug_fixes.py`でバグ修正の検証
- ✅ **データ同期の強化**: プロキシオブジェクトと元データの完全同期

### v0.1.0
- 初回リリース
- 基本的なスレッドセーフJSON辞書機能
- ネストした辞書・リストの変更追跡

## 開発・テスト

```bash
# リポジトリをクローン
git clone https://github.com/your-username/threadsafe-json-dict.git
cd threadsafe-json-dict

# テスト実行
python -m pytest tests/ -v

# カバレッジ確認
python -m pytest tests/ --cov=threadsafe_json_dict --cov-report=html

# コード品質チェック
ruff check .
black .
mypy threadsafe_json_dict/
```

## バグ報告・機能要求

バグを発見した場合や新機能のご要望は、[GitHub Issues](https://github.com/your-username/threadsafe-json-dict/issues)でお知らせください。

報告されたバグは`tests/test_bug_fixes.py`に検証テストを追加し、修正後の回帰テストとして活用します。

## ライセンス

MIT License - 詳細は[LICENSE](LICENSE)ファイルをご覧ください。

## 貢献

プルリクエストやイシューの報告を歓迎します！開発に参加していただける方は、まずイシューで議論してからプルリクエストを送信してください。