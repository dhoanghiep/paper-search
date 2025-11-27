# Paper Search Frontend

Lightweight vanilla JavaScript frontend for the Paper Search application.

## Features

- Dashboard with statistics
- Papers list with search
- Paper detail view
- Categories management
- Reports viewer
- Responsive design

## Running the Frontend

```bash
cd /workshop/paper-search/frontend
python3 server.py
```

The frontend will be available at: http://localhost:5173

## Requirements

- Python 3.x (for dev server)
- Backend API running at http://localhost:8000

## Structure

```
frontend/
├── index.html          # Main HTML page
├── css/
│   └── styles.css      # Styles
├── js/
│   ├── app.js          # Router and main app
│   ├── api.js          # API client
│   └── components/     # Page components
│       ├── Dashboard.js
│       ├── PapersList.js
│       ├── PaperDetail.js
│       ├── Categories.js
│       └── Reports.js
└── server.py           # Dev server
```

## API Endpoints Used

- `GET /stats` - Dashboard statistics
- `GET /papers` - List all papers
- `GET /papers/{id}` - Get paper details
- `GET /categories` - List categories
- `GET /reports` - List reports
