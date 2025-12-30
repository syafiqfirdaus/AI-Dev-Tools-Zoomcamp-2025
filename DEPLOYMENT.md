# Deployment Guide

## Prerequisites

- Docker and Docker Compose installed (for local deployment)
- Render account (or alternative cloud provider)
- PostgreSQL database (managed service recommended)

---

## Local Deployment with Docker

### 1. Build and Run with Docker Compose

```bash
# From the project root directory
docker-compose up --build
```

This will start:
- PostgreSQL database on port 5432
- Backend API on port 8000
- Frontend on port 80

Access the application at `http://localhost`

### 2. Stop the Services

```bash
docker-compose down
```

### 3. Clean Up (including volumes)

```bash
docker-compose down -v
```

---

## Cloud Deployment (Render)

### Why Render?

- Free tier available
- Easy PostgreSQL integration
- Automatic deployments from GitHub
- Built-in SSL certificates

### Backend Deployment

1. **Create a new Web Service** on Render
2. **Connect your GitHub repository**
3. **Configure the service:**
   - **Name**: `finance-calc-backend`
   - **Environment**: `Docker`
   - **Dockerfile path**: `Dockerfile.server`
   - **Port**: `8000`

4. **Add Environment Variables:**
   ```
   DATABASE_URL=<your-postgres-url>
   ENVIRONMENT=production
   CORS_ORIGINS=https://your-frontend-url.onrender.com
   ```

5. **Deploy**

### Frontend Deployment

1. **Create a new Static Site** on Render
2. **Configure:**
   - **Build Command**: `cd client && npm install && npm run build`
   - **Publish Directory**: `client/dist`

3. **Add Environment Variables:**
   ```
   VITE_API_URL=https://your-backend-url.onrender.com
   ```

4. **Deploy**

### Database Setup

1. **Create a PostgreSQL database** on Render
2. **Copy the Internal Database URL**
3. **Use it in the backend's `DATABASE_URL` environment variable**

---

## Alternative Deployment Options

### Railway

Similar to Render, with good free tier:
1. Connect GitHub repo
2. Deploy backend and frontend as separate services
3. Add PostgreSQL plugin
4. Configure environment variables

### Fly.io

More control, good for Docker:
```bash
# Install Fly CLI
flyctl launch

# Deploy
flyctl deploy
```

### Vercel (Frontend only)

Great for static frontend:
```bash
cd client
vercel --prod
```

Backend would need separate hosting.

---

## Environment Variables Reference

### Backend (.env)

```bash
DATABASE_URL=postgresql://user:password@host:5432/dbname
ENVIRONMENT=production
CORS_ORIGINS=https://your-frontend.com
```

### Frontend

```bash
VITE_API_URL=https://your-backend-api.com
```

---

## Post-Deployment Verification

1. **Check backend health:**
   ```bash
   curl https://your-backend.com/health
   ```

2. **Check API documentation:**
   Visit `https://your-backend.com/docs`

3. **Test frontend:**
   Open `https://your-frontend.com` and test a calculation

4. **Check database:**
   Verify calculations are being saved in history

---

## Monitoring and Logging

### Render

- Built-in logs in the dashboard
- Set up log drains for external services

### Health Checks

Backend includes:
- `/health` endpoint
- `/` root endpoint with API info

### Database Backups

- Render provides automatic daily backups
- Download backups from the dashboard

---

## Troubleshooting

### CORS Errors

Ensure  `CORS_ORIGINS` in backend includes your frontend URL

### Database Connection Issues

- Check `DATABASE_URL` format
- Verify database is accessible from backend service
- Check PostgreSQL version compatibility

### Build Failures

**Frontend:**
- Clear node_modules and reinstall
- Check for TypeScript errors

**Backend:**
- Verify Python version (3.12+)
- Check UV installation
- Verify all dependencies in pyproject.toml

---

## Scaling Considerations

1. **Database**: Use connection pooling for high traffic
2. **Backend**: Scale horizontally (multiple instances)
3. **Frontend**: Use CDN for static assets
4. **Caching**: Add Redis for calculation results

---

## Security Best Practices

1. ✅ Use HTTPS (Render provides this automatically)
2. ✅ Set strong database passwords
3. ✅ Rotate API keys regularly
4. ✅ Enable CORS only for trusted domains
5. ✅ Keep dependencies updated

---

**Deployment Status**: Ready for cloud deployment  
**Estimated Setup Time**: 30-45 minutes  
**Monthly Cost (Free tier)**: $0
