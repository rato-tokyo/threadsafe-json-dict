"""
ThreadSafeJsonDict - 自前実装によるJSON保存機能付き辞書クラス
"""

from __future__ import annotations

import copy
import json
import threading
from pathlib import Path
from typing import Any


class NestedListProxy:
    """
    ネストしたリストの変更を追跡するプロキシクラス
    """

    def __init__(self, data: list, parent: ThreadSafeJsonDict, root_key: str):
        self._data = data
        self._parent = parent
        self._root_key = root_key

    def __getitem__(self, index: int) -> Any:
        value = self._data[index]
        if isinstance(value, dict):
            return NestedDictProxy(value, self._parent, self._root_key)
        elif isinstance(value, list):
            return NestedListProxy(value, self._parent, self._root_key)
        return value

    def __setitem__(self, index: int, value: Any) -> None:
        self._data[index] = value

    def __delitem__(self, index: int) -> None:
        del self._data[index]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self):
        for item in self._data:
            if isinstance(item, dict):
                yield NestedDictProxy(item, self._parent, self._root_key)
            elif isinstance(item, list):
                yield NestedListProxy(item, self._parent, self._root_key)
            else:
                yield item

    def __repr__(self) -> str:
        return f"NestedListProxy({self._data})"

    def append(self, value: Any) -> None:
        """リストのappend()メソッド"""
        self._data.append(value)

    def extend(self, values) -> None:
        """リストのextend()メソッド"""
        self._data.extend(values)

    def insert(self, index: int, value: Any) -> None:
        """リストのinsert()メソッド"""
        self._data.insert(index, value)

    def remove(self, value: Any) -> None:
        """リストのremove()メソッド"""
        self._data.remove(value)

    def pop(self, index: int = -1) -> Any:
        """リストのpop()メソッド"""
        result = self._data.pop(index)
        return result

    def clear(self) -> None:
        """リストのclear()メソッド"""
        self._data.clear()


class NestedDictProxy:
    """
    ネストした辞書の変更を追跡するプロキシクラス
    """

    def __init__(self, data: dict, parent: ThreadSafeJsonDict, root_key: str):
        self._data = data
        self._parent = parent
        self._root_key = root_key

    def __getitem__(self, key: str) -> Any:
        value = self._data[key]
        if isinstance(value, dict):
            return NestedDictProxy(value, self._parent, self._root_key)
        elif isinstance(value, list):
            return NestedListProxy(value, self._parent, self._root_key)
        return value

    def __setitem__(self, key: str, value: Any) -> None:
        """ネストした辞書への代入"""
        self._data[key] = value

    def __delitem__(self, key: str) -> None:
        """ネストした辞書からの削除"""
        del self._data[key]

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __repr__(self) -> str:
        return f"NestedDictProxy({self._data})"

    def get(self, key: str, default: Any = None) -> Any:
        value = self._data.get(key, default)
        if isinstance(value, dict) and value is not default:
            return NestedDictProxy(value, self._parent, self._root_key)
        elif isinstance(value, list) and value is not default:
            return NestedListProxy(value, self._parent, self._root_key)
        return value

    def keys(self):
        return self._data.keys()

    def values(self):
        for value in self._data.values():
            if isinstance(value, dict):
                yield NestedDictProxy(value, self._parent, self._root_key)
            elif isinstance(value, list):
                yield NestedListProxy(value, self._parent, self._root_key)
            else:
                yield value

    def items(self):
        for key, value in self._data.items():
            if isinstance(value, dict):
                yield key, NestedDictProxy(value, self._parent, self._root_key)
            elif isinstance(value, list):
                yield key, NestedListProxy(value, self._parent, self._root_key)
            else:
                yield key, value

    def update(self, other: dict[str, Any]) -> None:
        """辞書のupdate()メソッド"""
        self._data.update(other)

    def pop(self, key: str, *args) -> Any:
        """辞書のpop()メソッド"""
        if len(args) > 1:
            raise TypeError(f"pop expected at most 2 arguments, got {len(args) + 1}")

        if len(args) == 0:
            if key not in self._data:
                raise KeyError(key)
            result = self._data.pop(key)
        else:
            result = self._data.pop(key, args[0])

        return result

    def setdefault(self, key: str, default: Any = None) -> Any:
        """辞書のsetdefault()メソッド"""
        if key not in self._data:
            self._data[key] = default
        value = self._data[key]
        if isinstance(value, dict):
            return NestedDictProxy(value, self._parent, self._root_key)
        elif isinstance(value, list):
            return NestedListProxy(value, self._parent, self._root_key)
        return value


