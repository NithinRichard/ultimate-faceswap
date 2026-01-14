"use client";

import { useParams } from "next/navigation";
import { useState, useEffect } from "react";
import { LucideUpload, LucideZap, LucideCheckCircle, LucideLoader2, LucideAlertCircle } from "lucide-react";
import Link from "next/link";
import { useAuth } from "@clerk/nextjs";
import { uploadFile, fetchWithAuth } from "@/lib/api";
import { Template } from "@/types";

export default function SwapPage() {
    const { id } = useParams();
    const { getToken, isLoaded, isSignedIn } = useAuth();

    const [template, setTemplate] = useState<Template | null>(null);
    const [loadingTemplate, setLoadingTemplate] = useState(true);

    useEffect(() => {
        const fetchTemplate = async () => {
            try {
                // Fetch template details. Since templates are public, we might not need auth, but api client currently assumes auth helper.
                // Let's use standard fetch for public template info or fetchWithAuth if we want.
                // Templates endpoint is public.
                const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
                const res = await fetch(`${apiUrl}/templates/${id}`);
                if (res.ok) {
                    const data = await res.json();
                    setTemplate(data);
                } else {
                    console.error("Template not found");
                }
            } catch (err) {
                console.error(err);
            } finally {
                setLoadingTemplate(false);
            }
        };
        if (id) fetchTemplate();
    }, [id]);

    const [sourceFile, setSourceFile] = useState<File | null>(null);
    const [isSwapping, setIsSwapping] = useState(false);
    // const [progress, setProgress] = useState(0); // Real progress is hard without websockets, we'll use a spinner or poll status
    const [result, setResult] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [statusMessage, setStatusMessage] = useState<string>("");

    if (loadingTemplate) return <div className="text-center py-20">Loading template...</div>;
    if (!template) return <div className="text-center py-20">Template not found</div>;

    const handleSwap = async () => {
        if (!isLoaded || !isSignedIn) {
            alert("Please sign in first!");
            return;
        }
        if (!sourceFile) return;

        setIsSwapping(true);
        setError(null);
        setResult(null);
        setStatusMessage("Uploading source image...");

        try {
            const token = await getToken();
            if (!token) throw new Error("No authentication token");

            // 1. Upload Source
            const uploadRes = await uploadFile(sourceFile, token);
            const sourceUrl = uploadRes.url;

            setStatusMessage("Queueing swap task...");

            // 2. Create Swap Task
            const createRes = await fetchWithAuth("/swaps/", token, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    type: template.type.toUpperCase(), // IMAGE or VIDEO
                    source_url: sourceUrl,
                    template_url: template.source_url || template.thumbnail, // Use source_url if available (video), else thumbnail (image)
                }),
            });

            const taskId = createRes.id;

            // 3. Poll for result
            setStatusMessage("Processing... (This may take 10-20 seconds)");

            const pollInterval = setInterval(async () => {
                try {
                    const task = await fetchWithAuth(`/swaps/${taskId}`, token);

                    if (task.status === "COMPLETED") {
                        clearInterval(pollInterval);
                        setIsSwapping(false);
                        // The backend returns a relative path like /static/results/..., we need to prepend API base if it's on a different port/domain
                        // But since we use a proxy or direct URL, let's assume valid URL or prepend backend host
                        // For MVP: Prepend backend URL
                        const backendUrl = process.env.NEXT_PUBLIC_API_URL?.replace("/api/v1", "") || "http://localhost:8000";
                        setResult(backendUrl + task.result_url);
                    } else if (task.status === "FAILED") {
                        clearInterval(pollInterval);
                        setIsSwapping(false);
                        setError(task.error_message || "Swap failed");
                    }
                } catch (e) {
                    // Ignore transient polling errors
                    console.error("Polling error", e);
                }
            }, 2000);

        } catch (err: any) {
            console.error(err);
            setError(err.message || "Something went wrong");
            setIsSwapping(false);
        }
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
                            {template.type} Template
                        </div>
                    </div>
                </div>

                {/* Right: Upload & Action */}
                <div className="flex flex-col gap-8 justify-center">
                    {!result ? (
                        <div className="flex flex-col gap-6">
                            <div className="space-y-2">
                                <h2 className="text-3xl font-bold tracking-tight">Upload Source Face</h2>
                                <p className="text-zinc-400">Choose a clear photo of the face you want to swap.</p>
                            </div>

                            <label className="border-2 border-dashed border-white/10 rounded-3xl p-12 flex flex-col items-center gap-4 hover:bg-zinc-900/50 hover:border-white/20 transition-all cursor-pointer group">
                                <input
                                    type="file"
                                    className="hidden"
                                    accept="image/*"
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

                            {error && (
                                <div className="bg-red-500/10 border border-red-500/20 text-red-500 p-4 rounded-xl flex items-center gap-3">
                                    <LucideAlertCircle size={20} />
                                    {error}
                                </div>
                            )}

                            <button
                                disabled={!sourceFile || isSwapping}
                                onClick={handleSwap}
                                className="w-full py-4 bg-yellow-500 text-black font-black rounded-2xl hover:bg-yellow-400 transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed text-lg"
                            >
                                {isSwapping ? (
                                    <><LucideLoader2 className="animate-spin" /> {statusMessage}</>
                                ) : (
                                    <><LucideZap fill="currentColor" /> Swap Now ({template.cost} Gems)</>
                                )}
                            </button>
                        </div>
                    ) : (
                        <div className="flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
                            <div className="flex items-center gap-3 text-green-500">
                                <LucideCheckCircle size={32} />
                                <h2 className="text-3xl font-bold">Swap Complete!</h2>
                            </div>

                            <div className="relative aspect-square rounded-3xl overflow-hidden border-4 border-yellow-500/50 shadow-2xl shadow-yellow-500/10">
                                {/* If it's a video, use video tag, else img */}
                                {template.type === 'VIDEO' ? (
                                    <video src={result} controls className="w-full h-full object-cover" />
                                ) : (
                                    <img src={result} className="w-full h-full object-cover" alt="Result" />
                                )}
                            </div>

                            <div className="flex gap-4">
                                <a href={result} download target="_blank" className="flex-1 py-4 bg-white text-black font-bold rounded-2xl hover:bg-zinc-200 transition-all text-center flex items-center justify-center">
                                    Download Result
                                </a>
                                <button
                                    onClick={() => { setResult(null); }}
                                    className="flex-1 py-4 bg-zinc-900 border border-white/10 font-bold rounded-2xl hover:bg-zinc-800 transition-all"
                                >
                                    Swap Again
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            <div className="mt-16 text-center">
                <Link href="/" className="text-zinc-500 hover:text-white transition-colors text-sm font-medium underline underline-offset-4">
                    Back to Templates
                </Link>
            </div>
        </div>
    );
}

