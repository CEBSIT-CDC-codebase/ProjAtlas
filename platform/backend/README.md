# AI Atlas Backend

> Backend service for the AI Atlas platform: provides **user / session / message** management via Flask, and LLM assistant conversation capabilities by integrating the `atlas_assistant` package from [`multi-agent-framework`](../../multi-agent-framework), part of this monorepo.

---

## Features

- User management (CRUD, soft delete)
- Session management (isolated per user)
- Message management (supports `role` / `task` and structured fields like `neurons` / `regions` / `matrix`)
- Asynchronous conversation: `flask_executor` calls the LLM assistant in the background to generate replies without blocking requests
- Database migrations (Flask-Migrate)
- Cross-origin support (flask-cors)

## Tech Stack

- Python 3.10
- Flask / Flask-SQLAlchemy / Flask-Migrate
- MySQL 8.x
- flask-cors, flask-executor
- `atlas_assistant` (installed from [`../../multi-agent-framework`](../../multi-agent-framework), provides RAG / agent conversation capabilities, includes PyTorch dependencies)

## Directory Structure

```
ProjAtlas/
├── multi-agent-framework/   # Provides the `atlas_assistant` package (see its own README)
└── platform/backend/
    ├── app/                     # Application main package
    │   ├── __init__.py          # Factory function create_app(), registers blueprints and extensions
    │   ├── models/              # SQLAlchemy models: User / Session / Message
    │   └── routes/              # Blueprints: user / session / message
    ├── config.py                # Configuration (reads environment variables)
    ├── run.py                   # Entry point: initializes DB, loads assistant, starts service
    ├── docker-compose.yml       # Local MySQL service
    ├── Dockerfile               # Based on PyTorch CUDA image (build context: repo root)
    ├── requirements.txt         # Python dependencies
    └── .env.example             # Environment variable template (copy to .env and fill in)
```

> **About `atlas_assistant`**: it is provided by [`multi-agent-framework`](../../multi-agent-framework),
> a sibling directory in this monorepo (not a git submodule). Install it in editable mode
> (see step 3 below) so that `from atlas_assistant.assistant import ChatSession` resolves
> correctly.

## System Requirements

- **Linux recommended** (Ubuntu, etc.). Dependencies for this project (especially PyTorch/CUDA packages pulled in by `atlas_assistant`) are **difficult to install on Windows**. Official support is only guaranteed for **Linux** environments.
- Python 3.10
- A running MySQL 8.x instance (can be started quickly with docker-compose)
- For GPU inference: Linux + NVIDIA drivers + CUDA

## Quick Start (Linux)

### 1. Clone the repository

```bash
git clone <your-repo-url> ProjAtlas
cd ProjAtlas/platform/backend
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env and fill in your database and LLM gateway information
```

See the "Environment Variables" section below for variable descriptions.

### 3. Install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e ../../multi-agent-framework   # installs the atlas_assistant package
```

### 4. Start the database (optional, using docker-compose)

```bash
docker compose up -d mysql
```

### 5. Run the service

```bash
# Development mode (debugger enabled, local only)
python run.py

# Production mode (debug disabled, using WSGI server, e.g., gunicorn)
gunicorn -w 4 -b 127.0.0.1:5000 run:app
```

The service listens on port `5000` by default.

## Environment Variables

Configure in `.env` in the project root (**do not commit `.env`**). All values below are placeholders — replace them with your actual values:

| Variable | Description | Example |
|----------|-------------|---------|
| `DB_HOST` | MySQL host address | `127.0.0.1` |
| `DB_PORT` | MySQL port | `3306` |
| `DB_DATABASE` | Database name | `atlas_dev` |
| `DB_PASSWORD` | Database password (**use a strong password**) | — |

`MYSQL_ROOT_PASSWORD` in `docker-compose.yml` reads from `${DB_PASSWORD}`, so ensure `DB_PASSWORD` is set in `.env`.

## Docker

Build context must be the monorepo root (not this directory), so that
`../multi-agent-framework` is visible during the build:

```bash
# From the repository root
docker build -f platform/backend/Dockerfile -t ai-atlas-backend .
docker run -p 5000:5000 --env-file platform/backend/.env ai-atlas-backend
```

Build and run inside a Linux container. Note that the image is based on the PyTorch CUDA runtime, is large in size, and requires pulling over the network.

## API Overview

No unified prefix; routes are organized by blueprint:

### User `user`
| Method | Path | Description |
|--------|------|-------------|
| GET | `/get-user/<email>` | Query active (non-deleted) user |
| POST | `/add-user` | Add new user (requires `email`) |
| PUT | `/update-user/<id>` | Update user |
| DELETE | `/delete-user/<id>` | Soft delete user |

### Session `session`
| Method | Path | Description |
|--------|------|-------------|
| GET | `/get-sessions/<userId>` | Get all sessions for a user |
| GET | `/get-session/<sessionId>` | Get a single session |
| POST | `/add-session` | Create new session (requires `userId`, `name`) |
| PUT | `/update-session/<sessionId>` | Update session |
| DELETE | `/delete-session/<sessionId>` | Soft delete session |

### Message `message`
| Method | Path | Description |
|--------|------|-------------|
| GET | `/get-messages/<sessionId>` | Get all messages for a session |
| GET | `/get-message/<messageId>` | Get a single message |
| POST | `/add-message` | Add a new message and **asynchronously trigger assistant reply** (requires `sessionId`, `role`, `task`) |
| PUT | `/update-message/<messageId>` | Update message |
| DELETE | `/delete-message/<messageId>` | Soft delete message |

## Security Notes

- **No authentication on API endpoints.** Write operations (creating, updating, or deleting users, sessions, or messages) do not verify caller identity — anyone with network access to this service can modify data. This is acceptable only when the database and this service are kept on a private/internal network with no public exposure. If you deploy this service on a public network, add your own access-control layer (API key, reverse-proxy auth, etc.) first.
- **Do not commit `.env`, logs (`*.log`), IDE configs (`.idea/`, etc.) to the repository** — they are ignored in `.gitignore`.
- Before public release / open-sourcing, ensure no real secrets remain in **git history** (see "Pre-release Checklist" below).
- `run.py` defaults to `debug=True` — **for local development only**; disable the debugger in production (exposing the debugger publicly = remote code execution risk).
- `CORS(app)` allows all origins by default; restrict allowed origins as needed in production.
- Dependency versions (Flask 2.0.x / Werkzeug 2.0.x) are relatively old; consider upgrading to supported versions before release to address known vulnerabilities.

## Pre-release Checklist

- [ ] Rotated any real secrets (credentials, API keys, etc.) that were previously committed to `.env`, on the provider/platform side
- [ ] Removed `.env`, `flask.log`, `.idea/` from git tracking (this repository already has them ignored)
- [ ] Confirmed no real secrets exist in git history (use `git filter-repo` if necessary)
- [ ] `multi-agent-framework` installed in editable mode (`pip install -e ../../multi-agent-framework`)
- [ ] Upgraded dependency versions with known vulnerabilities

## Citation

See the [repository root README](../../README.md#citation) for the current citation.

## License

This code is licensed under [Apache License 2.0](../../LICENSE), the same license
covering the rest of the ProjAtlas repository. See [NOTICE](../../NOTICE) for
third-party acknowledgements.