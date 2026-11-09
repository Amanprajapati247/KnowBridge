# KnowBridge Production Deployment Guide

This guide walks you through deploying **KnowBridge** to live cloud infrastructure.

Because KnowBridge packages the React Vite frontend and FastAPI backend into a unified architecture, you can deploy the **entire application on a single cloud service** with zero CORS complexity, or deploy the frontend and backend separately.

---

## Option 1: 1-Click Deployment on Render (Recommended & Free)

Render provides a free tier and supports automatic Docker builds directly from your GitHub repository.

### Steps:
1. Go to [https://render.com](https://render.com) and log in with your GitHub account.
2. In the Render Dashboard, click **New +** and select **Blueprint** (or **Web Service**).
3. Connect your repository: `https://github.com/Amanprajapati247/KnowBridge`.
4. Render will automatically detect `render.yaml` and `Dockerfile`.
5. Click **Apply** or **Create Web Service**.
6. Render builds the React frontend, sets up Python 3.12, and launches the server.
7. Once finished, you will receive a free public URL (e.g. `https://knowbridge.onrender.com`).

---

## Option 2: Deployment on Railway

Railway offers fast, zero-configuration Docker container deployment.

### Steps:
1. Go to [https://railway.app](https://railway.app) and sign in with GitHub.
2. Click **New Project** $\rightarrow$ **Deploy from GitHub repo**.
3. Select `Amanprajapati247/KnowBridge`.
4. Railway will detect the `Dockerfile` in the root directory and start the build automatically.
5. In your project settings on Railway:
   - Go to **Settings** $\rightarrow$ **Networking** $\rightarrow$ click **Generate Domain**.
6. Your platform is instantly live on your custom `*.up.railway.app` URL!

---

## Option 3: Separate Frontend on Vercel + Backend on Render

If you prefer hosting the React frontend on Vercel's global CDN:

### Part A: Deploy Backend on Render
1. In Render, select **New +** $\rightarrow$ **Web Service**.
2. Connect `Amanprajapati247/KnowBridge`.
3. Set:
   - **Root Directory:** `backend`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Note your backend URL (e.g. `https://knowbridge-api.onrender.com`).

### Part B: Deploy Frontend on Vercel
1. Go to [https://vercel.com](https://vercel.com) $\rightarrow$ **Add New Project**.
2. Import `Amanprajapati247/KnowBridge`.
3. Set **Root Directory** to `frontend`.
4. Update `frontend/vercel.json` with your live Render backend URL:
   ```json
   {
     "rewrites": [
       {
         "source": "/api/(.*)",
         "destination": "https://your-backend-api.onrender.com/api/$1"
       },
       {
         "source": "/(.*)",
         "destination": "/index.html"
       }
     ]
   }
   ```
5. Click **Deploy**. Vercel will build and serve your frontend globally.

---

## Option 4: Local or VPS Deployment with Docker

To run the complete platform inside a standalone Docker container on any Linux/macOS/Windows server:

```bash
# Clone the repository
git clone https://github.com/Amanprajapati247/KnowBridge.git
cd KnowBridge

# Build and run with Docker Compose
docker compose up -d --build
```

Access the application at `http://localhost:8000`.
The single container automatically serves both the React client and the FastAPI REST endpoints.
