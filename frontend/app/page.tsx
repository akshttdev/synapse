export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-black text-white">
      <h1 className="text-6xl font-extrabold mb-6">ScaleSearch</h1>
      <p className="text-gray-400 mb-10 text-lg">
        Multimodal AI Search Engine (Text + Image)
      </p>

      <a
        href="/dashboard/search"
        className="px-8 py-4 bg-white text-black text-lg rounded-xl font-semibold hover:bg-gray-200 transition"
      >
        🚀 Go to Search
      </a>
    </main>
  );
}
