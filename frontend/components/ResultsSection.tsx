'use client';

import ImageCard from './ImageCard';

export default function ResultsSection({ results }: any) {
  return (
    <div>
      <h2 className="text-2xl mb-4 font-semibold">Results</h2>

      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
        {results.map((r: any) => (
          <ImageCard key={r.id} result={r} />
        ))}
      </div>
    </div>
  );
}
