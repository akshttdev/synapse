'use client';

import { useState, useCallback } from 'react';
import { apiClient } from '@/lib/api/client';
import type { SearchResult, SearchRequest } from '@/types/api';

export function useSearch() {
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchStats, setSearchStats] = useState<any>(null);

  const search = useCallback(async (request: SearchRequest) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.search(request);
      setResults(response.results || []);
      setSearchStats({
        count: response.count,
        search_time_ms: response.search_time_ms,
        timestamp: response.timestamp,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { search, results, isLoading, error, searchStats };
}
