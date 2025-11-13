# Autonomous Finance Back-Office

[![Backend CI](https://github.com/akaash-nigam/ccw-AutonomousFinance/workflows/Backend%20CI/badge.svg)](https://github.com/akaash-nigam/ccw-AutonomousFinance/actions)
[![Frontend CI](https://github.com/akaash-nigam/ccw-AutonomousFinance/workflows/Frontend%20CI/badge.svg)](https://github.com/akaash-nigam/ccw-AutonomousFinance/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**An AI-native financial back-office platform powered by frontier LLM capabilities** featuring autonomous multi-agent systems that orchestrate end-to-end financial operations: Procure-to-Pay (P2P), Order-to-Cash (O2C), Record-to-Report (R2R), and tax compliance.

> **Tagline**: "Close the books while you sleep—with frontier AI autonomy."

---

## 🎯 Vision

Transform financial operations from a labor-intensive, error-prone process into an autonomous, AI-driven system that operates 24/7 with audit-grade accuracy and compliance.

### Key Outcomes
- **70-90% reduction** in month-end close time (from 7 days → 1.5 days)
- **95%+ straight-through processing** for invoices, payments, and reconciliations
- **<0.1% variance rate** before human review (vs. industry 2-5%)
- **Real-time compliance** with audit-ready evidence packs for every transaction
- **Adaptive learning** that improves accuracy with each month's operations

---

## 📚 Documentation

- **[Product Requirements Document (PRD)](./docs/PRD-Autonomous-Finance-Backoffice.md)** - Comprehensive product specification
- **[Product Roadmap](./docs/PRODUCT-ROADMAP.md)** - MVP and epic breakdown with timeline
- **[Development Plan](./docs/DEVELOPMENT-PLAN.md)** - 12-week implementation plan

---

## 🏗️ Architecture

### Tech Stack

**Backend**
- Python 3.11+ with FastAPI
- LangGraph for agent orchestration
- Anthropic Claude Sonnet 4.5 (primary LLM)
- PostgreSQL (transactional data)
- Redis (caching, sessions)
- RabbitMQ (async workflows)

**Frontend**
- React 18+ with TypeScript
- Vite (build tool)
- TailwindCSS (styling)
- Zustand (state management)

**Infrastructure**
- Docker & Docker Compose (local dev)
- Kubernetes (production)
- AWS (EKS, RDS, S3, ElastiCache)

### System Components

```
┌─────────────────┐
│   Frontend      │
│   (React TS)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   API Gateway   │
│   (FastAPI)     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────┐   ┌─────────────────┐
│Redis│   │  Agent System   │
└─────┘   │  (LangGraph)    │
          │  ┌─────────────┐│
          │  │ Supervisor  ││
          │  └──────┬──────┘│
          │    ┌────┴────┐  │
          │    ▼    ▼    ▼  │
          │   P2P  O2C  R2R │
          └────────┬────────┘
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
    ┌──────┐  ┌──────┐  ┌──────┐
    │ ERP  │  │ Bank │  │ OCR  │
    └──────┘  └──────┘  └──────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Docker** and **Docker Compose** (for local development)
- **Python 3.11+** (if running without Docker)
- **Node.js 20+** (if running frontend without Docker)
- **Anthropic API Key** ([Get one here](https://console.anthropic.com/))
- **Google Cloud Vision API** credentials (optional, for OCR)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/akaash-nigam/ccw-AutonomousFinance.git
   cd ccw-AutonomousFinance
   ```

2. **Set up environment variables**
   ```bash
   # Backend
   cp backend/.env.example backend/.env
   # Edit backend/.env and add your API keys
   ```

3. **Start all services with Docker Compose**
   ```bash
   cd infrastructure
   docker-compose up -d
   ```

   This will start:
   - **Backend API** on `http://localhost:8000`
   - **Frontend** on `http://localhost:3000`
   - **PostgreSQL** on `localhost:5432`
   - **Redis** on `localhost:6379`
   - **RabbitMQ** on `localhost:5672` (Management UI: `http://localhost:15672`)

4. **Access the application**
   - **Frontend**: http://localhost:3000
   - **API Docs**: http://localhost:8000/api/v1/docs
   - **Health Check**: http://localhost:8000/health
   - **RabbitMQ Management**: http://localhost:15672 (guest/guest)

5. **Run database migrations** (first time only)
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

### Development Without Docker

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up .env file
cp .env.example .env
# Edit .env with your API keys and database connection

# Run migrations
alembic upgrade head

# Start development server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_agents.py

# Run with verbose output
pytest -v
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm run test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test -- --watch
```

---

## 📦 Project Structure

```
autonomous-finance/
├── backend/                    # Python FastAPI backend
│   ├── src/
│   │   ├── agents/            # AI agent implementations
│   │   ├── api/               # FastAPI routes
│   │   ├── core/              # Core config & utilities
│   │   ├── integrations/      # ERP, OCR, LLM integrations
│   │   ├── models/            # Database models
│   │   ├── services/          # Business logic
│   │   └── schemas/           # Pydantic schemas
│   ├── tests/                 # Backend tests
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # React TypeScript frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API clients
│   │   └── store/             # State management
│   ├── tests/                 # Frontend tests
│   └── package.json           # Node dependencies
│
├── infrastructure/             # Docker & K8s configs
│   ├── docker-compose.yml     # Local development
│   └── k8s/                   # Kubernetes manifests
│
├── docs/                       # Documentation
│   ├── PRD-Autonomous-Finance-Backoffice.md
│   ├── PRODUCT-ROADMAP.md
│   └── DEVELOPMENT-PLAN.md
│
└── .github/
    └── workflows/             # CI/CD pipelines
```

---

## 🎯 MVP Scope (Months 1-3)

### Features

✅ **Procure-to-Pay (P2P)**
- Invoice ingestion with OCR + LLM extraction
- 3-way match (Invoice ↔ PO ↔ GR) with AI exception handling
- Payment scheduling (sandbox mode, no live execution)

✅ **Bank Reconciliation**
- Auto-matching of bank transactions to GL
- Exception handling with AI suggestions
- Reconciliation reports

✅ **Record-to-Report (R2R)**
- Basic journal automation (depreciation, accruals)
- Close checklist and orchestration
- Real-time close status dashboard

✅ **Audit & Compliance**
- Evidence pack generation for every transaction
- Immutable audit trail with reasoning chains
- Exception review dashboard

### Success Criteria

| Metric | Target |
|--------|--------|
| Auto-processed invoices | 70% |
| Bank transactions auto-matched | 80% |
| Close duration | 5 days (vs. 8-day baseline) |
| Invoice processing time | <5 minutes (vs. 45 min) |
| System uptime | 99.5% |
| Finance team NPS | ≥40 |

---

## 🛣️ Roadmap

### Phase 1: MVP (Months 1-3) ✅ Current
- Single entity, P2P + Bank Rec
- 70% automation rate
- 5-day close

### Phase 2: Expansion (Months 4-6)
- Multi-entity (3 entities)
- O2C (cash application, dunning)
- Advanced journals (FX, leases)
- Live payment execution
- 85% automation rate, 3-day close

### Phase 3: Full Autonomy (Months 7-12)
- Tax filing automation
- Adaptive learning
- M&A entity onboarding
- Multi-country deployment
- 95% automation rate, 1.5-day close

See [Product Roadmap](./docs/PRODUCT-ROADMAP.md) for detailed epic breakdown.

---

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines (coming soon).

### Development Workflow

1. Create a feature branch: `git checkout -b feature/EPIC-ID-description`
2. Make changes with tests (TDD preferred)
3. Run linters and tests locally
4. Push and create a Pull Request
5. CI runs tests and checks coverage
6. Get 1+ peer reviews
7. Merge to `main`

### Code Quality

**Backend**
- Black (formatting)
- Ruff (linting)
- MyPy (type checking)
- 80%+ test coverage

**Frontend**
- Prettier (formatting)
- ESLint (linting)
- TypeScript strict mode
- 80%+ test coverage

---

## 📝 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

---

## 🔒 Security

- All API keys and secrets must be stored in `.env` (never commit to git)
- OAuth 2.0 for authentication
- Role-based access control (RBAC)
- Encrypted data at rest (AES-256) and in transit (TLS 1.3)
- Immutable audit logs for compliance
- Regular security scans and penetration testing

**Reporting Security Issues**: Please email security@company.com (do not create public issues)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Anthropic** for Claude Sonnet 4.5 and frontier AI capabilities
- **LangChain/LangGraph** for agent orchestration framework
- **FastAPI** for high-performance Python APIs
- **React** and the amazing frontend ecosystem

---

## 📞 Support

- **Documentation**: [./docs](./docs)
- **Issues**: [GitHub Issues](https://github.com/akaash-nigam/ccw-AutonomousFinance/issues)
- **Email**: aakash@company.com

---

## 🌟 Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Built with ❤️ by the Autonomous Finance Team**

*Transforming financial operations with frontier AI*
