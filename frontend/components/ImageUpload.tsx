'use client'

import { useState, useRef } from 'react'
import Image from 'next/image'

interface ImageUploadProps {
  onUpload: (file: File) => void
  loading: boolean
}

export default function ImageUpload({ onUpload, loading }: ImageUploadProps) {
  const [preview, setPreview] = useState<string | null>(null)
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFile = (file: File) => {
    if (!file.type.startsWith('image/')) {
      alert('Please upload an image file')
      return
    }

    // Create preview
    const reader = new FileReader()
    reader.onload = (e) => setPreview(e.target?.result as string)
    reader.readAsDataURL(file)

    // Upload
    onUpload(file)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragActive(false)
    
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
  }

  return (
    <div className="w-full">
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleChange}
        className="hidden"
        disabled={loading}
      />

      <div
        onDragOver={(e) => { e.preventDefault(); setDragActive(true) }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
        onClick={() => !loading && fileInputRef.current?.click()}
        className={`relative border-4 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all ${
          dragActive
            ? 'border-blue-600 bg-blue-50'
            : 'border-gray-300 hover:border-blue-400 bg-white'
        } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        {preview ? (
          <div className="space-y-4">
            <div className="relative w-64 h-64 mx-auto rounded-xl overflow-hidden shadow-xl">
              <Image
                src={preview}
                alt="Preview"
                fill
                className="object-cover"
              />
            </div>
            <p className="text-gray-600">
              {loading ? 'Processing...' : 'Click or drop another image to change'}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="text-6xl">📁</div>
            <div>
              <p className="text-xl font-semibold text-gray-700 mb-2">
                Drop an image here or click to browse
              </p>
              <p className="text-sm text-gray-500">
                Supports: JPG, PNG, GIF, WebP
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}