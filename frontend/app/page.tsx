import Link from 'next/link';
import { Search, Zap, Cpu, Upload, Play, Image as ImageIcon } from 'lucide-react';
import GradientBlinds from '@/components/GradientBlinds';

export default function LandingPage() {
  return (

    
    <div className="min-h-screen bg-[#09090b] text-white">
      {/* Header */}
      <header className="border-b border-white/10 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-6 h-6 text-white">
              <svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                <path d="M4 42.4379C4 42.4379 14.0962 36.0744 24 41.1692C35.0664 46.8624 44 42.2078 44 42.2078L44 7.01134C44 7.01134 35.068 11.6577 24.0031 5.96913C14.0971 0.876274 4 7.27094 4 7.27094L4 42.4379Z" fill="currentColor"></path>
              </svg>
            </div>
            <h2 className="text-lg font-bold tracking-tight">Synapse</h2>
          </div>
          
          <div className="hidden md:flex items-center gap-8">
            <nav className="flex items-center gap-8">
              <a href="#features" className="text-white/80 hover:text-white transition-colors text-sm font-medium">
                Features
              </a>
              <a href="#how-it-works" className="text-white/80 hover:text-white transition-colors text-sm font-medium">
                How It Works
              </a>
            </nav>
            <Link href="/search">
              <button className="px-4 h-10 bg-white text-black rounded-xl text-sm font-bold hover:bg-white/90 transition-colors">
                Open Dashboard
              </button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-6">
        <GradientBlinds
    gradientColors={['#FF9FFC', '#5227FF']}
    angle={0}
    noise={0.3}
    blindCount={12}
    blindMinWidth={50}
    spotlightRadius={0.5}
    spotlightSoftness={1}
    spotlightOpacity={1}
    mouseDampening={0.15}
    distortAmount={0}
    shineDirection="left"
    mixBlendMode="lighten"
    z-index ={-1}
  />
        <section className="min-h-[60vh] flex flex-col items-center justify-center text-center py-20 md:py-32">
          <div className="flex flex-col gap-6">
            <h1 className="text-5xl md:text-7xl font-black tracking-tighter leading-tight">
              Search Beyond Text with{' '}
              <span className="bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent">
                Synapse
              </span>
            </h1>
            <h2 className="text-white/70 text-lg md:text-xl font-normal max-w-2xl mx-auto leading-relaxed">
              Unlock the power of your data with a system that understands images, audio, and text as one.
            </h2>
          </div>
          
          <div className="flex flex-wrap gap-3 justify-center mt-8">
            <Link href="/search">
              <button className="px-6 h-12 bg-white text-black rounded-2xl text-base font-bold hover:bg-white/90 transition-colors">
                Open Dashboard
              </button>
            </Link>
            <button className="px-6 h-12 bg-transparent border border-white/20 rounded-2xl text-base font-bold hover:bg-white/10 transition-colors">
              Documentation
            </button>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="py-16 md:py-24">
          <h4 className="text-white/60 text-sm font-bold tracking-wide text-center mb-8">
            Powerful By Design
          </h4>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="flex flex-col gap-4 rounded-2xl border border-white/10 bg-white/5 p-6">
              <Search className="w-8 h-8 text-white" />
              <div className="flex flex-col gap-2">
                <h3 className="text-lg font-bold">Multimodal Search</h3>
                <p className="text-white/60 text-sm leading-relaxed">
                  Query using any data type—text, images, or audio—to find the most relevant results across your entire dataset.
                </p>
              </div>
            </div>
            
            <div className="flex flex-col gap-4 rounded-2xl border border-white/10 bg-white/5 p-6">
              <Zap className="w-8 h-8 text-white" />
              <div className="flex flex-col gap-2">
                <h3 className="text-lg font-bold">Instant Vector Results</h3>
                <p className="text-white/60 text-sm leading-relaxed">
                  Experience near-instantaneous search results, powered by a highly optimized vector database.
                </p>
              </div>
            </div>
            
            <div className="flex flex-col gap-4 rounded-2xl border border-white/10 bg-white/5 p-6">
              <Cpu className="w-8 h-8 text-white" />
              <div className="flex flex-col gap-2">
                <h3 className="text-lg font-bold">GPU Embedding Pipeline</h3>
                <p className="text-white/60 text-sm leading-relaxed">
                  Leverage our powerful, scalable infrastructure to turn your raw data into searchable embeddings at scale.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* How It Works */}
        <section id="how-it-works" className="py-16 md:py-24 text-center">
          <h4 className="text-white/60 text-sm font-bold tracking-wide mb-2">
            How It Works
          </h4>
          <h3 className="text-3xl md:text-4xl font-bold mb-12">
            Simple. Fast. Effective.
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
            {/* Connecting Line */}
            <div className="hidden md:block absolute top-12 left-0 w-full h-px">
              <svg className="w-full h-full" preserveAspectRatio="none">
                <line
                  x1="0"
                  y1="1"
                  x2="100%"
                  y2="1"
                  stroke="#27272a"
                  strokeWidth="2"
                  strokeDasharray="8 8"
                />
              </svg>
            </div>
            
            <div className="flex flex-col items-center gap-4 relative z-10">
              <div className="flex h-12 w-12 items-center justify-center rounded-full border-2 border-white/20 bg-[#09090b] text-white font-bold text-xl">
                1
              </div>
              <Upload className="w-6 h-6 text-white/60" />
              <h3 className="text-lg font-bold">Upload Media</h3>
              <p className="text-white/60 text-sm max-w-xs">
                Submit your images, audio files, or text documents through our secure API or dashboard.
              </p>
            </div>
            
            <div className="flex flex-col items-center gap-4 relative z-10">
              <div className="flex h-12 w-12 items-center justify-center rounded-full border-2 border-white/20 bg-[#09090b] text-white font-bold text-xl">
                2
              </div>
              <Cpu className="w-6 h-6 text-white/60" />
              <h3 className="text-lg font-bold">AI Analyzes</h3>
              <p className="text-white/60 text-sm max-w-xs">
                Our system processes and converts your data into rich, searchable vector embeddings in real-time.
              </p>
            </div>
            
            <div className="flex flex-col items-center gap-4 relative z-10">
              <div className="flex h-12 w-12 items-center justify-center rounded-full border-2 border-white/20 bg-[#09090b] text-white font-bold text-xl">
                3
              </div>
              <Search className="w-6 h-6 text-white/60" />
              <h3 className="text-lg font-bold">Get Results</h3>
              <p className="text-white/60 text-sm max-w-xs">
                Perform complex, cross-modal searches and receive highly relevant results in milliseconds.
              </p>
            </div>
          </div>
        </section>

        {/* Who It's For */}
        <section className="py-16 md:py-24 text-center">
          <h4 className="text-white/60 text-sm font-bold tracking-wide mb-2">
            Who It's For
          </h4>
          <h3 className="text-3xl md:text-4xl font-bold mb-12">
            Built for Innovators
          </h3>
          
          <div className="flex flex-wrap justify-center gap-3">
            {['Developers', 'Data Scientists', 'AI Researchers', 'Product Managers', 'Enterprise Teams'].map((role) => (
              <span
                key={role}
                className="rounded-full border border-white/20 bg-white/10 px-4 py-2 text-sm font-medium"
              >
                {role}
              </span>
            ))}
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-16 md:py-24">
          <div className="flex flex-col items-center justify-center gap-6 rounded-2xl bg-white/5 border border-white/10 p-8 md:p-16 text-center">
            <h2 className="text-3xl md:text-5xl font-bold tracking-tight leading-tight">
              Ready to try the future of search?
            </h2>
            <Link href="/dashboard">
              <button className="px-8 h-12 bg-white text-black rounded-2xl text-base font-bold hover:bg-white/90 transition-colors mt-4">
                Open Dashboard
              </button>
            </Link>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 py-8 mt-16">
        <div className="max-w-7xl mx-auto px-6 text-center text-white/60 text-sm">
          <p>© 2024 Synapse. Built with ImageBind & Qdrant.</p>
        </div>
      </footer>
    </div>
  );
}