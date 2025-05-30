# RAG Webアプリケーション システムインターフェース設計書

## 1. システム間インターフェース

### 1.1 コンポーネント間の通信

#### フロントエンド ↔ バックエンド
```
[React Frontend] <--HTTP/HTTPS--> [FastAPI Backend]
     |                                  |
     |-- ドキュメントアップロード ----->|
     |<-- アップロード状態通知 ---------|
     |-- 検索クエリ送信 -------------->|
     |<-- 検索結果 --------------------|
     |-- 質問送信 ------------------->|
     |<-- 回答とソース --------------|
```

#### バックエンド ↔ ベクトルDB
```
[FastAPI Backend] <--Chroma Client--> [Chroma DB]
     |                                    |
     |-- ドキュメント保存 --------------->|
     |-- ベクトル検索クエリ ------------->|
     |<-- 検索結果 ----------------------|
     |-- インデックス更新 -------------->|
     |<-- 更新状態 ---------------------|
```

#### バックエンド ↔ LLM API
```
[FastAPI Backend] <--HTTP/HTTPS--> [Gemini API]
     |                                  |
     |-- テキスト埋め込み要求 --------->|
     |<-- ベクトル表現 -----------------|
     |-- 質問生成要求 ----------------->|
     |<-- 生成回答 --------------------|
```

### 1.2 データフロー

#### ドキュメント処理フロー
1. フロントエンド → バックエンド
   - ファイルアップロード（multipart/form-data）
   - メタデータ（JSON）

2. バックエンド → LLM API
   - テキストチャンク（JSON）
   - 埋め込みモデルパラメータ

3. バックエンド → Chroma DB
   - ベクトルデータ（バイナリ）
   - メタデータ（JSON）

4. バックエンド → フロントエンド
   - 処理状態（JSON）
   - エラー情報（JSON）

#### 検索フロー
1. フロントエンド → バックエンド
   - 検索クエリ（JSON）
   - フィルター条件（JSON）

2. バックエンド → LLM API
   - クエリテキスト（JSON）
   - 埋め込みパラメータ

3. バックエンド → Chroma DB
   - ベクトルクエリ（バイナリ）
   - 検索パラメータ（JSON）

4. バックエンド → フロントエンド
   - 検索結果（JSON）
   - スコア情報（JSON）

## 2. ベクトル化と検索の詳細

### 2.1 テキスト前処理

#### チャンキング戦略
```python
class TextChunker:
    def __init__(self, config):
        self.chunk_size = config.chunk_size  # デフォルト: 1000文字
        self.chunk_overlap = config.chunk_overlap  # デフォルト: 200文字
        self.separators = ["\n\n", "\n", "。", "、", " ", ""]

    def split_text(self, text: str) -> List[str]:
        # 1. テキストの正規化
        text = self.normalize_text(text)
        
        # 2. セパレータによる分割
        chunks = self.split_by_separators(text)
        
        # 3. チャンクサイズの調整
        chunks = self.adjust_chunk_sizes(chunks)
        
        return chunks

    def normalize_text(self, text: str) -> str:
        # 空白の正規化
        text = re.sub(r'\s+', ' ', text)
        # 特殊文字の処理
        text = text.replace('\r', '\n')
        return text.strip()
```

### 2.2 ベクトル化プロセス

#### 埋め込み生成
```python
class EmbeddingGenerator:
    def __init__(self, model_config):
        self.model = model_config.model  # "gemini-embedding-001"
        self.dimensions = model_config.dimensions  # 768
        self.batch_size = model_config.batch_size  # 32

    async def generate_embeddings(self, texts: List[str]) -> List[Vector]:
        # 1. バッチ処理の準備
        batches = self.create_batches(texts)
        
        # 2. 各バッチの埋め込み生成
        embeddings = []
        for batch in batches:
            # Gemini APIへのリクエスト
            response = await self.call_embedding_api(batch)
            embeddings.extend(response.embeddings)
        
        # 3. ベクトルの正規化
        normalized_embeddings = self.normalize_vectors(embeddings)
        
        return normalized_embeddings

    def normalize_vectors(self, vectors: List[Vector]) -> List[Vector]:
        # L2正規化
        return [v / np.linalg.norm(v) for v in vectors]
```

### 2.3 検索アルゴリズム

