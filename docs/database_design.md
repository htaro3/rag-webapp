# RAG Webアプリケーション データベース設計書

## 1. 概要

### 1.1 使用データベース
- ベクトルデータベース: Chroma
- 用途: ドキュメントのベクトル化とセマンティック検索

### 1.2 主要機能
- ドキュメントのベクトル化と保存
- セマンティック検索
- メタデータ管理
- インデックス管理

## 2. データモデル

### 2.1 ドキュメントコレクション

#### ドキュメントメタデータ
```json
{
  "id": "string",           // ドキュメントID
  "title": "string",        // ドキュメントタイトル
  "description": "string",  // 説明
  "file_path": "string",    // ファイルパス
  "file_type": "string",    // ファイルタイプ
  "file_size": "number",    // ファイルサイズ
  "created_at": "string",   // 作成日時
  "updated_at": "string",   // 更新日時
  "status": "string",       // ステータス（processing/completed/failed）
  "tags": ["string"],       // タグ
  "metadata": {             // 追加メタデータ
    "author": "string",
    "version": "string",
    "custom_fields": {}
  }
}
```

#### ドキュメントチャンク
```json
{
  "id": "string",           // チャンクID
  "document_id": "string",  // 親ドキュメントID
  "content": "string",      // テキスト内容
  "chunk_index": "number",  // チャンクの順序
  "embedding": "vector",    // ベクトル埋め込み
  "metadata": {             // チャンク固有のメタデータ
    "page": "number",
    "section": "string",
    "position": "number"
  }
}
```

### 2.2 インデックス管理

#### インデックスタスク
```json
{
  "id": "string",           // タスクID
  "document_ids": ["string"], // 対象ドキュメントID
  "status": "string",       // ステータス
  "progress": "number",     // 進捗率
  "created_at": "string",   // 作成日時
  "updated_at": "string",   // 更新日時
  "error": "string",        // エラーメッセージ
  "metadata": {             // タスク固有のメタデータ
    "model": "string",
    "parameters": {}
  }
}
```

## 3. インデックス設計

### 3.1 ベクトルインデックス
- インデックスタイプ: HNSW（Hierarchical Navigable Small World）
- 次元数: 768（Gemini Embedding Model）
- メトリック: コサイン類似度

### 3.2 インデックスパラメータ
```json
{
  "hnsw": {
    "M": 16,               // グラフの最大接続数
    "ef_construction": 100, // インデックス構築時の探索幅
    "ef_search": 50        // 検索時の探索幅
  },
  "optimization": {
    "batch_size": 1000,    // バッチ処理サイズ
    "threads": 4           // 並列処理スレッド数
  }
}
```

## 4. クエリ設計

### 4.1 セマンティック検索
```python
# 検索パラメータ
{
    "query": "検索クエリ",
    "n_results": 10,        # 取得件数
    "where": {              # メタデータフィルター
        "document_id": ["id1", "id2"],
        "tags": ["tag1", "tag2"]
    },
    "where_document": {     # ドキュメント内容フィルター
        "$contains": "キーワード"
    }
}
```

### 4.2 ハイブリッド検索
```python
# ハイブリッド検索パラメータ
{
    "query": "検索クエリ",
    "n_results": 10,
    "where": {},
    "where_document": {},
    "hybrid_search": {
        "alpha": 0.5,       # セマンティック検索の重み
        "text_search": {    # テキスト検索パラメータ
            "type": "bm25",
            "parameters": {
                "k1": 1.5,
                "b": 0.75
            }
        }
    }
}
```

## 5. パフォーマンス最適化

### 5.1 インデックス最適化
- 定期的なインデックスの再構築
- バッチ処理による効率的な更新
- キャッシュの活用

### 5.2 クエリ最適化
- 適切なインデックスパラメータの設定
- フィルター条件の最適化
- 結果のキャッシュ

## 6. バックアップとリカバリ

### 6.1 バックアップ戦略
- 定期的なスナップショット
- 増分バックアップ
- メタデータの別途バックアップ

### 6.2 リカバリ手順
1. スナップショットからの復元
2. メタデータの復元
3. インデックスの再構築
4. 整合性チェック

## 7. 監視とメンテナンス

### 7.1 監視項目
- インデックスサイズ
- クエリパフォーマンス
- メモリ使用量
- エラー率

### 7.2 メンテナンスタスク
- 定期的なインデックス最適化
- 古いデータのアーカイブ
- パフォーマンスチューニング
- セキュリティアップデート 