# Workstream: Frontend Interface

**Status:** Ready to implement
**Priority:** CRITICAL
**Estimated Time:** 4-5 hours

---

## Tasks

### 1. Project Setup
- [ ] Initialize Vite + React + TypeScript
- [ ] Install dependencies (TailwindCSS, React Router, Axios)
- [ ] Configure build and dev server
- [ ] Set up folder structure

### 2. Core Pages
- [ ] Dashboard (home page)
- [ ] Papers List (table view)
- [ ] Paper Detail (single paper)
- [ ] Categories (management)
- [ ] Reports (viewer)

### 3. Features
- [ ] API client setup
- [ ] Search functionality
- [ ] Filter by category
- [ ] Responsive layout

---

## Implementation Steps

### Step 1: Initialize Frontend
```bash
cd /workshop/paper-search
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install -D tailwindcss postcss autoprefixer
npm install react-router-dom axios
npx tailwindcss init -p
```

### Step 2: Folder Structure
```
frontend/
├── src/
│   ├── components/
│   │   ├── Dashboard.tsx
│   │   ├── PapersList.tsx
│   │   ├── PaperDetail.tsx
│   │   └── Navbar.tsx
│   ├── api/
│   │   └── client.ts
│   ├── types/
│   │   └── index.ts
│   ├── App.tsx
│   └── main.tsx
```

### Step 3: Configure API Client
```typescript
// src/api/client.ts
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

export default api;
```

### Step 4: Run Dev Server
```bash
npm run dev
```

---

## Files to Create
- `frontend/src/components/Dashboard.tsx`
- `frontend/src/components/PapersList.tsx`
- `frontend/src/components/PaperDetail.tsx`
- `frontend/src/components/Navbar.tsx`
- `frontend/src/api/client.ts`
- `frontend/src/types/index.ts`
- `frontend/tailwind.config.js`

---

## Testing Checklist
- [ ] Dev server runs on http://localhost:5173
- [ ] Can navigate between pages
- [ ] API calls work (mock data OK initially)
- [ ] Responsive on mobile
- [ ] TailwindCSS styles applied

---

## Next Steps After Completion
- Connect to real backend API
- Add authentication
- Implement dark mode
- Add loading states
