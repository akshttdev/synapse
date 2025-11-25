"use client";

import React from "react";

export interface MasonryItem {
  id: string;
  img: string;
  width?: number;
  height?: number;
}

interface MasonryProps {
  items: MasonryItem[];
}

/*
  Pure CSS column-based masonry
  - No JS layout
  - No hydration issues
  - Fully grayscale
  - Minimal
  - Works extremely well for image feeds
*/

const Masonry: React.FC<MasonryProps> = ({ items }) => {
  return (
    <div className="w-full">
      <div className="columns-2 md:columns-3 lg:columns-4 xl:columns-5 gap-4 space-y-4">
        {items.map((item) => (
          <div
            key={item.id}
            className="break-inside-avoid overflow-hidden rounded-xl shadow-md"
          >
            <img
              src={item.img}
              alt=""
              className="w-full h-auto object-cover filter grayscale rounded-xl"
            />
          </div>
        ))}
      </div>
    </div>
  );
};

export default Masonry;
