const BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function searchByText(query: string, topK = 20) {
  const res = await fetch(`${BASE}/api/v1/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, modality: 'text', top_k: topK }),
  });

  if (!res.ok) throw new Error('Search failed');
  return res.json();
}

export async function searchByImage(file: File, topK = 20) {
  const fd = new FormData();
  fd.append('file', file);
  fd.append('modality', 'image');
  fd.append('top_k', topK.toString());

  const res = await fetch(`${BASE}/api/v1/search`, { method: 'POST', body: fd });

  if (!res.ok) throw new Error('Image search failed');
  return res.json();
}
