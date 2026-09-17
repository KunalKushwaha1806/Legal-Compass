# Deploying Legal Compass to Vercel 🚀

This repository is configured to deploy directly to **Vercel** with zero friction.

---

## ⚡ Quick Deployment (Vercel Dashboard)

### Method 1: Connecting via GitHub (Recommended)
1. Push your changes to your GitHub repository:
   ```bash
   git add .
   git commit -m "Configure Vercel deployment"
   git push origin main
   ```
2. Go to [vercel.com](https://vercel.com) and click **"Add New Project"** -> **"Import Git Repository"**.
3. Select your `Legal-Compass` repository.
4. **Project Settings:**
   - **Framework Preset:** Vite
   - **Root Directory:** Keep as `./` (or choose `frontend` — both work seamlessly)
   - **Build Command:** `npm run build`
   - **Output Directory:** `frontend/dist` (if deployed from root) or `dist` (if root directory is `frontend`)
5. **Environment Variables:**
   Under **Environment Variables**, add:
   - `VITE_API_URL`: The URL of your deployed Render API (e.g., `https://legal-compass-api.onrender.com`).
     *(Note: If you are running locally or proxying, it falls back to `/api` automatically).*
6. Click **Deploy**.

For the Render API setup, environment variables, and end-to-end verification,
follow [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md).

---

### Method 2: Deploying via Vercel CLI
If you have the Vercel CLI installed:
```bash
npm install -g vercel
vercel
```
Follow the prompts and select the defaults.

---

## 🛠️ What Was Configured for Vercel
1. **Single-Page Application (SPA) Routing (`vercel.json`):**
   - Configured rewrites (`/(.*) -> /index.html`) so refreshing on `/login`, `/register`, or other client routes will not throw `404: NOT FOUND`.
2. **Dynamic API Configuration (`frontend/src/services/api.js`):**
   - Configured `axios` to read from `import.meta.env.VITE_API_URL` while keeping the local `/api` fallback.
3. **CORS Configuration (`backend_node/server.js`):**
   - Updated backend CORS policy to permit requests originating from all `*.vercel.app` preview and production domains.
4. **Root-Level Monorepo Build Support (`package.json` & root `vercel.json`):**
   - If imported at repository root, Vercel will automatically build the `frontend` workspace without requiring manual folder restructuring.
