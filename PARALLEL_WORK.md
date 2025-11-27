# Parallel Development Guide

## Two Workstreams Running Simultaneously

### 🔵 Workstream 1: arXiv Crawler (Backend)
**File:** `WORKSTREAM_ARXIV.md`
**Focus:** Data ingestion and scraping
**Terminal 1:**
```bash
cd /workshop/paper-search
source venv/bin/activate
# Work on backend Python code
```

### 🟢 Workstream 2: Frontend Interface
**File:** `WORKSTREAM_FRONTEND.md`
**Focus:** React UI development
**Terminal 2:**
```bash
cd /workshop/paper-search/frontend
npm run dev
# Work on React components
```

---

## How to Work in Parallel

### Option 1: Two Terminal Windows
1. Open Terminal 1 → Follow WORKSTREAM_ARXIV.md
2. Open Terminal 2 → Follow WORKSTREAM_FRONTEND.md
3. Work independently on each

### Option 2: tmux/screen
```bash
# Terminal 1
tmux new -s backend
cd /workshop/paper-search && source venv/bin/activate

# Terminal 2 (new window)
tmux new -s frontend
cd /workshop/paper-search/frontend && npm run dev

# Switch between: Ctrl+b then window number
```

### Option 3: VS Code Split Terminal
1. Split terminal (Ctrl+Shift+5)
2. Left pane: Backend work
3. Right pane: Frontend work

---

## Integration Points

Both workstreams are **independent** until:
- Backend has `/papers` API endpoint working
- Frontend needs real data (can use mock data initially)

**Integration happens in Phase 4**

---

## Progress Tracking

Update these files as you complete tasks:
- `WORKSTREAM_ARXIV.md` - Check off arXiv tasks
- `WORKSTREAM_FRONTEND.md` - Check off frontend tasks
- `PROGRESS.md` - Update overall progress

---

## Quick Start Commands

**Backend (arXiv):**
```bash
cd /workshop/paper-search
source venv/bin/activate
# Start implementing app/agents/scraper.py
```

**Frontend:**
```bash
cd /workshop/paper-search
npm create vite@latest frontend -- --template react-ts
cd frontend && npm install
```

---

## Communication Between Workstreams

**API Contract (already defined):**
- `GET /papers` - List papers
- `GET /papers/{id}` - Get paper detail
- `GET /categories` - List categories
- `GET /reports` - List reports

Frontend can use **mock data** until backend is ready.
