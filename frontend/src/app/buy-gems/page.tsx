"use client";

import { LucideCheck, LucideZap, LucideShieldCheck, LucideSparkles, LucideLoader2 } from "lucide-react";
import { useAuth } from "@clerk/nextjs";
import { fetchWithAuth } from "@/lib/api";
import { useState } from "react";
import { useRouter } from "next/navigation";

const RAZORPAY_KEY = process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID;

const PACKAGES = [
    {
        name: "Starter",
        gems: 10,
        price: 99,
        priceStr: "₹99",
        description: "Perfect for a few quick swaps",
        features: ["10 Image Swaps", "1 Video Swap", "Standard Support"],
        popular: false
    },
    {
        name: "Pro",
        gems: 50,
        price: 399,
        priceStr: "₹399",
        description: "Best for content creators",
        features: ["50 Image Swaps", "5 Video Swaps", "Priority Processing", "High Quality Video"],
        popular: true
    },
    {
        name: "Elite",
        gems: 200,
        price: 999,
        priceStr: "₹999",
        description: "Unlimited creative power",
        features: ["200 Image Swaps", "20 Video Swaps", "Instant Processing", "24/7 VIP Support"],
        popular: false
    }
];

// Add Razorpay type
declare global {
    interface Window {
        Razorpay: any;
    }
}

export default function BuyGems() {
    const { getToken, isSignedIn, isLoaded } = useAuth();
    const router = useRouter();
    const [loadingPackage, setLoadingPackage] = useState<string | null>(null);

    const loadRazorpay = () => {
        return new Promise((resolve) => {
            const script = document.createElement("script");
            script.src = "https://checkout.razorpay.com/v1/checkout.js";
            script.onload = () => resolve(true);
            script.onerror = () => resolve(false);
            document.body.appendChild(script);
        });
    };

    const handleBuy = async (pkg: typeof PACKAGES[0]) => {
        if (!isLoaded) return;
        if (!isSignedIn) {
            alert("Please sign in first!");
            return;
        }

        const res = await loadRazorpay();
        if (!res) {
            alert("Razorpay SDK failed to load. Are you online?");
            return;
        }

        setLoadingPackage(pkg.name);
        try {
            const token = await getToken();

            // 1. Create Order on Backend
            const orderRes = await fetchWithAuth("/payments/create-order", token, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    package_name: pkg.name,
                    gems: pkg.gems,
                    price_inr: pkg.price // Backend expects INR
                }),
            });

            const options = {
                key: RAZORPAY_KEY, // Enter the Key ID generated from the Dashboard
                amount: orderRes.amount,
                currency: orderRes.currency,
                name: "Ultimate Faceswap",
                description: `Purchase ${pkg.gems} Gems`,
                image: "https://your-logo-url", // Optional
                order_id: orderRes.id,
                handler: async function (response: any) {
                    try {
                        const verifyRes = await fetchWithAuth("/payments/verify-payment", token, {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({
                                razorpay_order_id: response.razorpay_order_id,
                                razorpay_payment_id: response.razorpay_payment_id,
                                razorpay_signature: response.razorpay_signature,
                                gems: pkg.gems
                            }),
                        });

                        // Check if new balance is returned or status is success
                        if (verifyRes.status === "success" || verifyRes.new_balance) {
                            alert(`Payment Successful! Added ${pkg.gems} Gems.`);
                            router.refresh();
                            // Optionally force re-fetch navbar balance here if context exposed it
                        } else {
                            alert("Payment verification failed, please contact support.");
                        }

                    } catch (verifyError) {
                        console.error(verifyError);
                        alert("Payment verification failed");
                    }
                },
                prefill: {
                    name: "User Name", // Ideally fill from UseUser hook
                    email: "user@example.com",
                    contact: "9999999999"
                },
                notes: {
                    address: "Razorpay Corporate Office"
                },
                theme: {
                    color: "#eab308" // Yellow-500
                }
            };

            const paymentObject = new window.Razorpay(options);
            paymentObject.open();

        } catch (error) {
            console.error("Payment setup error", error);
            alert("Failed to initiate payment");
        } finally {
            setLoadingPackage(null);
        }
    };

    return (
        <div className="container mx-auto px-4 py-16 flex flex-col gap-12">
            {/* Same UI as before, only constants changed */}
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
                                <span className="text-4xl font-black">{pkg.priceStr}</span>
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

                        <button
                            disabled={!!loadingPackage}
                            onClick={() => handleBuy(pkg)}
                            className={`w-full py-4 rounded-2xl font-bold transition-all flex items-center justify-center gap-2 ${pkg.popular
                                ? "bg-yellow-500 text-black hover:bg-yellow-400"
                                : "bg-white text-black hover:bg-zinc-200"
                                } disabled:opacity-50 disabled:cursor-not-allowed`}>
                            {loadingPackage === pkg.name ? (
                                <><LucideLoader2 className="animate-spin" /> Processing...</>
                            ) : (
                                "Buy Now"
                            )}
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
