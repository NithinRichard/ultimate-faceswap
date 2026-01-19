"use client";

import Link from 'next/link';
import { LucideZap, LucideGrid, LucideHistory, LucideCreditCard } from 'lucide-react';
import { SignInButton, SignedIn, SignedOut, UserButton, useAuth } from "@clerk/nextjs";
import { useEffect, useState } from 'react';
import { fetchWithAuth } from '@/lib/api';

export function Navbar() {
    const { getToken, isSignedIn } = useAuth();
    const [gems, setGems] = useState<number | null>(null);

    useEffect(() => {
        const fetchGems = async () => {
            if (!isSignedIn) return;
            try {
                const token = await getToken();
                const res = await fetchWithAuth("/users/balance", token);
                if (res.gem_balance !== undefined) {
                    setGems(res.gem_balance);
                }
            } catch (error) {
                console.error("Failed to fetch gems", error);
            }
        };

        fetchGems();
        // Poll every 10 seconds to keep updated (simple live update)
        const interval = setInterval(fetchGems, 10000);
        return () => clearInterval(interval);
    }, [isSignedIn, getToken]);

    return (
        <nav className="border-b border-white/10 bg-black/50 backdrop-blur-md sticky top-0 z-50">
            <div className="container mx-auto px-4 h-16 flex items-center justify-between">
                <Link href="/" className="flex items-center gap-2 font-bold text-xl tracking-tighter">
                    <LucideZap className="text-yellow-400 fill-yellow-400" />
                    <span>ULTIMATE FACESWAP</span>
                </Link>

                <div className="hidden md:flex items-center gap-8 text-sm font-medium text-zinc-400">
                    <Link href="/" className="hover:text-white transition-colors flex items-center gap-2">
                        <LucideGrid size={18} />
                        Templates
                    </Link>
                    <Link href="/history" className="hover:text-white transition-colors flex items-center gap-2">
                        <LucideHistory size={18} />
                        My Swaps
                    </Link>
                    <Link href="/buy-gems" className="hover:text-white transition-colors flex items-center gap-2">
                        <LucideCreditCard size={18} />
                        Buy Gems
                    </Link>
                </div>

                <div className="flex items-center gap-4">
                    <SignedIn>
                        <div className="bg-zinc-800 px-3 py-1 rounded-full text-xs font-bold text-yellow-500 border border-yellow-500/20">
                            {gems !== null ? `${gems} GEMS` : "..."}
                        </div>
                        <UserButton afterSignOutUrl="/" />
                    </SignedIn>
                    <SignedOut>
                        <SignInButton mode="modal">
                            <button className="bg-white text-black px-4 py-2 rounded-lg text-sm font-bold hover:bg-zinc-200 transition-colors">
                                Login
                            </button>
                        </SignInButton>
                    </SignedOut>
                </div>
            </div>
        </nav>
    );
}
