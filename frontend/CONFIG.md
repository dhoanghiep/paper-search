# Frontend Configuration

## Automatic Configuration (Default)

The frontend automatically detects the backend using the same hostname you access it from.

**Example:**
- If you access frontend at: `http://your-vm-ip:5173`
- It will connect to backend at: `http://your-vm-ip:8000`

## Manual Configuration

If you need to specify a different backend URL, edit `frontend/config.js`:

```javascript
window.API_BASE = 'http://YOUR_VM_IP_OR_DOMAIN:8000';
```

## Troubleshooting

1. **Check browser console** - Open DevTools (F12) and look for:
   - "Frontend URL: ..."
   - "API Base URL: ..."

2. **Verify backend is accessible** - Test from your browser:
   ```
   http://YOUR_VM_IP:8000/stats
   ```

3. **Check CORS** - Backend allows all origins by default

## Current Setup

- Frontend: Port 5173
- Backend: Port 8000
- CORS: Enabled for all origins
