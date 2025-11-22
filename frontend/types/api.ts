export interface SearchResult {
  id: string;
  score: number;
  payload: {
    text?: string;
    media_type?: string;
    file_path?: string;
    tags?: string[];
    timestamp?: number;
    [key: string]: any;
  };
}

export interface SearchResponse {
  results: SearchResult[];
  query: string;
  count: number;
  search_time_ms?: number;
  timestamp?: string;
}

export interface SearchRequest {
  query: string;
  top_k?: number;
  filters?: Record<string, any>;
  score_threshold?: number;
  search_type?: 'vector' | 'hybrid';
}
