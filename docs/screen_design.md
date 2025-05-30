# RAG Webアプリケーション 画面設計書

## 1. 画面一覧

### 1.1 ダッシュボード画面
- パス：`/`
- コンポーネント：`DashboardPage`
- 主要機能：
  - 最近の文書表示（`RecentDocuments`）
  - 検索履歴表示（`SearchHistory`）
  - システム状態表示（`SystemStatus`）
  - クイックアクション（`QuickActions`）

### 1.2 文書管理画面
- パス：`/documents`
- コンポーネント：`DocumentManagementPage`
- 主要機能：
  - 文書一覧表示（`DocumentList`）
  - 文書アップロード（`DocumentUpload`）
  - 文書編集（`DocumentEditor`）
  - 文書削除（`DocumentDelete`）

### 1.3 検索画面
- パス：`/search`
- コンポーネント：`SearchPage`
- 主要機能：
  - 検索フォーム（`SearchForm`）
  - 検索結果表示（`SearchResults`）
  - フィルター設定（`SearchFilters`）
  - 結果エクスポート（`ResultExport`）

### 1.4 質問応答画面
- パス：`/qa`
- コンポーネント：`QAPage`
- 主要機能：
  - 質問入力（`QuestionInput`）
  - 回答表示（`AnswerDisplay`）
  - 根拠表示（`EvidenceDisplay`）
  - 会話履歴（`ConversationHistory`）

### 1.5 設定画面
- パス：`/settings`
- コンポーネント：`SettingsPage`
- 主要機能：
  - インデックス管理（`IndexManagement`）
  - API設定（`APISettings`）
  - システム設定（`SystemSettings`）

## 2. 画面と機能の連携

### 2.1 ダッシュボード画面の機能連携
```
[RecentDocuments]
    ↓
[DocumentManager.list_documents] → [DocumentCard]
    ↓
[QuickActions]
    ↓
[DocumentManager.upload_document] または [SearchEngine.semantic_search]
```

### 2.2 文書管理画面の機能連携
```
[DocumentUpload]
    ↓
[DocumentManager.upload_document] → [DocumentProcessor.process_document]
    ↓
[DocumentList]
    ↓
[DocumentManager.list_documents] → [DocumentCard]
    ↓
[DocumentEditor] または [DocumentDelete]
    ↓
[DocumentManager.update_document_metadata] または [DocumentManager.delete_document]
```

### 2.3 検索画面の機能連携
```
[SearchForm]
    ↓
[SearchEngine.semantic_search] または [SearchEngine.hybrid_search]
    ↓
[SearchResults]
    ↓
[SearchResultFormatter.format_results] → [ResultCard]
    ↓
[SearchFilters] → [SearchEngine.semantic_search]
```

### 2.4 質問応答画面の機能連携
```
[QuestionInput]
    ↓
[QASystem.process_question] → [SearchEngine.semantic_search]
    ↓
[AnswerDisplay]
    ↓
[AnswerGenerator.generate_answer] → [EvidenceDisplay]
    ↓
[ConversationHistory]
    ↓
[QASystem.manage_conversation_history]
```

## 3. コンポーネントの詳細

### 3.1 共通コンポーネント
#### `Layout`
- 機能：画面の基本レイアウト
- 子コンポーネント：
  - `Header`
  - `Sidebar`
  - `MainContent`
  - `Footer`

#### `DocumentCard`
- 機能：文書情報の表示
- 表示項目：
  - タイトル
  - 作成日時
  - ステータス
  - アクションボタン

#### `SearchForm`
- 機能：検索条件の入力
- 入力項目：
  - 検索クエリ
  - 検索タイプ（セマンティック/ハイブリッド）
  - フィルター条件

### 3.2 機能別コンポーネント
#### `DocumentUpload`
- 機能：文書のアップロード
- 処理：
  1. ファイル選択
  2. メタデータ入力
  3. アップロード実行
  4. 進捗表示

#### `SearchResults`
- 機能：検索結果の表示
- 表示項目：
  - 結果リスト
  - スコア
  - ハイライト
  - ページネーション

#### `AnswerDisplay`
- 機能：回答の表示
- 表示項目：
  - 生成された回答
  - 信頼度
  - 根拠文書
  - 関連情報

## 4. 画面遷移

### 4.1 主要な画面遷移
```
ダッシュボード
    ↓
文書管理 ←→ 検索 ←→ 質問応答
    ↓
設定
```

### 4.2 遷移トリガー
- サイドバーメニュー
- クイックアクション
- 検索結果からの遷移
- 文書カードからの遷移

## 5. レスポンシブデザイン

### 5.1 ブレークポイント
- モバイル：< 640px
- タブレット：640px - 1024px
- デスクトップ：> 1024px

### 5.2 レイアウト調整
- モバイル：1カラム
- タブレット：2カラム
- デスクトップ：3カラム

## 6. エラー表示

### 6.1 エラーメッセージ
- アップロードエラー
- 検索エラー
- 質問応答エラー
- システムエラー

### 6.2 エラー表示方法
- トースト通知
- インラインエラー
- エラーモーダル
- エラーページ 