# AIMU GitHub-Based Update Server

Lightweight update server that uses GitHub Releases as storage backend.

## Features

✅ **Zero File Storage** - All files hosted on GitHub Releases (free, unlimited)
✅ **Lightweight** - Perfect for Render free tier
✅ **Simple Management** - Use GitHub UI to create releases
✅ **Fast CDN** - GitHub's global CDN for downloads
✅ **Analytics** - Track update checks and installations

## Architecture

```
Client (AIMU.exe)
    ↓ GET /api/updates/check
Render (Update Server)
    ↓ GitHub Releases API
GitHub Releases
    ↓ Direct download link
Client downloads from GitHub CDN
```

## Quick Start

### 1. Create GitHub Repository

Create a repository to host your releases (public or private):
- Repository name: `AIMU` (or any name)
- Owner: `Tayeb2323` (your GitHub username)

### 2. Deploy to Render

**Option A: One-Click Deploy**
1. Push this folder to GitHub
2. Connect to Render
3. Render will auto-detect `render.yaml`

**Option B: Manual Deploy**
1. Go to [render.com](https://render.com)
2. New → Web Service
3. Connect your GitHub repo
4. Select `github_update_server` directory
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `gunicorn app:app`

### 3. Configure Environment Variables

In Render dashboard, set:
- `GITHUB_OWNER`: `Tayeb2323`
- `GITHUB_REPO`: `AIMU`
- `GITHUB_TOKEN`: (Optional) Personal access token for private repos

### 4. Custom Domain (Optional)

In Render:
- Settings → Custom Domain
- Add: `api.aimu.hds-jp.com` or similar
- Update DNS CNAME record

## Creating Releases on GitHub

### Method 1: GitHub Web UI

1. Go to your repository: `https://github.com/Tayeb2323/AIMU`
2. Click "Releases" → "Create a new release"
3. Fill in:
   - **Tag**: `v1.0.0` (must follow semantic versioning)
   - **Title**: `AIMU v1.0.0`
   - **Description**: Release notes (markdown supported)
   - **Attach binaries**: Upload `AIMU_v1.0.0.zip` or `AIMU.exe`
4. Click "Publish release"

### Method 2: GitHub CLI

```bash
# Build your application
python build_AIMU_1_0_0.py

# Create a zip package
cd dist/AIMU_1_0_0
7z a AIMU_v1.0.0.zip *
cd ../..

# Create GitHub release
gh release create v1.0.0 \
  --title "AIMU v1.0.0" \
  --notes "Initial release with ML/DL capabilities" \
  dist/AIMU_1_0_0/AIMU_v1.0.0.zip
```

### Method 3: Automated Script

```bash
python create_github_release.py --version 1.0.0 --file dist/AIMU_1_0_0.zip
```

## API Endpoints

### Check for Updates
```bash
GET /api/updates/check?version=1.0.0&platform=win32&client_id=uuid
```

Response:
```json
{
  "update_available": true,
  "latest_version": "1.1.0",
  "current_version": "1.0.0",
  "release_date": "2025-01-15T10:00:00Z",
  "release_notes": "New features...",
  "download_url": "https://github.com/Tayeb2323/AIMU/releases/download/v1.1.0/AIMU_v1.1.0.zip",
  "file_size": 52428800,
  "file_name": "AIMU_v1.1.0.zip"
}
```

### Get Latest Release
```bash
GET /api/updates/latest
```

### List All Versions
```bash
GET /api/updates/versions
```

### Health Check
```bash
GET /health
```

### Report Installation (Client)
```bash
POST /api/updates/install
{
  "client_id": "uuid",
  "version": "1.1.0"
}
```

### Get Statistics
```bash
GET /api/updates/stats
```

## Testing

### Test Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GITHUB_OWNER=Tayeb2323
export GITHUB_REPO=AIMU

# Run server
python app.py
```

### Test Endpoints
```bash
# Health check
curl http://localhost:5000/health

# Check for updates
curl "http://localhost:5000/api/updates/check?version=0.9.0&platform=win32&client_id=test"

# Get latest release
curl http://localhost:5000/api/updates/latest

# List versions
curl http://localhost:5000/api/updates/versions
```

## Client Configuration

Update your `aimu_client_config.yaml`:

```yaml
updates:
  auto_check: true
  check_interval_hours: 24
  update_url: "https://your-service.onrender.com/api/updates"  # or custom domain
  auto_install: false
```

## GitHub Token (Optional)

For private repositories or higher rate limits:

1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token with `repo` scope
3. Add to Render environment variables as `GITHUB_TOKEN`

Without token:
- Rate limit: 60 requests/hour
- Public repos only

With token:
- Rate limit: 5000 requests/hour
- Access to private repos

## Cost Analysis

**Render Free Tier:**
- ✅ 750 hours/month (enough for 1 service)
- ✅ Auto-sleep after inactivity
- ✅ Wake up on first request (~30 seconds)

**GitHub:**
- ✅ Unlimited releases storage (public repos)
- ✅ Free CDN bandwidth
- ✅ No hosting costs

**Total Cost: $0/month** 🎉

## Monitoring

### Check Service Health
```bash
curl https://your-service.onrender.com/health
```

### View Logs (Render)
- Dashboard → your service → Logs

### Update Statistics
```bash
curl https://your-service.onrender.com/api/updates/stats
```

## Troubleshooting

### Service Returns 404
- Check Render deployment logs
- Verify build succeeded
- Check health endpoint

### "No releases available"
- Verify GitHub repository exists
- Check releases are published (not draft)
- Verify `GITHUB_OWNER` and `GITHUB_REPO` are correct

### Rate Limit Exceeded
- Add `GITHUB_TOKEN` environment variable
- This increases limit from 60 to 5000 req/hour

### Asset Not Found
- Ensure you uploaded .zip or .exe file to release
- Check file name format

## Next Steps

1. ✅ Deploy server to Render
2. ✅ Create first GitHub release (v1.0.0)
3. ✅ Update client configuration
4. ✅ Build AIMU with update system
5. ✅ Test update check from client

## Support

- **GitHub Issues**: Report bugs in your AIMU repository
- **Render Status**: Check render.com status page
- **Logs**: View real-time logs in Render dashboard
