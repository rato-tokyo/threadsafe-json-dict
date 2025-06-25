"""
ThreadSafe JSON Dict - 並行処理の使用例
"""

import threading
import time
from threadsafe_json_dict import ThreadSafeJsonDict


def demo_concurrent_access():
    """並行アクセスのデモ（スレッドセーフテスト）"""
    print("=== 並行アクセステスト ===")
    
    with ThreadSafeJsonDict("concurrent_test") as data:
        
        def writer_thread(thread_id: int):
            """書き込みスレッド"""
            for i in range(10):
                data[f"thread_{thread_id}_item_{i}"] = f"value_{i}"
                time.sleep(0.01)  # 少し待機
        
        def save_thread():
            """保存スレッド"""
            for i in range(5):
                time.sleep(0.05)
                data.save(f"concurrent_save_{i}.json")
                print(f"保存完了: concurrent_save_{i}.json")
        
        # 複数スレッドで並行実行
        threads = []
        
        # 書き込みスレッドを3つ起動
        for i in range(3):
            t = threading.Thread(target=writer_thread, args=(i,))
            threads.append(t)
            t.start()
        
        # 保存スレッドを起動
        save_t = threading.Thread(target=save_thread)
        threads.append(save_t)
        save_t.start()
        
        # すべてのスレッドの完了を待機
        for t in threads:
            t.join()
        
        print(f"並行アクセステスト完了。最終データ数: {len(data)}")
        
        # 最終状態を保存
        data.save("final_concurrent_result.json")


def demo_producer_consumer():
    """プロデューサー・コンシューマーパターンのデモ"""
    print("\n=== プロデューサー・コンシューマーパターン ===")
    
    with ThreadSafeJsonDict("producer_consumer") as queue_dict:
        
        def producer(producer_id: int):
            """データを生成するスレッド"""
            for i in range(5):
                item_key = f"producer_{producer_id}_item_{i}"
                item_data = {
                    "id": i,
                    "producer": producer_id,
                    "timestamp": time.time(),
                    "data": f"データ_{i}"
                }
                queue_dict[item_key] = item_data
                print(f"Producer {producer_id}: {item_key} を生成")
                time.sleep(0.1)
        
        def consumer(consumer_id: int):
            """データを消費するスレッド"""
            consumed_count = 0
            start_time = time.time()
            
            while time.time() - start_time < 2.0:  # 2秒間実行
                keys_to_process = list(queue_dict.keys())
                
                for key in keys_to_process:
                    if key.startswith("producer_"):
                        try:
                            item = queue_dict[key]
                            del queue_dict[key]  # 処理済みアイテムを削除
                            print(f"Consumer {consumer_id}: {key} を処理 - {item['data']}")
                            consumed_count += 1
                            break
                        except KeyError:
                            # 他のコンシューマーが既に処理済み
                            continue
                
                time.sleep(0.05)
            
            print(f"Consumer {consumer_id}: 合計 {consumed_count} 個のアイテムを処理")
        
        # プロデューサーとコンシューマーを起動
        threads = []
        
        # プロデューサーを2つ起動
        for i in range(2):
            t = threading.Thread(target=producer, args=(i,))
            threads.append(t)
            t.start()
        
        # コンシューマーを3つ起動
        for i in range(3):
            t = threading.Thread(target=consumer, args=(i,))
            threads.append(t)
            t.start()
        
        # すべてのスレッドの完了を待機
        for t in threads:
            t.join()
        
        print(f"処理完了。残りアイテム数: {len(queue_dict)}")
        
        # 残りのデータを保存
        if len(queue_dict) > 0:
            queue_dict.save("remaining_items.json")
            print("未処理のアイテムを保存しました")


if __name__ == "__main__":
    demo_concurrent_access()
    demo_producer_consumer() 