# RAG Webアプリケーション フロントエンド設計書

## 1. 概要

### 1.1 技術スタック
- フレームワーク: React
- 言語: TypeScript
- スタイリング: Tailwind CSS
- 状態管理: React Query + Zustand
- UIコンポーネント: Headless UI
- アイコン: Heroicons

### 1.2 主要機能
- ドキュメントアップロードと管理
- セマンティック検索
- 質問応答インターフェース
- インデックス管理

## 2. 画面設計

### 2.1 画面一覧

#### ダッシュボード
- パス: `/`
- 機能:
  - 最近のドキュメント表示
  - 検索履歴
  - システムステータス
  - クイックアクション

#### ドキュメント管理
- パス: `/documents`
- 機能:
  - ドキュメント一覧表示
  - アップロード
  - メタデータ編集
  - タグ管理
  - 削除

#### 検索
- パス: `/search`
- 機能:
  - セマンティック検索
  - フィルター
  - 検索結果表示
  - 結果のエクスポート

#### 質問応答
- パス: `/qa`
- 機能:
  - 質問入力
  - 回答表示
  - ソース表示
  - 会話履歴

#### 設定
- パス: `/settings`
- 機能:
  - インデックス管理
  - API設定
  - システム設定

### 2.2 コンポーネント設計

#### 共通コンポーネント
```typescript
// レイアウト
interface LayoutProps {
  children: React.ReactNode;
  title?: string;
}

// カード
interface CardProps {
  title: string;
  children: React.ReactNode;
  actions?: React.ReactNode;
}

// ボタン
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'danger';
  size: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
}

// 入力フィールド
interface InputProps {
  label: string;
  type: 'text' | 'textarea' | 'file';
  value: string;
  onChange: (value: string) => void;
  error?: string;
}
```

#### 機能別コンポーネント
```typescript
// ドキュメントアップロード
interface UploadProps {
  onUpload: (file: File, metadata: DocumentMetadata) => Promise<void>;
  maxSize: number;
  allowedTypes: string[];
}

// 検索フォーム
interface SearchFormProps {
  onSearch: (query: SearchQuery) => Promise<void>;
  filters: SearchFilters;
}

// 質問応答
interface QAChatProps {
  onQuestion: (question: string) => Promise<void>;
  history: ChatHistory[];
}

// インデックス管理
interface IndexManagerProps {
  onReindex: (documentIds: string[]) => Promise<void>;
  status: IndexStatus;
}
```

## 3. 状態管理

### 3.1 グローバル状態
```typescript
interface AppState {
  // ユーザー設定
  settings: {
    theme: 'light' | 'dark';
    language: string;
    apiKey: string;
  };
  
  // ドキュメント管理
  documents: {
    items: Document[];
    selected: string[];
    filters: DocumentFilters;
  };
  
  // 検索状態
  search: {
    query: string;
    results: SearchResult[];
    filters: SearchFilters;
  };
  
  // 質問応答
  qa: {
    history: ChatHistory[];
    currentQuestion: string;
    isProcessing: boolean;
  };
}
```

### 3.2 API状態管理
```typescript
// React Query設定
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      cacheTime: 30 * 60 * 1000,
      retry: 3,
    },
  },
});

// APIフック
const useDocuments = () => {
  return useQuery('documents', fetchDocuments);
};

const useSearch = (query: string) => {
  return useQuery(['search', query], () => searchDocuments(query));
};

const useQA = (question: string) => {
  return useMutation((q: string) => askQuestion(q));
};
```

## 4. スタイリング

### 4.1 デザインシステム
```typescript
// カラーパレット
const colors = {
  primary: {
    50: '#f0f9ff',
    100: '#e0f2fe',
    // ...
    900: '#0c4a6e',
  },
  // その他の色...
};

// タイポグラフィ
const typography = {
  h1: 'text-4xl font-bold',
  h2: 'text-3xl font-semibold',
  // ...
};

// スペーシング
const spacing = {
  xs: '0.25rem',
  sm: '0.5rem',
  // ...
};
```

### 4.2 レスポンシブデザイン
```typescript
// ブレークポイント
const breakpoints = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
};

// レスポンシブユーティリティ
const responsive = {
  container: 'container mx-auto px-4 sm:px-6 lg:px-8',
  grid: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4',
};
```

## 5. パフォーマンス最適化

### 5.1 コード分割
```typescript
// 遅延ロード
const DocumentManager = lazy(() => import('./DocumentManager'));
const SearchPage = lazy(() => import('./SearchPage'));
const QAPage = lazy(() => import('./QAPage'));

// ルーティング
const routes = [
  {
    path: '/documents',
    component: DocumentManager,
  },
  // ...
];
```

### 5.2 キャッシュ戦略
```typescript
// キャッシュ設定
const cacheConfig = {
  documents: {
    staleTime: 5 * 60 * 1000,
    cacheTime: 30 * 60 * 1000,
  },
  search: {
    staleTime: 1 * 60 * 1000,
    cacheTime: 5 * 60 * 1000,
  },
};
```

## 6. エラーハンドリング

### 6.1 エラー境界
```typescript
class ErrorBoundary extends React.Component {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return <ErrorFallback error={this.state.error} />;
    }
    return this.props.children;
  }
}
```

### 6.2 エラーメッセージ
```typescript
const errorMessages = {
  network: 'ネットワークエラーが発生しました',
  upload: 'ファイルのアップロードに失敗しました',
  search: '検索中にエラーが発生しました',
  // ...
};
```

## 7. アクセシビリティ

### 7.1 アクセシビリティ対応
- ARIA属性の適切な使用
- キーボードナビゲーション
- スクリーンリーダー対応
- カラーコントラスト

### 7.2 アクセシビリティコンポーネント
```typescript
// アクセシブルなボタン
const AccessibleButton = ({ children, ...props }) => (
  <button
    role="button"
    tabIndex={0}
    aria-label={props['aria-label']}
    {...props}
  >
    {children}
  </button>
);

// アクセシブルなモーダル
const AccessibleModal = ({ isOpen, onClose, children }) => (
  <Dialog
    open={isOpen}
    onClose={onClose}
    aria-labelledby="modal-title"
  >
    {children}
  </Dialog>
);
```

## 8. テスト戦略

### 8.1 テスト種類
- ユニットテスト: Jest
- コンポーネントテスト: React Testing Library
- E2Eテスト: Cypress
- アクセシビリティテスト: jest-axe

### 8.2 テストカバレッジ
```typescript
// テスト設定
module.exports = {
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};
``` 