class ThreadSafeJsonDict:
    """
    JSON保存機能付き辞書クラス（自前実装版）

    通常の辞書のように使用でき、save(path)メソッドでJSON形式での保存が可能です。
    設定とsave操作が競合しないよう、スレッドセーフに実装されています。
    ネストした辞書・リストへの操作も正しく追跡されます。
    """

    def __init__(self, json_file_path: str | Path):
        """
        初期化

        Args:
            json_file_path: JSONファイルの保存先パス
        """
        # JSONファイルパス
        self._json_file_path = Path(json_file_path)

        # 内部データストレージ
        self._data: dict[str, Any] = {}

        # スレッドセーフティ用のロック
        self._lock = threading.RLock()

    def __getitem__(self, key: str) -> Any:
        """辞書ライクな読み取り: dict[key]"""
        with self._lock:
            if key not in self._data:
                raise KeyError(key)

            value = self._data[key]
            if isinstance(value, dict):
                return NestedDictProxy(value, self, key)
            elif isinstance(value, list):
                return NestedListProxy(value, self, key)
            return value

    def __setitem__(self, key: str, value: Any) -> None:
        """辞書ライクな設定: dict[key] = value"""
        with self._lock:
            self._data[key] = copy.deepcopy(value)

    def __delitem__(self, key: str) -> None:
        """辞書ライクな削除: del dict[key]"""
        with self._lock:
            if key not in self._data:
                raise KeyError(key)
            del self._data[key]

    def __contains__(self, key: str) -> bool:
        """存在確認: key in dict"""
        with self._lock:
            return key in self._data

    def __len__(self) -> int:
        """長さ取得: len(dict)"""
        with self._lock:
            return len(self._data)

    def __repr__(self) -> str:
        """文字列表現"""
        with self._lock:
            return f"ThreadSafeJsonDict({dict(self._data)})"

    def _to_dict(self) -> dict[str, Any]:
        """
        内部データを通常の辞書として取得
        JSON保存時に使用
        """
        with self._lock:
            return copy.deepcopy(self._data)

    def save(self, indent: int = 2, ensure_ascii: bool = False) -> None:
        """
        現在のデータをJSONファイルに保存

        Args:
            indent: JSONインデント（可読性のため）
            ensure_ascii: ASCII文字のみで出力するか
        """
        with self._lock:
            # 内部データを取得
            data_to_save = self._to_dict()

            # ディレクトリが存在しない場合は作成
            self._json_file_path.parent.mkdir(parents=True, exist_ok=True)

            # JSONファイルに保存
            with open(self._json_file_path, "w", encoding="utf-8") as f:
                json.dump(
                    data_to_save,
                    f,
                    indent=indent,
                    ensure_ascii=ensure_ascii,
                    separators=(",", ": "),
                )

    def load(self, path: str | Path | None = None) -> None:
        """
        JSONファイルからデータを読み込み

        Args:
            path: 読み込み元ファイルパス（省略時は初期化時に指定したパス）

        Raises:
            FileNotFoundError: ファイルが存在しない場合
            ValueError: 無効なJSON形式の場合
        """
        load_path = Path(path) if path is not None else self._json_file_path

        if not load_path.exists():
            raise FileNotFoundError(f"ファイルが見つかりません: {load_path}")

        try:
            with open(load_path, encoding="utf-8") as f:
                loaded_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"無効なJSON形式です: {e}")

        with self._lock:
            # 既存データをクリアして新しいデータを設定
            self._data.clear()
            if isinstance(loaded_data, dict):
                self._data.update(loaded_data)
            else:
                raise ValueError("JSONのルートは辞書である必要があります")

    def set_json_file_path(self, new_path: str | Path) -> None:
        """
        JSONファイルパスを変更

        Args:
            new_path: 新しいJSONファイルパス
        """
        with self._lock:
            self._json_file_path = Path(new_path)

    def get_json_file_path(self) -> Path:
        """
        現在のJSONファイルパスを取得

        Returns:
            現在のJSONファイルパス
        """
        return self._json_file_path

    def get(self, key: str, default: Any = None) -> Any:
        """
        安全な値取得: dict.get(key, default)
        """
        with self._lock:
            if key not in self._data:
                return default

            value = self._data[key]
            if isinstance(value, dict):
                return NestedDictProxy(value, self, key)
            elif isinstance(value, list):
                return NestedListProxy(value, self, key)
            return value

    def keys(self):
        """キー一覧取得"""
        with self._lock:
            return self._data.keys()

    def values(self):
        """値一覧取得（プロキシ経由）"""
        with self._lock:
            for key, value in self._data.items():
                if isinstance(value, dict):
                    yield NestedDictProxy(value, self, key)
                elif isinstance(value, list):
                    yield NestedListProxy(value, self, key)
                else:
                    yield value

    def items(self):
        """キー・値ペア一覧取得（プロキシ経由）"""
        with self._lock:
            for key, value in self._data.items():
                if isinstance(value, dict):
                    yield key, NestedDictProxy(value, self, key)
                elif isinstance(value, list):
                    yield key, NestedListProxy(value, self, key)
                else:
                    yield key, value

    def __iter__(self):
        """イテレーション: for key in dict"""
        with self._lock:
            return iter(self._data)

    def clear(self) -> None:
        """全データクリア"""
        with self._lock:
            self._data.clear()

    # コンテキストマネージャー対応
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        pass
