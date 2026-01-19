"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { fetchWithAuth } from "@/lib/api";
import { LucideClock, LucideDownload, LucideLoader2 } from "lucide-react";
import Link from "next/link";

interface SwapTask {
    id: int;
    type: string;
    template_url: string;
    result_url: string | null;
    status: string;
    created_at: string;
    cost: number;
}

export default function HistoryPage() {
    const { getToken, isLoaded, isSignedIn } = useAuth();
    const [tasks, setTasks] = useState<SwapTask[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!isLoaded || !isSignedIn) return;

        async function loadHistory() {
            try {
                const token = await getToken();
                const data = await fetchWithAuth("/swaps/history", token);
                setTasks(data.reverse()); // Newest first
            } catch (error) {
                console.error("Failed to load history", error);
            } finally {
                setLoading(false);
            }
        }

        loadHistory();
    }, [isLoaded, isSignedIn]);

    if (!isLoaded || loading) {
        return (
            <div className="flex h-[50vh] items-center justify-center">
                <LucideLoader2 className="animate-spin text-zinc-500" size={32} />
            </div>
        );
    }

    if (!isSignedIn) {
        return (
            <div className="flex h-[50vh] flex-col items-center justify-center gap-4 text-center">
                <h1 className="text-2xl font-bold">Please Sign In</h1>
                <p className="text-zinc-400">You need to be logged in to view your history.</p>
            </div>
        );
    }

    const getResultUrl = (path: string | null) => {
        if (!path) return "";
        if (path.startsWith("http")) return path;
        const backendUrl = process.env.NEXT_PUBLIC_API_URL?.replace("/api/v1", "") || "http://localhost:8000";
        return backendUrl + path;
    };

    return (
        <div className="container mx-auto px-4 py-12 mb-20">
            <h1 className="text-3xl font-bold mb-8 flex items-center gap-3">
                <LucideClock className="text-yellow-500" /> Swap History
            </h1>

            {tasks.length === 0 ? (
                <div className="text-center py-20 bg-zinc-900/50 rounded-3xl border border-white/5">
                    <p className="text-zinc-400 text-lg mb-4">No swaps yet.</p>
                    <Link href="/" className="bg-white text-black px-6 py-2 rounded-full font-bold hover:bg-zinc-200 transition-colors">
                        Create your first swap
                    </Link>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {tasks.map((task) => (
                        <div key={task.id} className="bg-zinc-900 border border-white/5 rounded-2xl overflow-hidden p-4 flex flex-col gap-4">
                            <div className="flex gap-4">
                                <div className="w-1/2 aspect-[3/4] rounded-lg overflow-hidden bg-black relative">
                                    <img src={task.template_url} className="w-full h-full object-cover opacity-70" alt="Template" />
                                    <span className="absolute bottom-2 left-2 text-[10px] bg-black/50 px-2 py-0.5 rounded text-white">Template</span>
                                </div>
                                <div className="w-1/2 aspect-[3/4] rounded-lg overflow-hidden bg-black relative border border-yellow-500/20">
                                    {task.result_url ? (
                                        task.type === 'VIDEO' ? (
                                            <video src={getResultUrl(task.result_url)} className="w-full h-full object-cover" />
                                        ) : (
                                            <img src={getResultUrl(task.result_url)} className="w-full h-full object-cover" alt="Result" />
                                        )
                                    ) : (
                                        <div className="w-full h-full flex items-center justify-center bg-zinc-800">
                                            {task.status === 'PENDING' ? (
                                                <LucideLoader2 className="animate-spin text-yellow-500" />
                                            ) : (
                                                <span className="text-red-500 text-xs font-bold">{task.status}</span>
                                            )}
                                        </div>
                                    )}
                                </div>
                            </div>

                            <div className="flex items-center justify-between mt-auto pt-4 border-t border-white/5">
                                <div className="flex flex-col">
                                    <span className="text-xs font-bold text-zinc-500 uppercase">{task.type} SWAP</span>
                                    <span className="text-xs text-zinc-600">{new Date(task.created_at).toLocaleDateString()}</span>
                                </div>

                                {task.result_url && (
                                    <a
                                        href={getResultUrl(task.result_url)}
                                        download
                                        target="_blank"
                                        className="p-2 bg-white text-black rounded-full hover:bg-zinc-200 transition-colors"
                                    >
                                        <LucideDownload size={16} />
                                    </a>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
