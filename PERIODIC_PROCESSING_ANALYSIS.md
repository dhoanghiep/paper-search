# Periodic Processing Architecture Analysis

## Current State Assessment

### 📍 Where Periodic Processing Lives Now

**Location:** `app/scheduler.py` + `app/main.py` (FastAPI lifespan)

**Current Implementation:**
```python
# app/scheduler.py
- scrape_all_sources()    # Runs at 6:00 AM daily
- process_papers_job()    # Runs every 2 hours
- daily_report_job()      # Runs at 9:00 AM daily

# app/main.py
- Scheduler starts when FastAPI app starts
- Scheduler stops when FastAPI app stops
```

### 🔍 Architecture Analysis

```
┌─────────────────────────────────────────────────────────────┐
│                     Current Architecture                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐         ┌──────────────┐                  │
│  │   CLI        │         │   Frontend   │                  │
│  │              │         │              │                  │
│  │ - Manual     │         │ - View only  │                  │
│  │   commands   │         │ - No jobs    │                  │
│  │ - One-time   │         │              │                  │
│  │   execution  │         │              │                  │
│  └──────────────┘         └──────────────┘                  │
│         │                        │                           │
│         │                        │                           │
│         ▼                        ▼                           │
│  ┌─────────────────────────────────────────┐                │
│  │         FastAPI App (app/main.py)       │                │
│  │                                          │                │
│  │  ┌────────────────────────────────────┐ │                │
│  │  │  Scheduler (app/scheduler.py)      │ │                │
│  │  │                                     │ │                │
│  │  │  • Runs in background              │ │                │
│  │  │  • Starts with FastAPI             │ │                │
│  │  │  • APScheduler (BackgroundScheduler)│ │               │
│  │  │                                     │ │                │
│  │  │  Jobs:                              │ │                │
│  │  │  - scrape_all_sources() @ 6 AM     │ │                │
│  │  │  - process_papers_job() @ every 2h │ │                │
│  │  │  - daily_report_job() @ 9 AM       │ │                │
│  │  └────────────────────────────────────┘ │                │
│  │                                          │                │
│  │  ┌────────────────────────────────────┐ │                │
│  │  │  API Endpoints (/jobs/*)           │ │                │
│  │  │                                     │ │                │
│  │  │  • POST /jobs/scrape               │ │                │
│  │  │  • POST /jobs/process              │ │                │
│  │  │  • GET  /jobs/status               │ │                │
│  │  │  • GET  /jobs/scheduler/status     │ │                │
│  │  └────────────────────────────────────┘ │                │
│  └─────────────────────────────────────────┘                │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Recommended Architecture

### **Option 1: Keep Current (FastAPI-Embedded) ✅ RECOMMENDED**

**Best for:** Small to medium deployments, single-server setups

**Pros:**
- ✅ Already implemented and working
- ✅ Simple deployment (one process)
- ✅ No additional infrastructure needed
- ✅ Scheduler lifecycle tied to API
- ✅ Easy monitoring via API endpoints

**Cons:**
- ❌ Scheduler stops if API crashes
- ❌ Can't scale scheduler independently
- ❌ Jobs run in same process as API

**When to use:**
- Development and testing
- Single-server production
- Low to medium job frequency
- Jobs complete quickly (< 5 minutes)

### **Option 2: Separate Background Worker**

**Best for:** Production deployments, high-volume processing

**Architecture:**
```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   CLI        │     │   Frontend   │     │  Background  │
│              │     │              │     │   Worker     │
│ - Manual     │     │ - Dashboard  │     │              │
│   commands   │     │ - Monitoring │     │ - Scheduler  │
└──────┬───────┘     └──────┬───────┘     │ - Jobs       │
       │                    │              │ - Queue      │
       │                    │              └──────┬───────┘
       ▼                    ▼                     │
┌─────────────────────────────────────────┐      │
│         FastAPI App                     │      │
│                                          │      │
│  • API endpoints                        │◄─────┘
│  • Job triggers                         │
│  • Status monitoring                    │
│  • Queue management                     │
└─────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│         Message Queue (Redis/RabbitMQ)  │
└─────────────────────────────────────────┘
```

**Pros:**
- ✅ Independent scaling
- ✅ Better fault tolerance
- ✅ Can run long jobs
- ✅ Multiple workers possible

**Cons:**
- ❌ More complex setup
- ❌ Requires message queue (Redis/RabbitMQ)
- ❌ More infrastructure to manage

### **Option 3: Systemd Service (Linux)**

**Best for:** Linux servers, production deployments

**Architecture:**
```
┌──────────────────────────────────────────┐
│  Systemd Services                        │
│                                           │
│  ┌────────────────────────────────────┐  │
│  │  paper-search-api.service          │  │
│  │  - FastAPI app                     │  │
│  │  - Port 8000                       │  │
│  └────────────────────────────────────┘  │
│                                           │
│  ┌────────────────────────────────────┐  │
│  │  paper-search-scheduler.service    │  │
│  │  - Standalone scheduler            │  │
│  │  - Runs jobs                       │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

**Pros:**
- ✅ OS-level process management
- ✅ Auto-restart on failure
- ✅ Independent processes
- ✅ System logging

**Cons:**
- ❌ Linux-only
- ❌ Requires root/sudo access
- ❌ More deployment complexity

