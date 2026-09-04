# CuraVia

CuraVia is organized as one parent project containing three independent Git repositories:

- **Backend**: FastAPI, MySQL, Redis, Celery, Alembic, and the conversation services. See [backend/README.md](backend/README.md).
- **Frontend**: Vite, React, TypeScript, and Tailwind chat application. See [frontend/README.md](frontend/README.md).
- **Website**: The CuraVia public website. See [website/README.md](website/README.md).

## Clone the complete project

Clone the parent repository and initialize all three submodules:

```bash
git clone --recurse-submodules https://github.com/bilmoBaggins/CuraVia.git
cd CuraVia
```

If the repository was cloned without submodules:

```bash
git submodule update --init --recursive
```

The parent repository records the exact commit of each project, so a clone is reproducible.

## Project layout

```text
CuraVia/
├── backend/    # Python backend repository
├── frontend/   # React frontend repository
└── website/    # Website repository
```

## Backend

Run backend commands from the `backend/app` directory. Install Docker Desktop, make sure Docker is running, then start the services:

```bash
cd backend/app
docker compose up --build
```

For later starts:

```bash
docker compose up -d
docker compose run --rm fastapi alembic upgrade head
```

Create or apply migrations:

```bash
docker compose run --rm fastapi alembic revision --autogenerate -m "describe the change"
docker compose run --rm fastapi alembic upgrade head
```

Stop the services:

```bash
docker compose down
```

Useful Redis commands:

```bash
docker exec redis_service redis-cli FLUSHALL
docker exec redis_service redis-cli KEYS '*'
docker exec redis_service redis-cli GET <key>
```

Seed development data:

```bash
docker compose run --rm fastapi python seed/seed.py
```

Local quality checks:

```bash
pip install black flake8 mypy
black --check
flake8 --check
mypy --check
```

See [backend/README.md](backend/README.md) for the complete backend instructions.

## Frontend

Run frontend commands from the `frontend` directory:

```bash
cd frontend
npm install
npm run dev
```

Open the URL printed by Vite, usually `http://localhost:5173`.

Prettier checks:

```bash
npx prettier --check "src/**/*.{ts,tsx,js,jsx,css}"
npx prettier --write "src/**/*.{ts,tsx,js,jsx,css}"
```

See [frontend/README.md](frontend/README.md) for the original frontend README.

## Website

The website is contained in the `website` submodule. Open [website/index.html](website/index.html) directly in a browser or serve the directory with a local static web server.

See [website/README.md](website/README.md) for the website repository README.

## Updating submodules

To fetch the latest configured commits from all submodule remotes:

```bash
git submodule update --remote --merge
```

Review the resulting changes, then commit the updated submodule pointers in the parent repository:

```bash
git add backend frontend website
git commit -m "Update project submodules"
git push origin main
```

Changes made inside a submodule must be committed and pushed from that submodule's own directory before updating the pointer in the parent repository.

## Repositories

- Parent: https://github.com/bilmoBaggins/CuraVia
- CuraVia-backend: https://github.com/curavia/CuraVia-backend
- Frontend: https://github.com/curavia/Curavia-frontend
- Website: https://github.com/curavia/CuraVia-website
