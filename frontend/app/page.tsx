"use client";

import { Input } from "@/components/ui/input";
import { useTheme } from "next-themes";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";

export default function Home() {
  const { theme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Wait until theme is loaded on client
  useEffect(() => setMounted(true), []);

  if (!mounted) {
    // Avoid mismatched SSR vs client render
    return (
      <main className="flex h-screen w-full items-center justify-center bg-background text-foreground">
        <div className="h-10 w-10 animate-pulse rounded-full bg-muted" />
      </main>
    );
  }

  return (
    <main className="relative flex h-screen w-full flex-col items-center justify-center overflow-hidden bg-background text-foreground">
      {/* --- Background Gradient --- */}
      {theme === "light" ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="absolute inset-0 flex items-center justify-center"
        >
          <div className="pointer-events-none absolute h-[400px] w-[400px] rounded-full bg-gradient-to-br from-yellow-200 via-pink-200 to-purple-200 blur-[120px] opacity-60" />
        </motion.div>
      ) : (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="absolute inset-0 flex items-center justify-center"
        >
          <div className="pointer-events-none absolute h-[400px] w-[400px] rounded-full bg-gradient-to-br from-yellow-800 via-green-900 to-blue-900 blur-[120px] opacity-60" />
        </motion.div>
      )}

      {/* --- Content --- */}
      <div className="z-10 flex flex-col items-center gap-6 px-4 text-center">
        <h1 className="text-3xl font-medium sm:text-4xl">What can I help with?</h1>

        <div className="w-full max-w-lg">
          <Input
            type="text"
            placeholder="Ask me anything..."
            className="h-12 w-full rounded-2xl border border-border bg-card/70 px-4 text-base backdrop-blur-md placeholder:text-muted-foreground focus-visible:ring-1 focus-visible:ring-ring"
          />
        </div>

        <div className="flex flex-wrap items-center justify-center gap-2 text-sm text-muted-foreground">
          <span>Examples of queries:</span>
          <div className="flex flex-wrap justify-center gap-2">
            <button className="rounded-full border border-border/60 px-3 py-1 hover:bg-muted/20 transition">
              Explain quantum entanglement
            </button>
            <button className="rounded-full border border-border/60 px-3 py-1 hover:bg-muted/20 transition">
              Generate creative app names
            </button>
            <button className="rounded-full border border-border/60 px-3 py-1 hover:bg-muted/20 transition">
              Translate Latin phrases
            </button>
          </div>
        </div>
      </div>
    </main>
  );
}
