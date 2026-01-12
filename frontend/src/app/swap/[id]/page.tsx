"use client";

import { useParams } from "next/navigation";
import { TEMPLATES } from "@/lib/templates";
import { useState } from "react";
import { LucideUpload, LucideZap, LucideCheckCircle, LucideLoader2 } from "lucide-react";
import Link from "next/link";

export default function SwapPage() {
    const { id } = useParams();
    const template = TEMPLATES.find(t => t.id === id);
    const [sourceFile, setSourceFile] = useState<File | null>(null);
    const [isSwapping, setIsSwapping] = useState(false);
    const [progress, setProgress] = useState(0);
    const [result, setResult] = useState<string | null>(null);

    if (!template) return <div>Template not found</div>;

    const handleSwap = () => {
        setIsSwapping(true);
        // Mock progression
        let p = 0;
        const interval = setInterval(() => {
            p += 5;
            setProgress(p);
            if (p >= 100) {
                clearInterval(interval);
                setIsSwapping(false);
                setResult(template.thumbnail); // Mock result
            }
        }, 200);
    };

    return (
        <div className="container mx-auto px-4 py-12 max-w-5xl">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                {/* Left: Template Preview */}
                <div className="flex flex-col gap-4">
                    <div className="relative aspect-[3/4] rounded-3xl overflow-hidden border border-white/10 bg-zinc-900">
                        <img
                            src={template.thumbnail}
                            className="w-full h-full object-cover"
                            alt="Template"
                        />
                        <div className="absolute top-4 left-4 bg-black/60 backdrop-blur-md px-3 py-1.5 rounded-xl border border-white/10 text-xs font-bold uppercase tracking-widest">
                            Template
                        </div>
                    </div>
                    <div className="flex items-center justify-between px-2">
                        <div>
                            <h1 className="text-xl font-bold">{template.title}</h1>
                            <p className="text-zinc-500 text-sm capitalize">{template.type} Template</p>
                        </div>
                        <div className="text-right">
                            <p className="text-sm font-medium text-zinc-400">Cost</p>
                            <p className="text-lg font-black text-yellow-500">{template.cost} Gems</p>
                        </div>
                    </div>
                </div>

                {/* Right: Upload & Action */}
                <div className="flex flex-col gap-8 justify-center">
                    {!result ? (
                        <div className="flex flex-col gap-6">
                            <div className="space-y-2">
                                <h2 className="text-3xl font-bold tracking-tight">Upload Source Face</h2>
                                <p className="text-zinc-400">Choose a clear photo of the face you want to swap. Front-facing with good lighting works best.</p>
                            </div>

                            <label className="border-2 border-dashed border-white/10 rounded-3xl p-12 flex flex-col items-center gap-4 hover:bg-zinc-900/50 hover:border-white/20 transition-all cursor-pointer group">
                                <input
                                    type="file"
                                    className="hidden"
                                    onChange={(e) => setSourceFile(e.target.files?.[0] || null)}
                                />
                                <div className="w-16 h-16 rounded-full bg-zinc-800 flex items-center justify-center group-hover:scale-110 transition-transform">
                                    <LucideUpload className="text-zinc-400" />
                                </div>
                                <div className="text-center">
                                    <p className="font-bold">{sourceFile ? sourceFile.name : "Choose File"}</p>
                                    <p className="text-xs text-zinc-500 mt-1">PNG, JPG up to 10MB</p>
                                </div>
                            </label>

                            <button
                                disabled={!sourceFile || isSwapping}
                                onClick={handleSwap}
                                className="w-full py-4 bg-yellow-500 text-black font-black rounded-2xl hover:bg-yellow-400 transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed text-lg"
                            >
                                {isSwapping ? (
                                    <><LucideLoader2 className="animate-spin" /> Processing {progress}%</>
                                ) : (
                                    <><LucideZap fill="currentColor" /> Swap Now</>
                                )}
                            </button>

                            {isSwapping && (
                                <div className="w-full bg-zinc-800 h-2 rounded-full overflow-hidden">
                                    <div
                                        className="bg-yellow-500 h-full transition-all duration-300"
                                        style={{ width: `${progress}%` }}
                                    />
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
                            <div className="flex items-center gap-3 text-green-500">
                                <LucideCheckCircle size={32} />
                                <h2 className="text-3xl font-bold">Swap Complete!</h2>
                            </div>

                            <div className="relative aspect-square rounded-3xl overflow-hidden border-4 border-yellow-500/50 shadow-2xl shadow-yellow-500/10">
                                <img src={result} className="w-full h-full object-cover" alt="Result" />
                            </div>

                            <div className="flex gap-4">
                                <button className="flex-1 py-4 bg-white text-black font-bold rounded-2xl hover:bg-zinc-200 transition-all">
                                    Download Result
                                </button>
                                <button
                                    onClick={() => { setResult(null); setProgress(0); }}
                                    className="flex-1 py-4 bg-zinc-900 border border-white/10 font-bold rounded-2xl hover:bg-zinc-800 transition-all"
                                >
                                    Swap Again
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* History Back Link */}
            <div className="mt-16 text-center">
                <Link href="/" className="text-zinc-500 hover:text-white transition-colors text-sm font-medium underline underline-offset-4">
                    Back to Templates
                </Link>
            </div>
        </div>
    );
}
