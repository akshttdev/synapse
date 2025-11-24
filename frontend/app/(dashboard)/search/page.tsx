        'use client';

        import { useState } from 'react';
        import { Search, Loader2 } from 'lucide-react';
        import { Input } from '@/components/ui/input';
        import { Button } from '@/components/ui/button';
        import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
        import { Badge } from '@/components/ui/badge';
        import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
        import { useSearch } from '@/lib/hooks/use-search';

        export default function SearchPage() {
          const [query, setQuery] = useState('');
          const [topK, setTopK] = useState(20);
          const [searchType, setSearchType] = useState<'vector' | 'hybrid'>('vector');

          const { search, results, isLoading, error, searchStats } = useSearch();

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

          return (
            <div className="min-h-screen bg-slate-50">
              {/* Header */}
              <header className="border-b bg-white">
                <div className="container mx-auto px-4 py-4">
                  <h1 className="text-2xl font-bold">Search</h1>
                </div>
              </header>

              <div className="container mx-auto px-4 py-8 max-w-6xl">
                {/* Search Bar */}
                <Card className="mb-8">
                  <CardContent className="pt-6">
                    <div className="flex gap-4">
                      <div className="flex-1 relative">
                        <Search className="absolute left-3 top-3 h-5 w-5 text-muted-foreground" />
                        <Input
                          type="text"
                          placeholder="Search for images..."
                          value={query}
                          onChange={(e) => setQuery(e.target.value)}
                          onKeyPress={handleKeyPress}
                          className="pl-10 h-12"
                        />
                      </div>

                      <Button
                        onClick={handleSearch}
                        disabled={isLoading || !query.trim()}
                        size="lg"
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

                    {/* Filters */}
                    <div className="flex gap-4 mt-4">
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-muted-foreground">Results:</span>
                        <Select value={topK.toString()} onValueChange={(v) => setTopK(parseInt(v))}>
                          <SelectTrigger className="w-24">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="10">10</SelectItem>
                            <SelectItem value="20">20</SelectItem>
                            <SelectItem value="50">50</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Stats */}
                {searchStats && (
                  <div className="mb-4 flex gap-4">
                    <Badge variant="secondary">{searchStats.count} results</Badge>
                    {searchStats.search_time_ms && (
                      <Badge variant="secondary">{searchStats.search_time_ms}ms</Badge>
                    )}
                  </div>
                )}

                {/* Error */}
                {error && (
                  <Card className="mb-8 border-red-200 bg-red-50">
                    <CardContent className="pt-6">
                      <p className="text-red-600">{error}</p>
                    </CardContent>
                  </Card>
                )}

                {/* Results */}
                {isLoading ? (
                  <div className="flex justify-center py-20">
                    <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
                  </div>
                ) : results.length > 0 ? (
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {results.map((result, idx) => (
                      <Card key={result.id} className="hover:shadow-lg transition-shadow">
                        <CardHeader>
                          <div className="flex items-center justify-between">
                            <CardTitle className="text-base">Result {idx + 1}</CardTitle>
                            <Badge variant="outline">
                              {(result.score * 100).toFixed(1)}%
                            </Badge>
                          </div>
                        </CardHeader>

                        <CardContent>
                          {/* ⬇ FIXED: Use metadata instead of payload */}
                          <p className="text-sm text-muted-foreground mb-2">
                            {result.metadata?.path ||
                              result.metadata?.thumbnail ||
                              'No description'}
                          </p>

                          {/* Optional Thumbnail */}
                          {result.metadata?.thumbnail && (
                            <img
                              src={`http://localhost:8000/thumbnails/${result.metadata.thumbnail}`}
                              alt="thumbnail"
                              className="rounded-md w-full h-auto mt-2"
                            />
                          )}
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                ) : query ? (
                  <Card>
                    <CardContent className="py-20 text-center">
                      <p className="text-muted-foreground">No results found.</p>
                    </CardContent>
                  </Card>
                ) : (
                  <Card>
                    <CardContent className="py-20 text-center">
                      <Search className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
                      <p className="text-muted-foreground text-lg">
                        Enter a search query to get started
                      </p>
                    </CardContent>
                  </Card>
                )}
              </div>
            </div>
          );
        }