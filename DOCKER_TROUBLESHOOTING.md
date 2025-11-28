# Docker Network Troubleshooting

If you're experiencing network timeouts when pulling Docker images, try these solutions:

## Quick Fixes

1. **Restart Docker Desktop**
   - Close Docker Desktop completely
   - Restart it and wait for it to fully start
   - Try `docker compose up` again

2. **Check Docker Desktop Settings**
   - Open Docker Desktop
   - Go to Settings → Resources → Network
   - Ensure "Use kernel networking" is enabled (or try disabling it)
   - Apply & Restart

3. **Try Pulling Images Individually**
   ```powershell
   docker pull python:3.13-slim-bookworm
   docker pull node:20-alpine
   docker pull postgres:17-alpine
   ```

4. **Check for VPN/Proxy**
   - If you're on a VPN, try disconnecting temporarily
   - If behind a corporate proxy, configure Docker Desktop proxy settings:
     - Settings → Resources → Proxies
     - Add your proxy configuration

5. **Use Alternative Registry (if available)**
   - Some organizations have internal Docker registries
   - Check with your IT department

6. **Increase Docker Timeout**
   - Docker Desktop → Settings → Docker Engine
   - Add: `"max-concurrent-downloads": 3`
   - Apply & Restart

7. **Clear Docker Cache and Retry**
   ```powershell
   docker system prune -a
   docker compose up --build
   ```

## Alternative: Use Pre-built Images Locally

If network issues persist, you can:
1. Pull images on a machine with better connectivity
2. Save them: `docker save python:3.13-slim-bookworm > python.tar`
3. Load them: `docker load < python.tar`

## Verify Image Tags

The current Dockerfile uses:
- `python:3.13-slim-bookworm` (backend)
- `node:20-alpine` (frontend)
- `postgres:17-alpine` (database)

If `python:3.13-slim-bookworm` doesn't exist, try:
- `python:3.13-slim` (without bookworm)
- `python:3.12-slim-bookworm` (if 3.13 isn't available)

