import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Search, Upload, BarChart3, Zap } from 'lucide-react'

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      {/* Header */}
      <header className="border-b bg-white/50 backdrop-blur-sm dark:bg-slate-900/50">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600" />
              <h1 className="text-2xl font-bold">Multimodal Retrieval</h1>
            </div>
            <Link href="/search">
              <Button>Get Started</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="mx-auto max-w-3xl text-center">
          <h2 className="mb-6 text-5xl font-bold tracking-tight">
            Lightning-Fast
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              {' '}Multimodal Search
            </span>
          </h2>
          <p className="mb-8 text-xl text-muted-foreground">
            Search billions of images and videos in milliseconds using state-of-the-art AI.
            Built for scale, optimized for speed.
          </p>
          <div className="flex gap-4 justify-center">
            <Link href="/search">
              <Button size="lg" className="gap-2">
                <Search className="h-5 w-5" />
                Start Searching
              </Button>
            </Link>
            <Link href="/upload">
              <Button size="lg" variant="outline" className="gap-2">
                <Upload className="h-5 w-5" />
                Upload Media
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="container mx-auto px-4 py-20">
        <div className="grid gap-6 md:grid-cols-3">
          <Card>
            <CardHeader>
              <Zap className="mb-2 h-8 w-8 text-blue-600" />
              <CardTitle>Blazing Fast</CardTitle>
              <CardDescription>
                Sub-50ms search latency with HNSW indexing and multi-layer caching
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• Product Quantization (16x compression)</li>
                <li>• Redis multi-layer cache</li>
                <li>• Optimized vector search</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Search className="mb-2 h-8 w-8 text-purple-600" />
              <CardTitle>Multimodal AI</CardTitle>
              <CardDescription>
                Search using text, images, or videos with ImageBind embeddings
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• Text-to-image search</li>
                <li>• Image-to-image similarity</li>
                <li>• Video frame analysis</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <BarChart3 className="mb-2 h-8 w-8 text-green-600" />
              <CardTitle>Production Ready</CardTitle>
              <CardDescription>
                Built with scalability and reliability in mind
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• Horizontal scaling</li>
                <li>• Real-time monitoring</li>
                <li>• 99.9% uptime</li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Stats */}
      <section className="container mx-auto px-4 py-20">
        <div className="rounded-2xl bg-gradient-to-r from-blue-600 to-purple-600 p-12 text-white">
          <div className="grid gap-8 md:grid-cols-4 text-center">
            <div>
              <div className="text-4xl font-bold">{'<50ms'}</div>
              <div className="text-blue-100">Search Latency</div>
            </div>
            <div>
              <div className="text-4xl font-bold">1B+</div>
              <div className="text-blue-100">Vectors Indexed</div>
            </div>
            <div>
              <div className="text-4xl font-bold">16x</div>
              <div className="text-blue-100">Compression Ratio</div>
            </div>
            <div>
              <div className="text-4xl font-bold">{'85%'}</div>
              <div className="text-blue-100">Cache Hit Rate</div>
            </div>
          </div>
        </div>
      </section>
    </main>
  )
}
