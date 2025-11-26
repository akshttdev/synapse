'use client';

import { useRef, useState } from 'react';

export default function SearchInput({
  onSearch,
  loading,
}: {
  onSearch: (query: string, file?: File) => void;
  loading: boolean;
}) {
  const [query, setQuery] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSend = () => {
    if (query.trim()) onSearch(query.trim());
  };

  const handleFile = (file: File) => {
    onSearch('', file);
  };

  return (
    <div className="flex items-center gap-2 w-full bg-white/10 p-3 rounded-xl shadow-lg">
      
      {/* Upload Button */}
      <button
        onClick={() => fileInputRef.current?.click()}
        className="text-2xl"
      >
        📁
      </button>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={(e) => e.target.files && handleFile(e.target.files[0])}
      />

      {/* Text Input */}
      <input
        type="text"
        value={query}
        disabled={loading}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Type or upload image..."
        className="flex-1 px-3 py-2 bg-transparent outline-none text-white placeholder-gray-400"
      />

      {/* Send Arrow */}
      <button
        disabled={loading}
        onClick={handleSend}
        className="text-xl bg-white text-black px-4 py-2 rounded-lg font-bold hover:bg-gray-200"
      >
        ↑
      </button>
    </div>
  );
}
