'use client';

import { useState } from 'react';
import SearchInput from '@/components/SearchInput';
import ResultsSection from '@/components/ResultsSection';
import Loader from '@/components/Loader';
import { searchByText, searchByImage } from '@/lib/api';

export default function SearchPage() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState(null);

  const handleSearch = async (query: string, file?: File) => {
    setLoading(true);
    setResults([]);
    setStats(null);

    try {
      let data;

      if (file) data = await searchByImage(file, 100);
      else data = await searchByText(query, 100);

      setResults(data.results);
      setStats({
        total: data.total,
        latency: data.latency_ms,
        metrics: data.metrics,
        query: query || file?.name || 'Image Upload',
      });
    } catch (err) {
      console.error(err);
      alert('Search failed, try again.');
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-black text-white px-6 py-10">
      <div className="max-w-5xl mx-auto space-y-8">
        
        <h1 className="text-4xl font-bold text-center mb-6">
          🔍 AI Search (Text + Image)
        </h1>

        {/* Single Search Input */}
        <SearchInput onSearch={handleSearch} loading={loading} />

        {/* Loading */}
        {loading && <Loader />}

        {/* Stats */}
        {stats && (
          <div className="bg-white/10 p-4 rounded-xl backdrop-blur">
            <p className="text-sm text-gray-300">
              Query: <span className="text-white font-semibold">{stats.query}</span>
            </p>
            <p className="text-sm text-gray-300">
              Total Results: <span className="text-white font-semibold">{stats.total}</span>
            </p>
            <p className="text-sm text-gray-300">
              Latency: <span className="text-white font-semibold">{stats.latency.toFixed(0)}ms</span>
            </p>
          </div>
        )}

        {/* Results */}
        {results.length > 0 && <ResultsSection results={results} />}
      </div>
    </div>
  );
}
