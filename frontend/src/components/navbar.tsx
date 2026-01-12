import Link from 'next/link';
import { LucideZap, LucideGrid, LucideHistory, LucideCreditCard, LucideUser } from 'lucide-react';

export function Navbar() {
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
                    <div className="bg-zinc-800 px-3 py-1 rounded-full text-xs font-bold text-yellow-500 border border-yellow-500/20">
                        5 GEMS
                    </div>
                    <button className="bg-white text-black px-4 py-2 rounded-lg text-sm font-bold hover:bg-zinc-200 transition-colors">
                        Login
                    </button>
                </div>
            </div>
        </nav>
    );
}
