import { LucideCheck, LucideZap, LucideShieldCheck, LucideSparkles } from "lucide-react";

const PACKAGES = [
    {
        name: "Starter",
        gems: 10,
        price: "$9",
        description: "Perfect for a few quick swaps",
        features: ["10 Image Swaps", "1 Video Swap", "Standard Support"],
        popular: false
    },
    {
        name: "Pro",
        gems: 50,
        price: "$29",
        description: "Best for content creators",
        features: ["50 Image Swaps", "5 Video Swaps", "Priority Processing", "High Quality Video"],
        popular: true
    },
    {
        name: "Elite",
        gems: 200,
        price: "$79",
        description: "Unlimited creative power",
        features: ["200 Image Swaps", "20 Video Swaps", "Instant Processing", "24/7 VIP Support"],
        popular: false
    }
];

export default function BuyGems() {
    return (
        <div className="container mx-auto px-4 py-16 flex flex-col gap-12">
            <div className="text-center max-w-2xl mx-auto space-y-4">
                <h1 className="text-4xl md:text-5xl font-black tracking-tight">Refill Your Gems</h1>
                <p className="text-zinc-400 text-lg">
                    Choose a package to continue creating magic. Gems are added to your account instantly after purchase.
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
                {PACKAGES.map((pkg) => (
                    <div
                        key={pkg.name}
                        className={`relative flex flex-col p-8 rounded-3xl border transition-all hover:scale-[1.02] ${pkg.popular
                                ? "bg-zinc-900 border-yellow-500/50 shadow-2xl shadow-yellow-500/5"
                                : "bg-black border-white/10 hover:border-white/20"
                            }`}
                    >
                        {pkg.popular && (
                            <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-yellow-500 text-black px-4 py-1 rounded-full text-xs font-black uppercase tracking-wider">
                                Most Popular
                            </div>
                        )}

                        <div className="mb-8">
                            <h3 className="text-xl font-bold mb-2">{pkg.name}</h3>
                            <div className="flex items-baseline gap-1">
                                <span className="text-4xl font-black">{pkg.price}</span>
                                <span className="text-zinc-500 text-sm font-medium">/ one-time</span>
                            </div>
                            <div className="mt-4 flex items-center gap-2 text-yellow-500 font-bold">
                                <LucideZap size={18} fill="currentColor" />
                                {pkg.gems} Gems Included
                            </div>
                        </div>

                        <p className="text-zinc-400 text-sm mb-8">{pkg.description}</p>

                        <ul className="space-y-4 mb-12 flex-1">
                            {pkg.features.map((feature) => (
                                <li key={feature} className="flex gap-3 text-sm text-zinc-300">
                                    <LucideCheck size={18} className="text-green-500 shrink-0" />
                                    {feature}
                                </li>
                            ))}
                        </ul>

                        <button className={`w-full py-4 rounded-2xl font-bold transition-all ${pkg.popular
                                ? "bg-yellow-500 text-black hover:bg-yellow-400"
                                : "bg-white text-black hover:bg-zinc-200"
                            }`}>
                            Buy Now
                        </button>
                    </div>
                ))}
            </div>

            {/* Trust Badges */}
            <div className="flex flex-wrap justify-center gap-8 md:gap-16 opacity-50 mt-8">
                <div className="flex items-center gap-2 grayscale">
                    <LucideShieldCheck size={20} />
                    <span className="text-sm font-bold tracking-tighter">SECURE PAYMENTS</span>
                </div>
                <div className="flex items-center gap-2 grayscale">
                    <LucideSparkles size={20} />
                    <span className="text-sm font-bold tracking-tighter">AI POWERED</span>
                </div>
            </div>
        </div>
    );
}
