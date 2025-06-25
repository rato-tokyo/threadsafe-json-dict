"""
ThreadSafeJsonDict - diskcacheを使用したJSON保存機能付き辞書クラス
"""

import json
import threading
from typing import Any, Union, Dict
from pathlib import Path

try:
    import diskcache
except ImportError:
    raise ImportError(
        "diskcacheライブラリが必要です。以下のコマンドでインストールしてください:\n"
        "pip install diskcache"
    )


class ThreadSafeJsonDict:
    """
    diskcacheを使用したJSON保存機能付き辞書クラス

    通常の辞書のように使用でき、save(path)メソッドでJSON形式での保存が可能です。
    設定とsave操作が競合しないよう、スレッドセーフに実装されています。
    """

    def __init__(self, directory: Union[str, Path], size_limit: int = 2**30):  # 1GB
        """
        初期化

        Args:
            directory: diskcache内部ファイル（SQLiteデータベース等）の保存先ディレクトリのパス
                      相対パス・絶対パス両方に対応
            size_limit: キャッシュサイズの上限（バイト）
        """
        # パスを絶対パスに変換（相対パス・絶対パス両方に対応）
        self.directory = Path(directory).resolve()

        # diskcacheのCache作成（内部でSQLiteファイル等が作成される）
        self.cache = diskcache.Cache(str(self.directory), size_limit=size_limit)
        # JSON保存時の排他制御用ロック
        self._save_lock = threading.Lock()

    def __getitem__(self, key: str) -> Any:
        """辞書ライクな読み取り: dict[key]"""
        result = self.cache.get(key)
        if result is None and key not in self.cache:
            raise KeyError(key)
        return result

    def __setitem__(self, key: str, value: Any) -> None:
        """辞書ライクな設定: dict[key] = value"""
        self.cache.set(key, value)

    def __delitem__(self, key: str) -> None:
        """辞書ライクな削除: del dict[key]"""
        if not self.cache.delete(key):
            raise KeyError(key)

    def __contains__(self, key: str) -> bool:
        """in演算子のサポート: key in dict"""
        return key in self.cache

    def __len__(self) -> int:
        """len()のサポート: len(dict)"""
        return len(self.cache)

    def __repr__(self) -> str:
        """文字列表現"""
        return (
            f"ThreadSafeJsonDict(directory='{self.directory}', size={len(self.cache)})"
        )

    def _to_dict(self) -> Dict[str, Any]:
        """内部データを通常の辞書に変換"""
        return {key: self.cache[key] for key in self.cache}

    def save(
        self, path: Union[str, Path], indent: int = 2, ensure_ascii: bool = False
    ) -> None:
        """
        データをJSON形式でファイルに保存

        Args:
            path: 保存先ファイルパス
            indent: JSONのインデント（None で改行なし）
            ensure_ascii: ASCII文字のみ使用するか
        """
        save_path = Path(path)

        # 保存操作の排他制御
        with self._save_lock:
            try:
                # ディレクトリが存在しない場合は作成
                save_path.parent.mkdir(parents=True, exist_ok=True)

                # 現在のデータを辞書として取得
                data_dict = self._to_dict()

                # 一時ファイルに書き込んでから原子的に移動
                temp_path = save_path.with_suffix(".tmp")

                with open(temp_path, "w", encoding="utf-8") as f:
                    json.dump(data_dict, f, indent=indent, ensure_ascii=ensure_ascii)

                # 原子的にファイルを置き換え
                temp_path.replace(save_path)

            except Exception as e:
                # 一時ファイルが残っている場合は削除
                if temp_path.exists():
                    temp_path.unlink()
                raise IOError(f"JSON保存エラー: {e}")

    def load(self, path: Union[str, Path]) -> None:
        """
        JSON形式のファイルからデータを読み込み

        Args:
            path: 読み込み元ファイルパス
        """
        load_path = Path(path)

        if not load_path.exists():
            raise FileNotFoundError(f"ファイルが見つかりません: {load_path}")

        try:
            with open(load_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 既存データをクリアして新しいデータを設定
            self.cache.clear()
            for key, value in data.items():
                self.cache.set(key, value)

        except json.JSONDecodeError as e:
            raise ValueError(f"無効なJSON形式: {e}")
        except Exception as e:
            raise IOError(f"ファイル読み込みエラー: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """辞書のget()メソッド"""
        return self.cache.get(key, default)

    def keys(self):
        """キーの取得"""
        return self.cache.iterkeys()

    def values(self):
        """値の取得"""
        return (self.cache[key] for key in self.cache.iterkeys())

    def items(self):
        """アイテムの取得"""
        return ((key, self.cache[key]) for key in self.cache.iterkeys())

    def __iter__(self):
        """直接反復処理のサポート: for key in dict"""
        return iter(self.cache)

    def clear(self) -> None:
        """すべてのデータをクリア"""
        self.cache.clear()

    def close(self) -> None:
        """リソースを明示的にクローズ"""
        self.cache.close()

    def __enter__(self):
        """コンテキストマネージャーのサポート"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャーのサポート"""
        self.close()
