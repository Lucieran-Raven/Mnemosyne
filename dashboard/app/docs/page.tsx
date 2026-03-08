"use client";

import Link from "next/link";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { 
  Brain,
  Search,
  ChevronRight,
  ChevronDown,
  Copy,
  Check,
  Terminal,
  Zap,
  Shield,
  Globe,
  Code2,
  Database,
  MessageSquare,
  ExternalLink,
  Lightbulb,
  AlertTriangle,
  Info,
  Play,
  FileText,
  Package,
  Settings,
  Users,
  Webhook
} from "lucide-react";

// Code Block Component with copy functionality
function CodeBlock({ 
  code, 
  language = "python",
  filename,
  showLineNumbers = true
}: { 
  code: string; 
  language?: string;
  filename?: string;
  showLineNumbers?: boolean;
}) {
  const [copied, setCopied] = useState(false);
  
  const copy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const lines = code.split('\n');
  
  return (
    <div className="relative group my-6 rounded-xl overflow-hidden bg-[#0d1117] border border-gray-800">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-[#161b22] border-b border-gray-800">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-[#ff5f56]" />
            <div className="w-3 h-3 rounded-full bg-[#ffbd2e]" />
            <div className="w-3 h-3 rounded-full bg-[#27ca40]" />
          </div>
          {filename && (
            <span className="ml-3 text-sm text-gray-400 font-mono">{filename}</span>
          )}
        </div>
        <button
          onClick={copy}
          className="flex items-center gap-1.5 px-2 py-1 text-xs text-gray-400 hover:text-white transition-colors"
        >
          {copied ? (
            <>
              <Check className="h-3.5 w-3.5 text-green-500" />
              <span className="text-green-500">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="h-3.5 w-3.5" />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>
      
      {/* Code */}
      <div className="overflow-x-auto">
        <pre className="p-4 text-sm font-mono leading-relaxed">
          <code>
            {lines.map((line, i) => (
              <div key={i} className="table-row">
                {showLineNumbers && (
                  <span className="table-cell text-right pr-4 text-gray-600 select-none w-12">
                    {i + 1}
                  </span>
                )}
                <span 
                  className="table-cell"
                  dangerouslySetInnerHTML={{ 
                    __html: syntaxHighlight(line) 
                  }}
                />
              </div>
            ))}
          </code>
        </pre>
      </div>
    </div>
  );
}

// Simple syntax highlighting
function syntaxHighlight(code: string): string {
  return code
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/(".*?")/g, '<span class="text-[#a5d6ff]">$1</span>')
    .replace(/(\b\d+\b)/g, '<span class="text-[#79c0ff]">$1</span>')
    .replace(/\b(def|class|import|from|return|if|else|elif|for|while|try|except|async|await|with|as|pass|None|True|False)\b/g, 
      '<span class="text-[#ff7b72]">$1</span>')
    .replace(/\b(print|len|range|str|int|dict|list|tuple)\b/g, 
      '<span class="text-[#d2a8ff]">$1</span>')
    .replace(/(\b[A-Z][a-zA-Z0-9_]*\b)/g, '<span class="text-[#ffa657]">$1</span>')
    .replace(/(#.*$)/gm, '<span class="text-[#8b949e]">$1</span>')
    .replace(/\b(self|cls)\b/g, '<span class="text-[#ff7b72]">$1</span>');
}

// Callout Component
function Callout({ 
  type = "info", 
  title, 
  children 
}: { 
  type?: "info" | "tip" | "warning"; 
  title?: string;
  children: React.ReactNode;
}) {
  const styles = {
    info: {
      border: "border-blue-500/20",
      bg: "bg-blue-500/5",
      icon: Info,
      iconColor: "text-blue-400",
      titleColor: "text-blue-300"
    },
    tip: {
      border: "border-green-500/20",
      bg: "bg-green-500/5",
      icon: Lightbulb,
      iconColor: "text-green-400",
      titleColor: "text-green-300"
    },
    warning: {
      border: "border-amber-500/20",
      bg: "bg-amber-500/5",
      icon: AlertTriangle,
      iconColor: "text-amber-400",
      titleColor: "text-amber-300"
    }
  };

  const style = styles[type];
  const Icon = style.icon;

  return (
    <div className={`my-6 p-5 rounded-xl border ${style.border} ${style.bg}`}>
      <div className="flex items-start gap-3">
        <Icon className={`h-5 w-5 mt-0.5 ${style.iconColor} shrink-0`} />
        <div className="flex-1">
          {title && (
            <p className={`font-semibold mb-2 ${style.titleColor}`}>{title}</p>
          )}
          <div className="text-gray-300 leading-relaxed">{children}</div>
        </div>
      </div>
    </div>
  );
}

// Section Header
function SectionHeader({ 
  title, 
  description 
}: { 
  title: string; 
  description?: string;
}) {
  return (
    <div className="mb-8 pb-6 border-b border-gray-800">
      <h1 className="text-4xl font-bold text-white mb-3">{title}</h1>
      {description && (
        <p className="text-xl text-gray-400">{description}</p>
      )}
    </div>
  );
}

// API Endpoint Card
function ApiEndpoint({ 
  method, 
  path, 
  description,
  parameters
}: { 
  method: string; 
  path: string; 
  description: string;
  parameters?: Array<{name: string, type: string, required: boolean, description: string}>;
}) {
  const methodColors: Record<string, string> = {
    GET: "bg-green-500/20 text-green-400 border-green-500/30",
    POST: "bg-blue-500/20 text-blue-400 border-blue-500/30",
    PUT: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
    PATCH: "bg-purple-500/20 text-purple-400 border-purple-500/30",
    DELETE: "bg-red-500/20 text-red-400 border-red-500/30"
  };

  return (
    <div className="my-6 p-5 rounded-xl border border-gray-800 bg-[#161b22]">
      <div className="flex items-center gap-3 mb-3">
        <span className={`px-3 py-1 rounded-md text-xs font-semibold border ${methodColors[method]}`}>
          {method}
        </span>
        <code className="text-sm font-mono text-gray-300">{path}</code>
      </div>
      <p className="text-gray-400 text-sm mb-4">{description}</p>
      
      {parameters && parameters.length > 0 && (
        <div className="mt-4">
          <h4 className="text-sm font-semibold text-gray-300 mb-3">Parameters</h4>
          <div className="space-y-2">
            {parameters.map((param) => (
              <div key={param.name} className="flex items-start gap-3 text-sm">
                <code className="text-blue-400 font-mono">{param.name}</code>
                <span className="text-gray-500">{param.type}</span>
                {param.required && (
                  <span className="text-red-400 text-xs">required</span>
                )}
                <span className="text-gray-400">{param.description}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// Main Docs Page
export default function DocsPage() {
  const [activeSection, setActiveSection] = useState("quickstart");
  const [searchQuery, setSearchQuery] = useState("");

  // Navigation structure
  const navItems = [
    {
      id: "getting-started",
      title: "Getting Started",
      icon: Zap,
      defaultOpen: true,
      children: [
        { id: "quickstart", title: "Quick Start" },
        { id: "installation", title: "Installation" },
        { id: "authentication", title: "Authentication" }
      ]
    },
    {
      id: "core-concepts",
      title: "Core Concepts",
      icon: Database,
      children: [
        { id: "storing", title: "Storing Memories" },
        { id: "retrieving", title: "Retrieving Memories" },
        { id: "memory-types", title: "Memory Types" }
      ]
    },
    {
      id: "api-reference",
      title: "API Reference",
      icon: Code2,
      children: [
        { id: "api-overview", title: "Overview" },
        { id: "api-store", title: "Store Memory" },
        { id: "api-retrieve", title: "Retrieve Memories" },
        { id: "api-list", title: "List Memories" }
      ]
    },
    {
      id: "features",
      title: "Features",
      icon: Globe,
      children: [
        { id: "languages", title: "Multi-Language" },
        { id: "webhooks", title: "Webhooks" }
      ]
    },
    {
      id: "resources",
      title: "Resources",
      icon: FileText,
      children: [
        { id: "sdks", title: "SDKs" },
        { id: "changelog", title: "Changelog" }
      ]
    }
  ];

  const renderContent = () => {
    switch (activeSection) {
      case "quickstart":
        return (
          <div>
            <SectionHeader 
              title="Quick Start"
              description="Get Mnemosyne running in 5 minutes. Add persistent memory to your AI agent with one line of code."
            />

            <div className="prose prose-invert max-w-none">
              <h2 className="text-2xl font-semibold text-white mt-8 mb-4">1. Install the SDK</h2>
              <p className="text-gray-400 mb-4">
                Mnemosyne is available as a Python package. Install it using pip:
              </p>
              <CodeBlock 
                code="pip install mnemosyne" 
                filename="Terminal"
              />

              <h2 className="text-2xl font-semibold text-white mt-8 mb-4">2. Get your API key</h2>
              <p className="text-gray-400 mb-4">
                Sign up for a free account at{" "}
                <Link href="/login" className="text-blue-400 hover:underline">
                  mnemosyne.dev
                </Link>{" "}
                and get your API key. No credit card required to start.
              </p>

              <Callout type="tip" title="Free tier includes">
                <ul className="list-disc list-inside space-y-1">
                  <li>100,000 operations per month</li>
                  <li>1,000 memories stored</li>
                  <li>All SDK features</li>
                  <li>Community support</li>
                </ul>
              </Callout>

              <h2 className="text-2xl font-semibold text-white mt-8 mb-4">3. Start using memory</h2>
              <p className="text-gray-400 mb-4">
                Initialize the client and start storing memories:
              </p>
              <CodeBlock 
                code={`from mnemosyne import MnemosyneClient

# Initialize client
client = MnemosyneClient(api_key="your-api-key")

# Store a memory
client.store("I'm gluten-free and love Italian food")

# Retrieve memories
memories = client.retrieve("What are my food preferences?")
for memory in memories:
    print(memory.content)`}
                filename="example.py"
              />

              <Callout type="info">
                🎉 <strong>That&apos;s it!</strong> Your AI agent now has persistent memory. 
                Every interaction is automatically stored and can be retrieved contextually.
              </Callout>

              <h2 className="text-2xl font-semibold text-white mt-8 mb-4">Next steps</h2>
              <ul className="space-y-3">
                <li>
                  <Link href="#installation" className="text-blue-400 hover:underline">
                    Learn more about installation options →
                  </Link>
                </li>
                <li>
                  <Link href="#authentication" className="text-blue-400 hover:underline">
                    Set up authentication →
                  </Link>
                </li>
                <li>
                  <Link href="#storing" className="text-blue-400 hover:underline">
                    Explore memory storage →
                  </Link>
                </li>
              </ul>
            </div>
          </div>
        );

      case "installation":
        return (
          <div>
            <SectionHeader 
              title="Installation"
              description="Set up Mnemosyne in your development environment."
            />

            <div className="prose prose-invert max-w-none">
              <h2 className="text-2xl font-semibold text-white mt-8 mb-4">Requirements</h2>
              <ul className="list-disc list-inside text-gray-400 space-y-2">
                <li>Python 3.8 or higher</li>
                <li>pip or poetry package manager</li>
              </ul>

              <h2 className="text-2xl font-semibold text-white mt-8 mb-4">Install with pip</h2>
              <CodeBlock 
                code="pip install mnemosyne" 
                filename="Terminal"
              />

              <h2 className="text-2xl font-semibold text-white mt-8 mb-4">Install with Poetry</h2>
              <CodeBlock 
                code="poetry add mnemosyne" 
                filename="Terminal"
              />

              <h2 className="text-2xl font-semibold text-white mt-8 mb-4">Verify installation</h2>
              <CodeBlock 
                code={`import mnemosyne
print(mnemosyne.__version__)
# Output: 0.1.0`}
                filename="verify.py"
              />

              <h2 className="text-2xl font-semibold text-white mt-8 mb-4">Development installation</h2>
              <p className="text-gray-400 mb-4">
                To install from source for development:
              </p>
              <CodeBlock 
                code={`git clone https://github.com/Lucieran-Raven/Mnemosyne.git
cd Mnemosyne/sdk
pip install -e .`}
                filename="Terminal"
              />
            </div>
          </div>
        );

      case "authentication":
        return (
          <div>
            <SectionHeader 
              title="Authentication"
              description="Secure your API requests with API key authentication."
            />

            <div className="prose prose-invert max-w-none">
              <h2 className="text-2xl font-semibold text-white mt-8 mb-4">API Key</h2>
              <p className="text-gray-400 mb-4">
                All API requests must include your API key in the header. You can find your API key in the{" "}
                <Link href="/dashboard" className="text-blue-400 hover:underline">
                  Dashboard
                </Link>.
              </p>

              <CodeBlock 
                code={`from mnemosyne import MnemosyneClient

# Option 1: Pass API key directly
client = MnemosyneClient(api_key="mnem_live_1234567890")

# Option 2: Use environment variable (recommended)
import os
client = MnemosyneClient()  # Automatically reads MNEMOSYNE_API_KEY`}
                filename="auth.py"
              />

              <Callout type="warning" title="Security best practices">
                <ul className="list-disc list-inside space-y-1">
                  <li>Never commit API keys to version control</li>
                  <li>Use environment variables for production</li>
                  <li>Rotate keys regularly</li>
                  <li>Use different keys for development and production</li>
                </ul>
              </Callout>

              <h2 className="text-2xl font-semibold text-white mt-8 mb-4">Environment variables</h2>
              <CodeBlock 
                code={`# .env file
MNEMOSYNE_API_KEY=mnem_live_1234567890
MNEMOSYNE_BASE_URL=https://api.mnemosyne.dev`}
                filename=".env"
              />
            </div>
          </div>
        );

      case "storing":
        return (
          <div>
            <SectionHeader 
              title="Storing Memories"
              description="Learn how to store and manage memories for your AI agents."
            />

            <div className="prose prose-invert max-w-none">
              <h2 className="text-2xl font-semibold text-white mt-8 mb-4">Basic storage</h2>
              <p className="text-gray-400 mb-4">
                Store memories with automatic type detection:
              </p>
              <CodeBlock 
                code={`from mnemosyne import MnemosyneClient, MemoryType

client = MnemosyneClient()

# Store with automatic type detection
result = client.store("I'm gluten-free and love Italian food")

# Store with specific type
result = client.store(
    content="I prefer email over phone calls",
    memory_type=MemoryType.PREFERENCE
)

print(result.status)  # "accepted" or "completed"
print(result.memory_ids)  # IDs of stored memories`}
                filename="store.py"
              />

              <h2 className="text-2xl font-semibold text-white mt-8 mb-4">Store conversation turns</h2>
              <p className="text-gray-400 mb-4">
                Store entire conversations and let Mnemosyne extract relevant memories:
              </p>
              <CodeBlock 
                code={`turns = [
    {"role": "user", "content": "I need a restaurant recommendation"},
    {"role": "assistant", "content": "What cuisine do you prefer?"},
    {"role": "user", "content": "Italian, but I need gluten-free options"},
]

result = client.store_turns(turns)
print(f"Extracted {len(result.memory_ids)} memories")`}
                filename="conversation.py"
              />

              <h2 className="text-2xl font-semibold text-white mt-8 mb-4">Async processing</h2>
              <p className="text-gray-400 mb-4">
                For high-throughput applications, use async storage:
              </p>
              <CodeBlock 
                code={`import asyncio
from mnemosyne import AsyncMnemosyneClient

async def store_memories():
    client = AsyncMnemosyneClient()
    
    # Store multiple memories concurrently
    tasks = [
        client.store(f"Memory {i}")
        for i in range(100)
    ]
    results = await asyncio.gather(*tasks)
    
    return results

asyncio.run(store_memories())`}
                filename="async_store.py"
              />
            </div>
          </div>
        );

      case "retrieving":
        return (
          <div>
            <SectionHeader 
              title="Retrieving Memories"
              description="Access stored memories using semantic search."
            />

            <div className="prose prose-invert max-w-none">
              <h2 className="text-2xl font-semibold text-white mt-8 mb-4">Semantic search</h2>
              <p className="text-gray-400 mb-4">
                Retrieve memories using natural language queries:
              </p>
              <CodeBlock 
                code={`# Basic retrieval
memories = client.retrieve("What food does the user like?")

# With options
memories = client.retrieve(
    query="What are my dietary restrictions?",
    top_k=10,  # Return up to 10 results
    memory_type=MemoryType.PREFERENCE,  # Filter by type
    min_confidence=0.7  # Minimum relevance score
)

for memory in memories:
    print(f"{memory.content} (confidence: {memory.confidence:.2f})")`}
                filename="retrieve.py"
              />

              <h2 className="text-2xl font-semibold text-white mt-8 mb-4">List all memories</h2>
              <CodeBlock 
                code={`# List all memories
all_memories = client.list_memories(limit=50)

# Filter by type
preferences = client.list_memories(
    memory_type=MemoryType.PREFERENCE,
    limit=20
)

# Get specific memory
memory = client.get_memory("mem_1234567890")
print(memory.content)`}
                filename="list.py"
              />
            </div>
          </div>
        );

      case "api-overview":
        return (
          <div>
            <SectionHeader 
              title="API Reference"
              description="Complete reference for the Mnemosyne REST API."
            />

            <div className="prose prose-invert max-w-none">
              <h2 className="text-2xl font-semibold text-white mt-8 mb-4">Base URL</h2>
              <CodeBlock 
                code="https://api.mnemosyne.dev/v1" 
                filename="Base URL"
              />

              <h2 className="text-2xl font-semibold text-white mt-8 mb-4">Authentication</h2>
              <p className="text-gray-400 mb-4">
                All requests must include your API key in the header:
              </p>
              <CodeBlock 
                code={`X-API-Key: mnem_live_1234567890`}
                filename="Headers"
              />

              <h2 className="text-2xl font-semibold text-white mt-8 mb-4">Response format</h2>
              <p className="text-gray-400 mb-4">
                All responses are returned in JSON format:
              </p>
              <CodeBlock 
                code={`{
  "success": true,
  "data": { ... },
  "error": null
}`}
                filename="Response"
              />

              <Callout type="tip">
                View interactive API documentation at{" "}
                <Link href="https://api.mnemosyne.dev/docs" className="text-blue-400 hover:underline">
                  api.mnemosyne.dev/docs
                </Link>
              </Callout>
            </div>
          </div>
        );

      case "api-store":
        return (
          <div>
            <SectionHeader 
              title="Store Memory"
              description="Store a new memory for an entity."
            />

            <ApiEndpoint 
              method="POST"
              path="/v1/memories/store"
              description="Store a new memory. The memory will be processed and embedded automatically."
              parameters={[
                { name: "content", type: "string", required: true, description: "The memory content to store" },
                { name: "entity_id", type: "string", required: false, description: "Unique identifier for the entity (default: 'default')" },
                { name: "memory_type", type: "string", required: false, description: "Type of memory (preference, fact, experience, etc.)" },
                { name: "async", type: "boolean", required: false, description: "Process asynchronously (default: false)" }
              ]}
            />

            <CodeBlock 
              code={`curl -X POST https://api.mnemosyne.dev/v1/memories/store \\
  -H "X-API-Key: mnem_live_1234567890" \\
  -H "Content-Type: application/json" \\
  -d '{
    "content": "I'm gluten-free and love Italian food",
    "entity_id": "user_123",
    "memory_type": "preference"
  }'`}
              filename="cURL"
            />
          </div>
        );

      case "api-retrieve":
        return (
          <div>
            <SectionHeader 
              title="Retrieve Memories"
              description="Search and retrieve memories using semantic search."
            />

            <ApiEndpoint 
              method="POST"
              path="/v1/memories/retrieve"
              description="Retrieve relevant memories for a given query using semantic search."
              parameters={[
                { name: "query", type: "string", required: true, description: "Search query" },
                { name: "entity_id", type: "string", required: false, description: "Filter by entity" },
                { name: "top_k", type: "integer", required: false, description: "Number of results (default: 5, max: 50)" },
                { name: "memory_type", type: "string", required: false, description: "Filter by memory type" }
              ]}
            />

            <CodeBlock 
              code={`curl -X POST https://api.mnemosyne.dev/v1/memories/retrieve \\
  -H "X-API-Key: mnem_live_1234567890" \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "What food does the user like?",
    "entity_id": "user_123",
    "top_k": 10
  }'`}
              filename="cURL"
            />

            <h3 className="text-xl font-semibold text-white mt-8 mb-4">Response</h3>
            <CodeBlock 
              code={`{
  "success": true,
  "data": {
    "memories": [
      {
        "id": "mem_1234567890",
        "content": "User is gluten-free and loves Italian food",
        "memory_type": "preference",
        "confidence": 0.95,
        "created_at": "2025-01-15T10:30:00Z"
      }
    ],
    "total": 1
  }
}`}
              filename="Response"
            />
          </div>
        );

      case "languages":
        return (
          <div>
            <SectionHeader 
              title="Multi-Language Support"
              description="Native support for 10+ languages including Southeast Asian languages."
            />

            <div className="prose prose-invert max-w-none">
              <p className="text-xl text-gray-400 mb-8">
                Mnemosyne understands and processes memories in multiple languages, 
                including code-switching (mixing languages in one conversation).
              </p>

              <h2 className="text-2xl font-semibold text-white mt-8 mb-4">Supported languages</h2>
              <div className="grid grid-cols-2 gap-4 mb-8">
                {[
                  "English", "Bahasa Malaysia", "Bahasa Indonesia",
                  "Thai (ภาษาไทย)", "Mandarin Chinese (中文)", "Tamil (தமிழ்)",
                  "Tagalog/Filipino", "Vietnamese (Tiếng Việt)", "Hindi (हिन्दी)",
                  "Arabic (العربية)"
                ].map((lang) => (
                  <div key={lang} className="flex items-center gap-3 p-3 rounded-lg bg-[#161b22] border border-gray-800">
                    <Globe className="h-4 w-4 text-primary" />
                    <span className="text-gray-300">{lang}</span>
                  </div>
                ))}
              </div>

              <h2 className="text-2xl font-semibold text-white mt-8 mb-4">Code-switching examples</h2>
              <p className="text-gray-400 mb-4">
                Mnemosyne understands when users mix languages (&quot;rojak&quot; English):
              </p>

              <div className="space-y-4">
                <div className="p-4 rounded-lg bg-[#161b22] border border-gray-800">
                  <p className="text-sm text-gray-500 mb-2">Input:</p>
                  <p className="text-gray-300">&quot;I&apos;m gluten-free, tapi saya suka Italian food&quot;</p>
                  <p className="text-sm text-green-400 mt-2 font-mono">→ Extracts: dietary_restriction: gluten-free, cuisine_preference: Italian</p>
                </div>

                <div className="p-4 rounded-lg bg-[#161b22] border border-gray-800">
                  <p className="text-sm text-gray-500 mb-2">Input:</p>
                  <p className="text-gray-300">&quot;Saya allergic to peanuts, but I love Thai cuisine&quot;</p>
                  <p className="text-sm text-green-400 mt-2 font-mono">→ Extracts: allergy: peanuts, cuisine_preference: Thai</p>
                </div>
              </div>

              <Callout type="tip" title="Regional focus">
                Mnemosyne is built with Southeast Asian languages as first-class citizens. 
                Unlike other solutions that primarily focus on English, we understand Malay, 
                Indonesian, Thai, and code-switching natively.
              </Callout>
            </div>
          </div>
        );

      default:
        return (
          <div>
            <SectionHeader 
              title="Documentation"
              description="Select a section from the sidebar to get started."
            />
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-[#0d1117] text-gray-300">
      {/* Top Navigation */}
      <header className="sticky top-0 z-50 bg-[#0d1117]/95 backdrop-blur border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-8">
              <Link href="/" className="flex items-center gap-2 text-white">
                <Brain className="h-7 w-7 text-primary" />
                <span className="font-bold text-lg">Mnemosyne</span>
              </Link>
              
              <div className="hidden md:flex items-center gap-1 text-sm">
                <span className="text-gray-500">Docs</span>
                <ChevronRight className="h-4 w-4 text-gray-600" />
                <span className="text-gray-300">
                  {navItems.find(item => 
                    item.children?.some(child => child.id === activeSection)
                  )?.title || "Getting Started"}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="relative hidden md:block">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
                <Input
                  type="search"
                  placeholder="Search docs..."
                  className="w-64 pl-10 bg-[#161b22] border-gray-700 text-gray-300 placeholder:text-gray-500"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>

              <Link href="https://github.com/Lucieran-Raven/Mnemosyne" target="_blank">
                <Button variant="ghost" size="sm" className="text-gray-400 hover:text-white">
                  <ExternalLink className="h-4 w-4" />
                </Button>
              </Link>

              <Link href="/login">
                <Button size="sm" className="bg-primary hover:bg-primary/90 text-white">
                  Sign In
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex gap-8 py-8">
          {/* Sidebar */}
          <aside className="w-64 hidden lg:block shrink-0">
            <nav className="space-y-6 sticky top-24">
              {navItems.map((section) => (
                <div key={section.id}>
                  <h3 className="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                    {section.title}
                  </h3>
                  <div className="space-y-0.5">
                    {section.children?.map((item) => (
                      <button
                        key={item.id}
                        onClick={() => setActiveSection(item.id)}
                        className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left text-sm transition-all duration-200 ${
                          activeSection === item.id 
                            ? "bg-primary/10 text-primary font-medium" 
                            : "text-gray-400 hover:text-white hover:bg-white/5"
                        }`}
                      >
                        {item.title}
                      </button>
                    ))}
                  </div>
                </div>
              ))}

              <div className="pt-6 border-t border-gray-800">
                <h3 className="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
                  Need help?
                </h3>
                <div className="space-y-1">
                  <Link 
                    href="#" 
                    className="flex items-center gap-2 px-3 py-2 text-sm text-gray-400 hover:text-white transition-colors"
                  >
                    <MessageSquare className="h-4 w-4" />
                    Community Discord
                  </Link>
                  <Link 
                    href="mailto:support@mnemosyne.dev" 
                    className="flex items-center gap-2 px-3 py-2 text-sm text-gray-400 hover:text-white transition-colors"
                  >
                    <ExternalLink className="h-4 w-4" />
                    Email Support
                  </Link>
                </div>
              </div>
            </nav>
          </aside>

          {/* Main Content */}
          <main className="flex-1 min-w-0 max-w-3xl">
            <AnimatePresence mode="wait">
              <motion.div
                key={activeSection}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
              >
                {renderContent()}
              </motion.div>
            </AnimatePresence>

            {/* Footer */}
            <div className="mt-16 pt-8 border-t border-gray-800">
              <div className="flex items-center justify-between">
                <p className="text-sm text-gray-500">
                  Last updated: January 2025
                </p>
                <div className="flex items-center gap-4">
                  <Link 
                    href="#" 
                    className="text-sm text-gray-400 hover:text-white transition-colors"
                  >
                    Edit this page →
                  </Link>
                </div>
              </div>
            </div>
          </main>

          {/* Right Sidebar - Table of Contents */}
          <aside className="w-48 hidden xl:block shrink-0">
            <div className="sticky top-24">
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
                On this page
              </h3>
              <nav className="space-y-2 text-sm">
                <a href="#" className="block text-gray-400 hover:text-white transition-colors">
                  Overview
                </a>
                <a href="#" className="block text-gray-500 hover:text-white transition-colors pl-3">
                  Installation
                </a>
                <a href="#" className="block text-gray-500 hover:text-white transition-colors pl-3">
                  Quick Start
                </a>
              </nav>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}
