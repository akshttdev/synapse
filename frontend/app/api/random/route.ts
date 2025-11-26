import { NextResponse } from "next/server";

export async function GET() {
  // Generate 12 random images
  const items = Array.from({ length: 12 }).map(() => {
    const w = 500 + Math.floor(Math.random() * 800);
    const h = 500 + Math.floor(Math.random() * 900);

    return {
      id: crypto.randomUUID(),
      img: `https://picsum.photos/${w}/${h}?random=${Math.random()}`,
      width: w,
      height: h,
    };
  });

  return NextResponse.json({ items });
}
