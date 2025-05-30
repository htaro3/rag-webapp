"""
ベクトルDBの再インデックスを行うユーティリティスクリプト
"""

import os
import sys
from pathlib import Path
import traceback
import time

# 内部モジュールをインポートするためにパスを調整
sys.path.append('.')

try:
    from app.core.chromadb_client import collection, client
    from app.services.embed_service import embed_content
    from app.core.config import VECTOR_DB_DIR, VECTOR_COLLECTION_NAME
    print("モジュールのインポートに成功しました")
except Exception as e:
    print(f"モジュールのインポート中にエラーが発生しました: {e}")
    traceback.print_exc()
    sys.exit(1)

def main():
    print("ベクトルDBの再インデックスを開始します...")
    print(f"ベクトルDB保存先: {VECTOR_DB_DIR}")
    print(f"コレクション名: {VECTOR_COLLECTION_NAME}")
    
    # collection変数をグローバルで使用することを宣言
    global collection
    
    try:
        # コレクション名を取得
        collection_name = collection.name
        print(f"現在のコレクション名: {collection_name}")
        
        # ベクトルDBの内容を一旦全削除（コレクションを削除して再作成）
        print(f"既存のコレクション '{collection_name}' を削除中...")
        try:
            client.delete_collection(collection_name)
            print("コレクション削除成功")
        except Exception as e:
            print(f"コレクション削除中にエラー: {e}")
            traceback.print_exc()
        
        print(f"コレクション '{collection_name}' を再作成中...")
        # コレクション参照を更新
        from app.core.chromadb_client import get_collection
        collection = get_collection()
        print(f"新しいコレクション作成成功: {collection.name}")
    except Exception as e:
        print(f"コレクションのリセット中にエラーが発生しました: {e}")
        traceback.print_exc()
        print("既存のコレクションを使用して続行します...")
    
    # アップロードディレクトリ内のファイルを処理
    upload_dir = Path("uploads")
    if not upload_dir.exists():
        print(f"アップロードディレクトリが見つかりません: {upload_dir.absolute()}")
        return
    
    # すべてのテキストファイルを処理
    files = list(upload_dir.glob("*.txt"))
    total = len(files)
    print(f"合計 {total} 個のファイルを処理します...")
    
    if total == 0:
        print(f"警告: ディレクトリ {upload_dir.absolute()} にテキストファイルが見つかりません")
        return
    
    success_count = 0
    error_count = 0
    total_chunks = 0
    
    for i, file_path in enumerate(files, 1):
        try:
            # ファイルの内容を読み込む
            content = file_path.read_text(encoding="utf-8")
            
            # コンテンツ先頭部分を表示（デバッグ用）
            content_preview = content[:100].replace('\n', ' ') + '...'
            print(f"ファイル内容プレビュー: {content_preview}")
            
            # ベクトルDBに再登録
            chunks = embed_content(content, file_path.name)
            
            print(f"[{i}/{total}] {file_path.name} - {chunks}チャンク作成")
            success_count += 1
            total_chunks += chunks
            
            # 処理の間に少し待機（API制限対策）
            if i % 10 == 0:
                print(f"API制限対策のため5秒間待機中...")
                time.sleep(5)
                
        except Exception as e:
            print(f"[エラー] {file_path.name}: {e}")
            traceback.print_exc()
            error_count += 1
    
    print("\n==== 再インデックス完了 ====")
    print(f"処理成功: {success_count} ファイル")
    print(f"エラー: {error_count} ファイル")
    print(f"作成されたチャンク数: {total_chunks}")
    print(f"コレクション '{collection.name}' の現在のアイテム数: {len(collection.get()['ids'])}")

if __name__ == "__main__":
    main() 