#### セマンティック検索
```python
class SemanticSearcher:
    def __init__(self, db_config):
        self.collection = db_config.collection
        self.index_params = {
            "hnsw": {
                "M": 16,
                "ef_construction": 100,
                "ef_search": 50
            }
        }

    async def search(self, query: str, filters: Dict) -> List[SearchResult]:
        # 1. クエリのベクトル化
        query_vector = await self.embed_query(query)
        
        # 2. ベクトル検索の実行
        results = await self.vector_search(
            query_vector,
            filters,
            n_results=10
        )
        
        # 3. スコアの計算と正規化
        normalized_results = self.normalize_scores(results)
        
        return normalized_results

    def normalize_scores(self, results: List[SearchResult]) -> List[SearchResult]:
        # スコアの正規化（0-1の範囲に）
        max_score = max(r.score for r in results)
        if max_score > 0:
            for r in results:
                r.score = r.score / max_score
        return results
```

### 2.4 スコアリングとランキング

#### ハイブリッドスコアリング
```python
class HybridScorer:
    def __init__(self, config):
        self.semantic_weight = config.semantic_weight  # 0.7
        self.keyword_weight = config.keyword_weight    # 0.3
        self.bm25 = BM25Okapi()

    def calculate_hybrid_score(self, 
                             semantic_score: float,
                             keyword_score: float) -> float:
        # 重み付けスコアの計算
        hybrid_score = (
            self.semantic_weight * semantic_score +
            self.keyword_weight * keyword_score
        )
        return hybrid_score

    def rank_results(self, results: List[SearchResult]) -> List[SearchResult]:
        # スコアによるソート
        return sorted(results, key=lambda x: x.score, reverse=True)
```

### 2.5 一致判定

#### 類似度計算
```python
class SimilarityCalculator:
    def __init__(self):
        self.similarity_threshold = 0.7
        self.metrics = {
            "cosine": self.cosine_similarity,
            "euclidean": self.euclidean_similarity
        }

    def cosine_similarity(self, vec1: Vector, vec2: Vector) -> float:
        # コサイン類似度の計算
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        return dot_product / (norm1 * norm2)

    def is_match(self, 
                query_vector: Vector,
                doc_vector: Vector,
                metric: str = "cosine") -> bool:
        # 類似度の計算
        similarity = self.metrics[metric](query_vector, doc_vector)
        # 閾値による判定
        return similarity >= self.similarity_threshold
```

## 3. パフォーマンス最適化

### 3.1 キャッシュ戦略
```python
class CacheManager:
    def __init__(self, config):
        self.vector_cache = LRUCache(
            maxsize=config.vector_cache_size,
            ttl=config.vector_cache_ttl
        )
        self.result_cache = LRUCache(
            maxsize=config.result_cache_size,
            ttl=config.result_cache_ttl
        )

    async def get_cached_vector(self, text: str) -> Optional[Vector]:
        return await self.vector_cache.get(text)

    async def get_cached_results(self, 
                               query: str,
                               filters: Dict) -> Optional[List[SearchResult]]:
        cache_key = self.generate_cache_key(query, filters)
        return await self.result_cache.get(cache_key)
```

### 3.2 バッチ処理
```python
class BatchProcessor:
    def __init__(self, config):
        self.batch_size = config.batch_size
        self.max_workers = config.max_workers

    async def process_batch(self, items: List[Any]) -> List[Any]:
        # バッチの分割
        batches = [
            items[i:i + self.batch_size]
            for i in range(0, len(items), self.batch_size)
        ]
        
        # 並列処理
        async with asyncio.TaskGroup() as group:
            tasks = [
                group.create_task(self.process_single_batch(batch))
                for batch in batches
            ]
        
        # 結果の結合
        results = []
        for task in tasks:
            results.extend(task.result())
        
        return results
```

## 4. エラーハンドリング

### 4.1 エラー種別
```python
class VectorizationError(Exception):
    """ベクトル化処理中のエラー"""
    pass

class SearchError(Exception):
    """検索処理中のエラー"""
    pass

class CacheError(Exception):
    """キャッシュ処理中のエラー"""
    pass
```

### 4.2 リトライ戦略
```python
class RetryHandler:
    def __init__(self, config):
        self.max_retries = config.max_retries
        self.retry_delay = config.retry_delay

    async def with_retry(self, 
                        operation: Callable,
                        *args,
                        **kwargs) -> Any:
        for attempt in range(self.max_retries):
            try:
                return await operation(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(self.retry_delay * (attempt + 1))
``` 