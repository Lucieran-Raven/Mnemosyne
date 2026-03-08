# Mnemosyne - AI Memory Layer

**The definitive memory infrastructure for AI agents.**

Mnemosyne gives every AI agent persistent, semantic memory—so they can truly know their users. Built for developers who need fast, affordable memory without enterprise overhead.

## Quick Start

```bash
# 1. Clone and setup
./scripts/setup-local.sh

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Start services
docker-compose up -d

# 4. Install SDK
pip install mnemosyne-memory
```

## One-Line Integration

```python
from mnemosyne import MnemosyneClient

client = MnemosyneClient(api_key="your-key")

# Store memory
client.store("I'm gluten-free and love Italian food")

# Retrieve later
memories = client.retrieve("What are user's dietary restrictions?")
```

## Project Structure

```
mnemosyne/
├── api/              # FastAPI backend service
│   ├── app/
│   │   ├── api/routes/    # REST endpoints
│   │   ├── models/        # SQLAlchemy models
│   │   ├── services/      # Business logic
│   │   └── core/          # Config & utilities
│   ├── Dockerfile
│   └── requirements.txt
├── sdk/              # Python SDK (pip install)
│   ├── src/mnemosyne/
│   ├── integrations/      # LangChain, etc.
│   └── pyproject.toml
├── dashboard/        # Next.js admin interface
│   ├── app/
│   ├── components/
│   └── Dockerfile
├── cli/              # Mnemosyne CLI tool
│   └── mnemosyne_cli/
├── infra/            # Terraform configs
├── scripts/          # Automation scripts
└── docker-compose.yml
```

## Development

```bash
# Setup
./scripts/setup-local.sh

# Start all services
docker-compose up -d

# Run CLI commands
mnemosyne status          # Check services
mnemosyne dev start       # Start dev mode
mnemosyne test            # Run tests
mnemosyne deploy api      # Deploy to Cloud Run

# API: http://localhost:8000/docs
# Dashboard: http://localhost:3000
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/v1/memories/store` | POST | Store new memory |
| `/v1/memories/retrieve` | POST | Retrieve memories |
| `/v1/memories/list` | GET | List all memories |
| `/v1/memories/{id}` | GET | Get specific memory |
| `/v1/memories/{id}` | DELETE | Delete memory |

## Key Features

- **Automatic Distillation**: Raw text → structured memories (entities, preferences, facts)
- **Semantic Retrieval**: Vector search with temporal weighting
- **Conflict Resolution**: Detects and handles contradictory memories
- **Multi-language**: Optimized for English, Malay, Indonesian
- **Async Processing**: Background jobs via Cloud Tasks
- **Cost Optimized**: 10x cheaper than alternatives (~$0.00004/op)

## Pricing Target

| Component | Cost |
|-----------|------|
| Distillation (Gemini Flash) | $0.000015 |
| Embedding | $0.000025 |
| Infrastructure | $0.000005 |
| **Total per operation** | **~$0.00004** |

## CLI Automation

The Mnemosyne CLI manages the entire stack:

```bash
mnemosyne deploy api              # Deploy API to Cloud Run
mnemosyne deploy dashboard        # Deploy to Vercel
mnemosyne status all              # Check all services
mnemosyne logs service=api        # Stream logs
mnemosyne db migrate              # Run migrations
mnemosyne db backup               # Backup database
mnemosyne config validate         # Validate configs
mnemosyne config env              # Show required env vars
```

## Architecture

| Component | Technology |
|-----------|------------|
| **API** | FastAPI + Cloud Run |
| **Vectors** | Pinecone (prod) / Chroma (local) |
| **Metadata** | PostgreSQL 16 |
| **Cache** | Redis |
| **Queue** | Google Cloud Tasks |
| **LLM** | Gemini 2.5 Flash |
| **Embeddings** | text-embedding-004 |
| **Auth** | Clerk |

## Environment Variables

See `.env.example` for full configuration. Required:

- `GEMINI_API_KEY` - Google AI Studio
- `PINECONE_API_KEY` - Vector database
- `CLERK_SECRET_KEY` - Authentication
- `DATABASE_URL` - PostgreSQL
- `REDIS_URL` - Cache

## Roadmap

- [x] Core API with store/retrieve
- [x] Python SDK with LangChain integration
- [x] Next.js dashboard
- [x] Docker & local development
- [x] CI/CD pipelines
- [ ] Terraform infrastructure
- [ ] Background worker processing
- [ ] Advanced conflict resolution
- [ ] Memory analytics
- [ ] Open-source distillation core

## License

MIT License - see LICENSE file

---

**Built by developers, for developers.**
*10x cheaper. Bootstrapper-friendly. Southeast Asia first.*
