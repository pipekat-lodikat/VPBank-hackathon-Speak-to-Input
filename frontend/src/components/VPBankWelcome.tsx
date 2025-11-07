import { Button } from "./ui/button";
import { ArrowRight, Sparkles, FileCheck, UserCog, Briefcase, FileBarChart, CheckCircle } from "lucide-react";

// Simplified GenAI badge - cleaner design
function GenAIBadge() {
    return (
        <span className="ml-2 inline-flex items-center gap-1.5 align-middle select-none">
            <span className="text-xs font-semibold tracking-wide" style={{ color: "#00b74f" }}>
                VPBank
            </span>
            <span className="relative h-3 w-px bg-gray-300" />
            <span className="relative inline-flex items-center">
                <span className="text-lg font-black tracking-tight bg-gradient-to-r from-[#1d4289] via-[#00b74f] to-[#009440] bg-clip-text text-transparent">
                    GenAI
                </span>
                <Sparkles className="ml-1 h-3.5 w-3.5" style={{ color: "#00b74f" }} />
            </span>
        </span>
    );
}

// 5 use cases - clean and organized
const FEATURES = [
    {
        key: "loan-kyc",
        Icon: FileCheck,
        title: "Loan KYC",
        description: "Customer verification & loan info",
    },
    {
        key: "crm-update",
        Icon: UserCog,
        title: "CRM Update",
        description: "Customer profile & contact info",
    },
    {
        key: "hr-workflow",
        Icon: Briefcase,
        title: "HR Workflow",
        description: "Leave requests & approvals",
    },
    {
        key: "compliance",
        Icon: FileBarChart,
        title: "Compliance",
        description: "Audit reports & risk assessment",
    },
    {
        key: "operations",
        Icon: CheckCircle,
        title: "Operations",
        description: "Transaction validation & review",
    },
];

interface VPBankWelcomeProps {
    onStartSpeaking?: () => void;
}

export default function VPBankWelcome({ onStartSpeaking }: VPBankWelcomeProps) {
    return (
        <section className="relative mx-auto max-w-6xl px-6 py-16">
            {/* Centered Content */}
            <div className="relative text-center">
                {/* Main Title - Reduced size to prevent line break */}
                <h1
                    className="text-3xl md:text-4xl font-bold tracking-tight mb-3"
                    style={{ color: "#343434" }}
                >
                    AI Voice Assistant for Banking Operations
                    <GenAIBadge />
                </h1>

                {/* Subtitle */}
                <p
                    className="text-sm md:text-base max-w-2xl mx-auto mb-8"
                    style={{ color: "#343434", opacity: 0.75 }}
                >
                    Just speak — your AI assistant handles the rest with banking-grade security.
                </p>

                {/* CTA Button - Official VPBank Gradient */}
                <Button
                    className="group text-sm font-semibold px-8 py-5 rounded-xl shadow-lg hover:shadow-xl transition-all border-0"
                    style={{
                        background: "linear-gradient(270deg, #00b74f -22.41%, #1d4289 108.33%)",
                        color: "#ffffff",
                    }}
                    onClick={onStartSpeaking}
                >
                    <Sparkles className="mr-2 h-4 w-4" />
                    Start Speaking
                    <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                </Button>
            </div>

            {/* Clean 5-card layout - 3 top, 2 bottom centered */}
            <div className="relative mt-16 flex flex-wrap justify-center gap-4 max-w-4xl mx-auto">
                {FEATURES.map(({ key, Icon, title, description }) => (
                    <div
                        key={key}
                        className="relative group w-full sm:w-[calc(50%-0.5rem)] md:w-[calc(33.333%-0.75rem)]"
                    >
                        <div
                            className="h-full p-4 rounded-lg transition-all hover:shadow-md border"
                            style={{
                                backgroundColor: "#ffffff",
                                borderColor: "#e5e7eb",
                            }}
                        >
                            {/* Compact Icon */}
                            <div className="flex justify-center mb-3">
                                <Icon
                                    className="w-8 h-8"
                                    strokeWidth={1.5}
                                    style={{ color: "#016d33" }}
                                />
                            </div>

                            {/* Title */}
                            <h3
                                className="text-sm font-bold mb-1.5 text-center"
                                style={{ color: "#343434" }}
                            >
                                {title}
                            </h3>

                            {/* Description */}
                            <p
                                className="text-xs text-center leading-relaxed"
                                style={{ color: "#343434", opacity: 0.65 }}
                            >
                                {description}
                            </p>
                        </div>
                    </div>
                ))}
            </div>

            {/* Trust footer with VPBank red accent */}
            <p
                className="mt-12 text-center text-xs font-medium"
                style={{ color: "#343434", opacity: 0.6 }}
            >
                <span style={{ color: "#e10600" }}>🔒</span> Enterprise-grade security • Compliant with VPBank data policies
            </p>
        </section>
    );
}