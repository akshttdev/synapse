'use client'

import Image from "next/image"
import { useState } from "react"

export default function ImageCard({ result }: any) {
  const [loaded, setLoaded] = useState(false)

  // FIX → Always use metadata.thumbnail first
  const url =
    result?.metadata?.thumbnail ||
    result?.thumbnail_url ||
    "";

  return (
    <div className="bg-white/10 rounded-xl overflow-hidden shadow-md">
      <div className="relative w-full aspect-square">
        {!loaded && (
          <div className="absolute inset-0 bg-black/40 animate-pulse" />
        )}

        <Image
          src={url}
          alt={result.metadata?.filename}
          fill
          sizes="(max-width:768px) 50vw, 33vw"
          className={`object-cover transition-all duration-500 ${loaded ? "opacity-100" : "opacity-0"}`}
          onLoad={() => setLoaded(true)}
        />

        {/* Filename */}
        <span className="absolute top-1 left-1 bg-black/50 px-2 py-1 text-xs rounded-md">
          {result.metadata?.filename}
        </span>
      </div>
    </div>
  )
}