## 📊 Monitoring Strategy

### **Where to Monitor From**

#### 1. **CLI (Best for: Admins, DevOps)** ✅ RECOMMENDED

**Add monitoring commands:**
```bash
./paper jobs status          # Show processing status
./paper jobs scheduler       # Show scheduled jobs
./paper jobs history         # Show job execution history
./paper jobs trigger scrape  # Manually trigger scraping
./paper jobs trigger process # Manually trigger processing
```

**Pros:**
- ✅ Quick access for admins
- ✅ Scriptable for automation
- ✅ No UI needed
- ✅ SSH-friendly

#### 2. **Frontend (Best for: End users, Stakeholders)**

**Add Jobs Dashboard page:**
```javascript
// frontend/js/components/Jobs.js
- Show scheduler status
- Show job history
- Show processing queue
- Trigger manual jobs
- Real-time updates
```

**Pros:**
- ✅ Visual monitoring
- ✅ Accessible to non-technical users
- ✅ Real-time updates
- ✅ Better UX

#### 3. **API Endpoints (Best for: Integration, Automation)**

**Current endpoints (already exist):**
```
GET  /jobs/status            # Processing status
GET  /jobs/scheduler/status  # Scheduler status
POST /jobs/scrape            # Trigger scraping
POST /jobs/process           # Trigger processing
```

**Pros:**
- ✅ Already implemented
- ✅ Integration-friendly
- ✅ Automation-ready

## 🚀 Recommended Implementation Plan

### **Phase 1: Enhance Current Setup (Immediate)**

1. **Add CLI monitoring commands**
   ```bash
   ./paper jobs status
   ./paper jobs scheduler
   ./paper jobs logs
   ```

2. **Add job history tracking**
   - Create `JobHistory` model
   - Track: job_type, start_time, end_time, status, result

3. **Add better logging**
   - Structured logging
   - Log rotation
   - Error tracking

### **Phase 2: Add Frontend Monitoring (Short-term)**

1. **Create Jobs Dashboard**
   - Show scheduler status
   - Show recent job runs
   - Show processing queue
   - Manual job triggers

2. **Add real-time updates**
   - WebSocket or polling
   - Live job status
   - Progress indicators

### **Phase 3: Production Hardening (Long-term)**

1. **Add job retry logic**
2. **Add job failure notifications**
3. **Add performance metrics**
4. **Consider separate worker if needed**

## 💡 Specific Recommendations

### **For Your Current Setup:**

**Keep:** FastAPI-embedded scheduler (Option 1)
- ✅ Simple and working
- ✅ Sufficient for current scale
- ✅ Easy to maintain

**Add:**
1. **CLI monitoring commands** (highest priority)
2. **Job history tracking** (medium priority)
3. **Frontend dashboard** (nice to have)

### **When to Migrate:**

Consider separate worker (Option 2) when:
- Processing > 1000 papers/day
- Jobs take > 5 minutes
- Need multiple workers
- API becomes slow during jobs

## 📝 Implementation Code

### **1. Add CLI Monitoring Commands**

```python
# app/cli/jobs.py
@click.group()
def jobs():
    """Monitor and manage background jobs"""
    pass

@jobs.command()
def status():
    """Show processing status"""
    # Call /jobs/status endpoint

@jobs.command()
def scheduler():
    """Show scheduler status"""
    # Call /jobs/scheduler/status endpoint

@jobs.command()
def trigger():
    """Trigger jobs manually"""
    # Interactive menu or subcommands
```

### **2. Add Job History Model**

```python
# app/models.py
class JobHistory(Base):
    __tablename__ = "job_history"
    
    id = Column(Integer, primary_key=True)
    job_type = Column(String)  # scrape, process, report
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    status = Column(String)  # success, failed, running
    result = Column(JSON)  # Store job results
    error = Column(Text)  # Store error if failed
```

### **3. Add Frontend Jobs Dashboard**

```javascript
// frontend/js/components/Jobs.js
export class Jobs {
    async render() {
        const status = await api.getJobStatus();
        const scheduler = await api.getSchedulerStatus();
        
        return `
            <div class="jobs-dashboard">
                <h2>Background Jobs</h2>
                <div class="scheduler-status">
                    Status: ${scheduler.status}
                    Next runs: ...
                </div>
                <div class="processing-status">
                    Processed: ${status.processed}
                    Pending: ${status.unprocessed}
                </div>
            </div>
        `;
    }
}
```

## 🎯 Final Recommendation

**For your current architecture:**

1. **Keep scheduler in FastAPI** (app/main.py + app/scheduler.py)
   - It's working and appropriate for your scale

2. **Add CLI monitoring** (highest priority)
   - Quick wins for admins
   - Easy to implement
   - Scriptable

3. **Add job history tracking** (medium priority)
   - Better visibility
   - Debugging aid
   - Audit trail

4. **Add frontend dashboard** (nice to have)
   - Better UX
   - Stakeholder visibility
   - Real-time monitoring

5. **Monitor and scale later**
   - If jobs become slow or frequent
   - Consider separate worker then
   - Don't over-engineer now

**Summary:** Your current setup is good. Add monitoring through CLI first, then frontend. Only move to separate worker if you hit performance issues.
