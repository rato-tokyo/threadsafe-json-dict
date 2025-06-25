"""
ThreadSafe JSON Dict - diskcacheライブラリを使用したスレッドセーフなJSON保存機能付き辞書

特徴:
- 辞書ライクなインターフェース
- save(path)メソッドでJSON形式保存
- 競合状態の自動回避（スレッドセーフ・プロセスセーフ）
- SQLiteベースの高信頼性
"""

from .core import ThreadSafeJsonDict

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__all__ = ["ThreadSafeJsonDict"]
