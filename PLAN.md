# Paper Search App - MCP Servers Plan

## MCP Servers to Build

### 1. ArXiv MCP Server
**Purpose:** Fetch papers from arXiv API
**Tools:**
- `search_papers` - Search by query, category, date range
- `get_paper_details` - Get full paper metadata by arXiv ID
- `get_recent_papers` - Fetch latest submissions

**Resources:**
- arXiv API endpoint configuration
- Rate limiting handling

**Status:** NOT STARTED

---

### 2. Database MCP Server
**Purpose:** PostgreSQL operations for papers, categories, reports
**Tools:**
- `query_papers` - Search/filter papers
- `add_paper` - Insert new paper
- `update_paper` - Update paper metadata
- `add_category` - Create category
- `assign_category` - Link paper to category
- `get_statistics` - Database stats

**Resources:**
- Database connection pool
- Query templates

**Status:** NOT STARTED

---

### 3. Summarization MCP Server
**Purpose:** Generate paper summaries using LLM
**Tools:**
- `summarize_paper` - Create brief summary from abstract
- `summarize_detailed` - In-depth analysis
- `extract_key_points` - Bullet point extraction

**Resources:**
- LLM API configuration (Bedrock/OpenAI)
- Prompt templates

**Status:** NOT STARTED

---

### 4. Classification MCP Server
**Purpose:** Categorize papers automatically
**Tools:**
- `classify_paper` - Assign to existing categories
- `suggest_category` - Propose new category
- `find_related_papers` - Similarity search

**Resources:**
- Category taxonomy
- Embedding model

**Status:** NOT STARTED

---

### 5. Report Generation MCP Server
**Purpose:** Create daily/weekly/monthly reports
**Tools:**
- `generate_daily_report` - Papers from last 24h
- `generate_weekly_report` - Weekly digest
- `generate_monthly_report` - Monthly summary
- `generate_paper_report` - Single paper deep dive

**Resources:**
- Report templates
- Formatting utilities

**Status:** NOT STARTED

---

### 6. Email Notification MCP Server
**Purpose:** Send email alerts
**Tools:**
- `send_new_paper_alert` - Notify about new papers
- `send_report` - Email report
- `send_custom_alert` - Custom notifications

**Resources:**
- SMTP configuration
- Email templates

**Status:** NOT STARTED

---

## Build Order Priority

1. **ArXiv MCP Server** (CRITICAL) - Data ingestion
2. **Database MCP Server** (CRITICAL) - Data persistence
3. **Summarization MCP Server** (HIGH) - Core feature
4. **Classification MCP Server** (HIGH) - Core feature
5. **Report Generation MCP Server** (MEDIUM) - User value
6. **Email Notification MCP Server** (LOW) - Nice to have

---

## Integration Points

```
ArXiv MCP → Database MCP → Summarization MCP → Classification MCP
                ↓
         Report Generation MCP → Email MCP
```

---

---

## 7. Frontend Interface MCP Server
**Purpose:** Web UI for viewing and managing papers
**Tools:**
- `serve_frontend` - Serve static files
- `get_ui_config` - Frontend configuration

**Resources:**
- React/Vue/Svelte components
- API client for backend

**Pages:**
- Dashboard - Recent papers overview
- Papers List - Searchable/filterable table
- Paper Detail - Full paper view with summary
- Categories - Manage categories
- Reports - View/generate reports
- Settings - Email preferences, API keys

**Status:** NOT STARTED

---

## Build Order Priority

1. **ArXiv MCP Server** (CRITICAL) - Data ingestion
2. **Database MCP Server** (CRITICAL) - Data persistence
3. **Summarization MCP Server** (HIGH) - Core feature
4. **Classification MCP Server** (HIGH) - Core feature
5. **Report Generation MCP Server** (MEDIUM) - User value
6. **Email Notification MCP Server** (LOW) - Nice to have
7. **Frontend Interface MCP Server** (MEDIUM) - User interface

---

## Integration Points

```
ArXiv MCP → Database MCP → Summarization MCP → Classification MCP
                ↓
         Report Generation MCP → Email MCP
                ↓
         Frontend Interface MCP
```

---

## Technical Requirements

**Backend:**
- Python 3.10+
- MCP SDK
- FastAPI for MCP server hosting
- PostgreSQL client
- httpx for HTTP requests
- boto3 for AWS Bedrock (if using)

**Frontend:**
- React 18+ or Vue 3+ or Svelte
- TailwindCSS or Material-UI
- Axios/Fetch for API calls
- React Query or SWR for data fetching
- React Router or Vue Router
