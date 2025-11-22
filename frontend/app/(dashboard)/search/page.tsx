'use client';

import { useState, useCallback } from 'react';
import { Search, Loader2, Upload, Image as ImageIcon, X, CheckCircle2 } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useSearch } from '@/lib/hooks/use-search';

export default function SearchPage() {
  // Search state
  const [query, setQuery] = useState('');
  const [topK, setTopK] = useState(20);
  const [searchType, setSearchType] = useState<'vector' | 'hybrid'>('vector');
  const { search, results, isLoading, error, searchStats } = useSearch();

  // Upload state
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadPreview, setUploadPreview] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Drag and drop state
  const [isDragging, setIsDragging] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    await search({
      query: query.trim(),
      top_k: topK,
      search_type: searchType,
    });
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleSearch();
  };

  // File upload handlers
  const handleFileSelect = (file: File) => {
    if (!file.type.startsWith('image/') && !file.type.startsWith('video/')) {
      setUploadError('Please select an image or video file');
      return;
    }

    setUploadFile(file);
    setUploadError(null);
    setUploadSuccess(false);

    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setUploadPreview(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const file = e.dataTransfer.files[0];
    if (file) handleFileSelect(file);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFileSelect(file);
  };

  const clearUpload = () => {
    setUploadFile(null);
    setUploadPreview(null);
    setUploadSuccess(false);
    setUploadError(null);
  };

  const handleUpload = async () => {
    if (!uploadFile) return;

    setIsUploading(true);
    setUploadError(null);

    try {
      const formData = new FormData();
      formData.append('file', uploadFile);
      formData.append('metadata', JSON.stringify({
        filename: uploadFile.name,
        size: uploadFile.size,
        type: uploadFile.type,
      }));

      const response = await fetch('http://localhost:8000/api/v1/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const data = await response.json();
      setUploadSuccess(true);
      
      // Clear after 3 seconds
      setTimeout(() => {
        clearUpload();
      }, 3000);
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  // Search by image
  const handleSearchByImage = async () => {
    if (!uploadFile) return;

    setIsUploading(true);
    setUploadError(null);

    try {
      const formData = new FormData();
      formData.append('file', uploadFile);

      const response = await fetch(
        `http://localhost:8000/api/v1/search/image?top_k=${topK}`,
        {
          method: 'POST',
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error('Image search failed');
      }

      const data = await response.json();
      
      // Update results using the search hook's setter
      // For now, we'll just show a success message
      setUploadSuccess(true);
      alert(`Found ${data.count} similar images!`);
      
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : 'Image search failed');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600" />
              <h1 className="text-2xl font-bold">Multimodal Search</h1>
            </div>
            <Badge variant="secondary">
              {results.length} results
            </Badge>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <Tabs defaultValue="text-search" className="w-full">
          <TabsList className="grid w-full max-w-md mx-auto grid-cols-2">
            <TabsTrigger value="text-search" className="gap-2">
              <Search className="h-4 w-4" />
              Text Search
            </TabsTrigger>
            <TabsTrigger value="image-search" className="gap-2">
              <ImageIcon className="h-4 w-4" />
              Image Search
            </TabsTrigger>
          </TabsList>

          {/* Text Search Tab */}
          <TabsContent value="text-search" className="mt-6">
            <Card className="mb-8">
              <CardContent className="pt-6">
                <div className="flex gap-4">
                  <div className="flex-1 relative">
                    <Search className="absolute left-3 top-3 h-5 w-5 text-muted-foreground" />
                    <Input
                      type="text"
                      placeholder="Describe what you're looking for..."
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      onKeyPress={handleKeyPress}
                      className="pl-10 h-12 text-lg"
                    />
                  </div>
                  <Button
                    onClick={handleSearch}
                    disabled={isLoading || !query.trim()}
                    size="lg"
                    className="px-8"
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                        Searching...
                      </>
                    ) : (
                      <>
                        <Search className="mr-2 h-5 w-5" />
                        Search
                      </>
                    )}
                  </Button>
                </div>

                {/* Search Options */}
                <div className="flex gap-4 mt-4 items-center">
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-muted-foreground">Results:</span>
                    <Select
                      value={topK.toString()}
                      onValueChange={(value) => setTopK(parseInt(value))}
                    >
                      <SelectTrigger className="w-24">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="10">10</SelectItem>
                        <SelectItem value="20">20</SelectItem>
                        <SelectItem value="50">50</SelectItem>
                        <SelectItem value="100">100</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="text-sm text-muted-foreground">Mode:</span>
                    <Select
                      value={searchType}
                      onValueChange={(value: 'vector' | 'hybrid') => setSearchType(value)}
                    >
                      <SelectTrigger className="w-32">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="vector">Vector</SelectItem>
                        <SelectItem value="hybrid">Hybrid</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Image/Upload Search Tab */}
          <TabsContent value="image-search" className="mt-6">
            <Card className="mb-8">
              <CardHeader>
                <CardTitle>Search by Image or Upload New Media</CardTitle>
                <CardDescription>
                  Upload an image to find similar content or add it to the database
                </CardDescription>
              </CardHeader>
              <CardContent>
                {/* Upload Area */}
                <div
                  onDrop={handleDrop}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  className={`
                    relative border-2 border-dashed rounded-lg p-8 text-center
                    transition-all cursor-pointer
                    ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
                    ${uploadFile ? 'bg-slate-50' : ''}
                  `}
                >
                  {!uploadFile ? (
                    <div>
                      <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                      <p className="text-lg font-medium mb-2">
                        Drop an image or video here
                      </p>
                      <p className="text-sm text-muted-foreground mb-4">
                        or click to browse files
                      </p>
                      <input
                        type="file"
                        accept="image/*,video/*"
                        onChange={handleFileInput}
                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                      />
                      <Button variant="outline" className="pointer-events-none">
                        Select File
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {/* Preview */}
                      {uploadPreview && (
                        <div className="relative max-w-md mx-auto">
                          <img
                            src={uploadPreview}
                            alt="Preview"
                            className="rounded-lg max-h-64 mx-auto"
                          />
                          <Button
                            variant="destructive"
                            size="icon"
                            className="absolute top-2 right-2"
                            onClick={clearUpload}
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </div>
                      )}

                      {/* File Info */}
                      <div className="text-sm text-muted-foreground">
                        <p className="font-medium text-foreground">{uploadFile.name}</p>
                        <p>{(uploadFile.size / 1024 / 1024).toFixed(2)} MB</p>
                      </div>

                      {/* Success Message */}
                      {uploadSuccess && (
                        <div className="flex items-center justify-center gap-2 text-green-600">
                          <CheckCircle2 className="h-5 w-5" />
                          <span className="font-medium">Upload successful!</span>
                        </div>
                      )}

                      {/* Error Message */}
                      {uploadError && (
                        <div className="text-red-600 text-sm">
                          {uploadError}
                        </div>
                      )}

                      {/* Action Buttons */}
                      <div className="flex gap-3 justify-center">
                        <Button
                          onClick={handleSearchByImage}
                          disabled={isUploading}
                          variant="default"
                        >
                          {isUploading ? (
                            <>
                              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                              Searching...
                            </>
                          ) : (
                            <>
                              <Search className="mr-2 h-4 w-4" />
                              Find Similar
                            </>
                          )}
                        </Button>
                        <Button
                          onClick={handleUpload}
                          disabled={isUploading}
                          variant="secondary"
                        >
                          {isUploading ? (
                            <>
                              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                              Uploading...
                            </>
                          ) : (
                            <>
                              <Upload className="mr-2 h-4 w-4" />
                              Add to Database
                            </>
                          )}
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Stats */}
        {searchStats && (
          <div className="mb-4 flex gap-4">
            <Badge variant="secondary">
              {searchStats.count} results
            </Badge>
            {searchStats.search_time_ms && (
              <Badge variant="secondary">
                {searchStats.search_time_ms}ms
              </Badge>
            )}
          </div>
        )}

        {/* Error Display */}
        {error && (
          <Card className="mb-8 border-red-200 bg-red-50">
            <CardContent className="pt-6">
              <p className="text-red-600">{error}</p>
            </CardContent>
          </Card>
        )}

        {/* Results */}
        {isLoading ? (
          <div className="flex justify-center items-center py-20">
            <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
          </div>
        ) : results.length > 0 ? (
          <div>
            <h2 className="text-2xl font-bold mb-6">Search Results</h2>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {results.map((result, idx) => (
                <Card key={result.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-sm font-medium">
                        Result {idx + 1}
                      </CardTitle>
                      <Badge variant="outline" className="text-xs">
                        {(result.score * 100).toFixed(1)}%
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <p className="text-sm text-muted-foreground line-clamp-3">
                      {result.payload.text || result.payload.file_path || 'No description'}
                    </p>
                    {result.payload.tags && (
                      <div className="flex gap-1 flex-wrap">
                        {result.payload.tags.slice(0, 3).map((tag: string) => (
                          <Badge key={tag} variant="secondary" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    )}
                    {result.payload.media_type && (
                      <Badge variant="outline" className="text-xs">
                        {result.payload.media_type}
                      </Badge>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        ) : query || uploadFile ? (
          <Card>
            <CardContent className="py-20 text-center">
              <p className="text-muted-foreground text-lg">
                No results found. Try a different query or image.
              </p>
            </CardContent>
          </Card>
        ) : (
          <Card className="border-2 border-dashed">
            <CardContent className="py-20 text-center">
              <Search className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
              <p className="text-muted-foreground text-lg mb-2">
                Start searching
              </p>
              <p className="text-sm text-muted-foreground">
                Enter a text query or upload an image to find similar content
              </p>
            </CardContent>
          </Card>
        )}

        {/* Performance Stats */}
        {results.length > 0 && searchStats && (
          <Card className="mt-8 bg-gradient-to-r from-blue-50 to-purple-50">
            <CardHeader>
              <CardTitle className="text-lg">Performance Insights</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Search Time</p>
                  <p className="text-2xl font-bold">
                    {searchStats.search_time_ms || 0}ms
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Results</p>
                  <p className="text-2xl font-bold">{results.length}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Search Type</p>
                  <p className="text-2xl font-bold capitalize">{searchType}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Avg Confidence</p>
                  <p className="text-2xl font-bold">
                    {(results.reduce((sum, r) => sum + r.score, 0) / results.length * 100).toFixed(1)}%
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}