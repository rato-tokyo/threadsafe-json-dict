# ThreadSafeJsonDict 問題レポート

## 概要
ThreadSafeJsonDictライブラリを使用中に、反復処理（iteration）で`AttributeError`が発生しています。

## 発生した問題

### エラーメッセージ
```
AttributeError: 'Cache' object has no attribute 'iteritems'. Did you mean: 'iterkeys'?
```

### エラーが発生するコード
```python
from threadsafe_json_dict import ThreadSafeJsonDict

def main():
    try:
        status_dict = ThreadSafeJsonDict("tmp")
        status_dict.load("json/status.json")
        count = 0
        # この行でエラーが発生
        for key, value in status_dict.items():
            if count >= 10:
                break
            print(f"Key: {key}, Value: {value}")
            count += 1
    finally:
        status_dict.close()
```

### 完全なスタックトレース
```
Traceback (most recent call last):
  File "C:\Users\tomos\Desktop\git\openwork_scraper\main.py", line 65, in <module>
    main()
  File "C:\Users\tomos\Desktop\git\openwork_scraper\main.py", line 54, in main
    for key, value in status_dict.items():
                      ^^^^^^^^^^^^^^^^^^^
  File "C:\Users\tomos\scoop\apps\pyenv\current\pyenv-win\versions\3.11.9\Lib\site-packages\threadsafe_json_
dict\core.py", line 154, in items
    return self.cache.iteritems()
AttributeError: 'Cache' object has no attribute 'iteritems'. Did you mean: 'iterkeys'?
```

## 環境情報

### Python環境
- Python バージョン: 3.11.9
- OS: Windows 10 (win32 10.0.26100)
- シェル: PowerShell

### 依存関係
- threadsafe-json-dict (pip経由でインストール)
- diskcache (ThreadSafeJsonDictの依存関係)

## 試行した解決方法

### 1. 異なる反復処理方法
以下の方法も試しましたが、同様のエラーまたは別のエラーが発生：

```python
# 方法1: 直接反復処理
for key in status_dict:  # KeyError: 0 が発生

# 方法2: enumerate使用
for (index, value) in enumerate(status_dict):  # KeyError: 0 が発生

# 方法3: items()メソッド
for key, value in status_dict.items():  # AttributeError: 'Cache' object has no attribute 'iteritems'
```

## 根本原因の推測

### diskcacheライブラリのバージョン互換性問題
- `iteritems()`メソッドはPython 2.x時代のメソッド名
- 現在のdiskcacheライブラリでは`iteritems()`が廃止されている可能性
- ThreadSafeJsonDictが古いdiskcache APIを使用している

### 具体的な問題箇所
`threadsafe_json_dict/core.py`の154行目：
```python
def items(self):
    return self.cache.iteritems()  # ← この行が問題
```

## 期待する修正内容

### 1. items()メソッドの修正
```python
def items(self):
    # 修正前
    return self.cache.iteritems()
    
    # 修正後（推奨）
    return iter(self.cache.items())
    # または
    return self.cache.items()
```

### 2. 他の反復処理メソッドの確認
以下のメソッドも同様の問題がある可能性があります：
- `keys()` メソッド
- `values()` メソッド
- `__iter__()` メソッド

### 3. diskcacheの現在のAPIに合わせた更新
- `iteritems()` → `items()`
- `iterkeys()` → `keys()`
- `itervalues()` → `values()`

## テストケース

修正後は以下のコードが正常に動作することを確認してください：

```python
from threadsafe_json_dict import ThreadSafeJsonDict

# テストデータ作成
with ThreadSafeJsonDict("test_cache") as data:
    data["key1"] = "value1"
    data["key2"] = {"nested": "data"}
    data["key3"] = [1, 2, 3]

# 反復処理テスト
with ThreadSafeJsonDict("test_cache") as data:
    # items()の動作確認
    print("=== items() テスト ===")
    for key, value in data.items():
        print(f"{key}: {value}")
    
    # keys()の動作確認
    print("=== keys() テスト ===")
    for key in data.keys():
        print(f"Key: {key}")
    
    # values()の動作確認
    print("=== values() テスト ===")
    for value in data.values():
        print(f"Value: {value}")
    
    # 直接反復処理の動作確認
    print("=== 直接反復処理テスト ===")
    for key in data:
        print(f"Key: {key}, Value: {data[key]}")
```

## 緊急度
**高** - 現在、ThreadSafeJsonDictを使用したプロジェクトが動作不能状態です。

## 追加情報
- JSONファイルサイズ: 約4.7MB（26,210件の企業データ）
- 使用目的: マルチプロセス間でのデータ共有とJSON保存
- 代替手段: 現時点で適切な代替ライブラリが見つからない

## 連絡先
この問題の解決が完了しましたら、修正されたバージョンの使用方法をお知らせください。 