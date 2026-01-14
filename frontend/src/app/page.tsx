import Link from "next/link";
import { LucideVideo, LucideImage, LucideArrowRight, LucideAlertCircle } from "lucide-react";
import { Template } from "@/types";

async function getTemplates(): Promise<Template[]> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
  try {
    // If running server side, we might need internal container URL or localhost
    // But NEXT_PUBLIC_API_URL usually points to external. 
    // In dev environment with both on localhost, this is fine.
    const res = await fetch(`${apiUrl}/templates/`, { cache: 'no-store' });
    if (!res.ok) {
      throw new Error('Failed to fetch templates');
    }
    return res.json();
  } catch (error) {
    console.error("Error fetching templates:", error);
    return [];
  }
}

export default async function Home() {
  const templates = await getTemplates();

  return (
    <div className="flex flex-col gap-16 py-12 container mx-auto px-4">
      {/* Hero Section */}
      <section className="text-center flex flex-col items-center gap-6 max-w-3xl mx-auto">
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tighter bg-gradient-to-b from-white to-zinc-500 bg-clip-text text-transparent">
          Face Swap Everything.
        </h1>
        <p className="text-zinc-400 text-lg md:text-xl">
          Create professional AI faceswaps for images and videos in seconds.
          Powered by InsightFace and FaceFusion.
        </p>
        <div className="flex gap-4">
          <button className="bg-white text-black px-8 py-3 rounded-full font-bold hover:bg-zinc-200 transition-all flex items-center gap-2">
            Get Started <LucideArrowRight size={20} />
          </button>
          <button className="bg-zinc-900 border border-white/10 px-8 py-3 rounded-full font-bold hover:bg-zinc-800 transition-all">
            View Pricing
          </button>
        </div>
      </section>

      {/* Template Grid */}
      <section className="flex flex-col gap-8">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold tracking-tight">Image & Video Templates</h2>
          <div className="flex gap-2">
            <button className="bg-zinc-900 px-4 py-1.5 rounded-md text-sm font-medium border border-white/5 hover:border-white/20 transition-all">All</button>
            <button className="text-zinc-500 px-4 py-1.5 rounded-md text-sm font-medium hover:text-white transition-all">Videos</button>
            <button className="text-zinc-500 px-4 py-1.5 rounded-md text-sm font-medium hover:text-white transition-all">Images</button>
          </div>
        </div>

        {templates.length === 0 ? (
          <div className="text-center py-12 border border-dashed border-white/10 rounded-2xl">
            <p className="text-zinc-500">No templates found. Is the backend running?</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {templates.map((template) => (
              <Link
                key={template.id}
                href={`/swap/${template.id}`}
                className="group relative bg-zinc-900 rounded-2xl overflow-hidden border border-white/5 hover:border-white/20 transition-all hover:scale-[1.02]"
              >
                <div className="aspect-[3/4] relative">
                  <img
                    src={template.thumbnail}
                    alt={template.title}
                    className="w-full h-full object-cover grayscale-[0.5] group-hover:grayscale-0 transition-all duration-500"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-60 group-hover:opacity-100 transition-opacity" />

                  <div className="absolute top-3 left-3 flex gap-2">
                    <div className="bg-black/60 backdrop-blur-md px-2 py-1 rounded-lg flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider border border-white/10">
                      {template.type === 'VIDEO' ? <LucideVideo size={12} className="text-blue-400" /> : <LucideImage size={12} className="text-green-400" />}
                      {template.type}
                    </div>
                  </div>

                  <div className="absolute bottom-4 left-4 right-4">
                    <p className="text-sm font-bold text-white mb-1 group-hover:translate-x-1 transition-transform">{template.title}</p>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-zinc-400">{template.cost} Gems</span>
                      <span className="bg-yellow-500/10 text-yellow-500 px-2 py-0.5 rounded text-[10px] font-extrabold border border-yellow-500/20 opacity-0 group-hover:opacity-100 transition-opacity">
                        SWAP NOW
                      </span>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
