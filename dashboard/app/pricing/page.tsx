"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { 
  Brain, 
  Check, 
  X,
  Zap,
  ArrowRight,
  HelpCircle
} from "lucide-react";

const plans = [
  {
    name: "Free",
    price: "$0",
    period: "forever",
    description: "Perfect for hobby projects and testing",
    features: [
      "100K operations/month",
      "1,000 memories stored",
      "Basic semantic search",
      "Community support",
      "API access",
    ],
    cta: "Get Started Free",
    popular: false,
  },
  {
    name: "Bootstrapper",
    price: "$19",
    period: "/month",
    description: "For indie hackers and early startups",
    features: [
      "1M operations/month",
      "50,000 memories stored",
      "Advanced semantic search",
      "Multi-language support",
      "Priority email support",
      "Webhook integrations",
      "Analytics dashboard",
    ],
    cta: "Start Building",
    popular: true,
  },
  {
    name: "Startup",
    price: "$99",
    period: "/month",
    description: "For growing teams with scale needs",
    features: [
      "10M operations/month",
      "500,000 memories stored",
      "Custom embeddings",
      "Team collaboration",
      "Priority support",
      "SLA guarantee",
      "Dedicated infrastructure",
      "Custom integrations",
    ],
    cta: "Scale Up",
    popular: false,
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "",
    description: "For organizations with specific needs",
    features: [
      "Unlimited operations",
      "Unlimited memories",
      "Self-hosted option",
      "SSO & SAML",
      "Audit logs",
      "99.99% SLA",
      "Dedicated support",
      "Custom contracts",
    ],
    cta: "Contact Sales",
    popular: false,
  },
];

const comparisons = [
  { feature: "Price per memory", mnemosyne: "$0.0001", mem0: "$0.001", build: "$0.001+" },
  { feature: "Minimum monthly", mnemosyne: "$0", mem0: "$249", build: "3 months dev" },
  { feature: "Setup time", mnemosyne: "5 minutes", mem0: "1 hour", build: "3 months" },
  { feature: "Multi-language", mnemosyne: "✓ Native", mem0: "✓ Limited", build: "DIY" },
  { feature: "Maintenance", mnemosyne: "Zero", mem0: "Low", build: "High" },
  { feature: "Vector search", mnemosyne: "✓ Included", mem0: "✓ Included", build: "Build it" },
];

export default function PricingPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="border-b sticky top-0 bg-background/95 backdrop-blur z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <Link href="/" className="flex items-center gap-2">
              <Brain className="h-8 w-8 text-primary" />
              <span className="text-xl font-bold">Mnemosyne</span>
            </Link>
            <div className="hidden md:flex items-center gap-8">
              <Link href="/docs" className="text-muted-foreground hover:text-foreground transition-colors">
                Docs
              </Link>
              <Link href="/pricing" className="text-foreground font-medium">
                Pricing
              </Link>
              <Link href="/login">
                <Button variant="ghost">Sign In</Button>
              </Link>
              <Link href="/login">
                <Button>Get Started</Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="py-20 text-center">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            Simple, transparent pricing
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Start free, scale as you grow. No hidden fees, no enterprise tax. 
            <span className="text-primary font-semibold">90% cheaper</span> than building it yourself.
          </p>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="pb-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {plans.map((plan) => (
              <Card 
                key={plan.name}
                className={`p-6 flex flex-col ${
                  plan.popular 
                    ? "border-2 border-primary relative" 
                    : ""
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <span className="bg-primary text-primary-foreground text-xs font-semibold px-3 py-1 rounded-full">
                      Most Popular
                    </span>
                  </div>
                )}
                
                <div className="mb-4">
                  <h3 className="text-lg font-semibold">{plan.name}</h3>
                  <p className="text-sm text-muted-foreground">{plan.description}</p>
                </div>
                
                <div className="mb-6">
                  <span className="text-4xl font-bold">{plan.price}</span>
                  <span className="text-muted-foreground">{plan.period}</span>
                </div>
                
                <ul className="space-y-3 mb-6 flex-1">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-2 text-sm">
                      <Check className="h-4 w-4 text-green-500 mt-0.5 shrink-0" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
                
                <Link href="/login">
                  <Button 
                    className="w-full" 
                    variant={plan.popular ? "default" : "outline"}
                  >
                    {plan.cta}
                  </Button>
                </Link>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Comparison Table */}
      <section className="py-20 bg-muted/50">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-12">
            Why Mnemosyne beats the alternatives
          </h2>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-4 font-semibold">Feature</th>
                  <th className="text-center py-4 font-semibold text-primary">Mnemosyne</th>
                  <th className="text-center py-4 font-semibold text-muted-foreground">Mem0</th>
                  <th className="text-center py-4 font-semibold text-muted-foreground">Build Yourself</th>
                </tr>
              </thead>
              <tbody>
                {comparisons.map((row, i) => (
                  <tr key={i} className="border-b last:border-0">
                    <td className="py-4 font-medium">{row.feature}</td>
                    <td className="text-center py-4 text-primary font-semibold">{row.mnemosyne}</td>
                    <td className="text-center py-4 text-muted-foreground">{row.mem0}</td>
                    <td className="text-center py-4 text-muted-foreground">{row.build}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="py-20">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-12">Frequently Asked Questions</h2>
          
          <div className="space-y-6">
            <div className="p-6 border rounded-lg">
              <h3 className="font-semibold mb-2">What's an operation?</h3>
              <p className="text-muted-foreground">
                An operation is any API call - store, retrieve, list, or delete. 
                100K operations = ~3,300 operations per day on the Free plan.
              </p>
            </div>
            
            <div className="p-6 border rounded-lg">
              <h3 className="font-semibold mb-2">Can I upgrade or downgrade anytime?</h3>
              <p className="text-muted-foreground">
                Yes! You can change plans at any time. Upgrades are prorated, 
                downgrades take effect at the end of your billing cycle.
              </p>
            </div>
            
            <div className="p-6 border rounded-lg">
              <h3 className="font-semibold mb-2">What happens if I exceed my limits?</h3>
              <p className="text-muted-foreground">
                We'll notify you when you hit 80% of your limit. You can upgrade 
                instantly or operations will be rate-limited until the next month.
              </p>
            </div>
            
            <div className="p-6 border rounded-lg">
              <h3 className="font-semibold mb-2">Do you offer refunds?</h3>
              <p className="text-muted-foreground">
                Yes, we offer 30-day refunds if you're not satisfied. 
                No questions asked.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-primary text-primary-foreground">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Still have questions?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Our team is here to help. Reach out and we'll get back to you within 24 hours.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/login">
              <Button size="lg" variant="secondary" className="gap-2">
                Get Started Free <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Button size="lg" variant="outline" className="border-primary-foreground hover:bg-primary-foreground hover:text-primary">
              Contact Sales
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Brain className="h-6 w-6 text-primary" />
              <span className="font-semibold">Mnemosyne</span>
            </div>
            <p className="text-sm text-muted-foreground">
              © 2025 Mnemosyne. Built for Southeast Asia, available worldwide.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
