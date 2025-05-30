# RAG Webアプリケーション API設計書

## 1. API概要

### 1.1 基本情報
- ベースURL: `/api/v1`
- 認証方式: APIキー認証
- レスポンス形式: JSON
- 文字コード: UTF-8

### 1.2 共通レスポンス形式
```json
{
    "status": "success" | "error",
    "data": {
        // レスポンスデータ
    },
    "error": {
        "code": "エラーコード",
        "message": "エラーメッセージ"
    }
}
```

## 2. エンドポイント一覧

### 2.1 文書管理API
#### 文書アップロード
- エンドポイント: `POST /documents/upload`
- 機能: `DocumentManager.upload_document`
- リクエスト:
  ```json
  {
      "file": "ファイルデータ（multipart/form-data）",
      "metadata": {
          "title": "文書タイトル",
          "description": "文書の説明",
          "tags": ["タグ1", "タグ2"]
      }
  }
  ```
- レスポンス:
  ```json
  {
      "status": "success",
      "data": {
          "document_id": "文書ID",
          "status": "processing",
          "created_at": "作成日時"
      }
  }
  ```

#### 文書一覧取得
- エンドポイント: `GET /documents`
- 機能: `DocumentManager.list_documents`
- クエリパラメータ:
  - `page`: ページ番号
  - `per_page`: 1ページあたりの件数
  - `sort`: ソート順
  - `status`: ステータスフィルター
- レスポンス:
  ```json
  {
      "status": "success",
      "data": {
          "documents": [
              {
                  "id": "文書ID",
                  "title": "文書タイトル",
                  "status": "ステータス",
                  "created_at": "作成日時"
              }
          ],
          "total": "総件数",
          "page": "現在のページ",
          "per_page": "1ページあたりの件数"
      }
  }
  ```

### 2.2 検索API
#### セマンティック検索
- エンドポイント: `POST /search`
- 機能: `SearchEngine.semantic_search`
- リクエスト:
  ```json
  {
      "query": "検索クエリ",
      "options": {
          "n_results": 10,
          "min_score": 0.5,
          "filters": {
              "tags": ["タグ1", "タグ2"],
              "date_range": {
                  "start": "開始日",
                  "end": "終了日"
              }
          }
      }
  }
  ```
- レスポンス:
  ```json
  {
      "status": "success",
      "data": {
          "results": [
              {
                  "document_id": "文書ID",
                  "content": "マッチした内容",
                  "score": 0.85,
                  "highlights": ["ハイライト1", "ハイライト2"]
              }
          ],
          "total": "検索結果件数"
      }
  }
  ```

#### ハイブリッド検索
- エンドポイント: `POST /search/hybrid`
- 機能: `SearchEngine.hybrid_search`
- リクエスト:
  ```json
  {
      "query": "検索クエリ",
      "keywords": ["キーワード1", "キーワード2"],
      "options": {
          "semantic_weight": 0.7,
          "keyword_weight": 0.3,
          "n_results": 10
      }
  }
  ```
- レスポンス: セマンティック検索と同じ形式

### 2.3 質問応答API
#### 質問処理
- エンドポイント: `POST /qa`
- 機能: `QASystem.process_question`
- リクエスト:
  ```json
  {
      "question": "質問文",
      "options": {
          "max_evidence": 3,
          "min_confidence": 0.7,
          "conversation_id": "会話ID"
      }
  }
  ```
- レスポンス:
  ```json
  {
      "status": "success",
      "data": {
          "answer": "生成された回答",
          "confidence": 0.85,
          "evidence": [
              {
                  "document_id": "文書ID",
                  "content": "根拠となる内容",
                  "relevance": 0.9
              }
          ],
          "conversation_id": "会話ID"
      }
  }
  ```

### 2.4 インデックス管理API
#### インデックス再構築
- エンドポイント: `POST /reindex`
- 機能: `IndexManager.rebuild_index`
- リクエスト:
  ```json
  {
      "document_ids": ["文書ID1", "文書ID2"],
      "options": {
          "force": false,
          "batch_size": 100
      }
  }
  ```
- レスポンス:
  ```json
  {
      "status": "success",
      "data": {
          "task_id": "タスクID",
          "status": "processing",
          "created_at": "作成日時"
      }
  }
  ```

#### インデックス状態確認
- エンドポイント: `GET /reindex/{task_id}`
- 機能: `IndexManager.check_index_status`
- レスポンス:
  ```json
  {
      "status": "success",
      "data": {
          "task_id": "タスクID",
          "status": "completed",
          "progress": 100,
          "created_at": "作成日時",
          "completed_at": "完了日時"
      }
  }
  ```

## 3. エラーコード

### 3.1 共通エラーコード
- `400`: リクエストが不正
- `401`: 認証エラー
- `403`: アクセス権限なし
- `404`: リソースが見つからない
- `500`: サーバーエラー

### 3.2 業務エラーコード
- `1001`: ファイル形式エラー
- `1002`: ファイルサイズ超過
- `2001`: 検索クエリ不正
- `2002`: 検索結果なし
- `3001`: 質問形式不正
- `3002`: 回答生成エラー
- `4001`: インデックス作成エラー
- `4002`: インデックス更新エラー

## 4. レート制限

### 4.1 制限値
- 検索API: 60リクエスト/分
- 質問応答API: 30リクエスト/分
- 文書アップロード: 10リクエスト/分
- インデックス再構築: 5リクエスト/分

### 4.2 レート制限ヘッダー
- `X-RateLimit-Limit`: 制限値
- `X-RateLimit-Remaining`: 残りリクエスト数
- `X-RateLimit-Reset`: 制限リセット時刻 