"use client";

import React, { useCallback, useEffect, useRef, useState } from "react";
import Masonry, { MasonryItem } from "@/components/search/Masonry";

export default function DashboardPage() {
  const [items, setItems] = useState<MasonryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const loaderRef = useRef<HTMLDivElement | null>(null);

  // Load black & white random images
  const loadBatch = async () => {
    await new Promise((r) => setTimeout(r, 350)); // smooth load

    const batch = Array.from({ length: 12 }).map(() => {
      const w = 500 + Math.floor(Math.random() * 800);
      const h = 500 + Math.floor(Math.random() * 900);

      return {
        id: crypto.randomUUID(),
        img: `https://picsum.photos/${w}/${h}?grayscale&random=${Math.random()}`,
        width: w,
        height: h,
      };
    });

    return batch;
  };

  // INITIAL LOAD
  useEffect(() => {
    (async () => {
      const b = await loadBatch();
      setItems(b);
      setLoading(false);
    })();
  }, []);

  // LOAD MORE
  const loadMore = useCallback(async () => {
    if (loading) return;

    setLoading(true);
    const more = await loadBatch();
    setItems((prev) => [...prev, ...more]); // append to bottom
    setLoading(false);
    setPage((p) => p + 1);
  }, [loading]);

  // INTERSECTION OBSERVER
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) loadMore();
      },
      { rootMargin: "200px", threshold: 0.1 }
    );

    if (loaderRef.current) observer.observe(loaderRef.current);
    return () => observer.disconnect();
  }, [loadMore]);

  return (
    <div className="min-h-screen w-full bg-[#07040b] text-white px-6 py-8">
      <div className="max-w-6xl mx-auto">

        {/* Minimal top bar */}
        <h1 className="text-xl font-medium mb-6 text-white/80">
          Image Feed — Minimal Black & White
        </h1>

        {/* Masonry Feed */}
        <Masonry items={items} />

        {/* Infinite scroll loader */}
        <div ref={loaderRef} className="w-full h-20 flex items-center justify-center">
          {loading && <div className="text-gray-400 animate-pulse">Loading…</div>}
        </div>
      </div>
    </div>
  );
}
