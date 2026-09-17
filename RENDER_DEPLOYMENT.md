# Deploy the API to Render

This project deploys the React application to Vercel and the Express API in
`backend_node/` to Render. The API stores user accounts and chat history in
PostgreSQL, so do not rely on the local SQLite or JSON fallbacks in production.

## 1. Push the deployment configuration

Commit and push `render.yaml` together with the backend code. Render reads this
file from the repository root and uses `backend_node` as the service root.

## 2. Create the database

In Render, create a **Postgres** database in the same region as the web service.
Copy its **Internal Database URL**. The API creates its `users` and `chats`
tables automatically on startup.

You can use an existing Neon PostgreSQL database instead; use its connection
string as `DATABASE_URL`.

## 3. Create the API web service

1. In Render, choose **New** > **Blueprint** and select this repository.
2. Confirm the service named `legal-compass-api`. The blueprint supplies:
   - Root directory: `backend_node`
   - Build command: `npm ci`
   - Start command: `npm start`
   - Health check: `/health`
3. Supply the values Render marks as required:

| Variable | Value |
| --- | --- |
| `DATABASE_URL` | Render Postgres Internal Database URL (or your Neon URL) |
| `FRONTEND_URL` | Your Vercel production URL, such as `https://legal-compass.vercel.app` |
| `PYTHON_API_URL` | Public URL for the Python FastAPI service that answers chat requests |

Render securely generates `JWT_SECRET`. Keep it unchanged after users begin
using the service, otherwise existing sessions become invalid. The Render Node
service does not install the Python model dependencies, so set `PYTHON_API_URL`
to a deployed FastAPI engine for live chat answers.

After the deploy succeeds, open `https://<your-render-service>.onrender.com/health`.
It must return JSON with `"status": "ok"`.

## 4. Point Vercel at Render

In the Vercel project settings, add this production environment variable, then
redeploy the frontend:

| Variable | Value |
| --- | --- |
| `VITE_API_URL` | `https://<your-render-service>.onrender.com` |

Do not append `/api`; the frontend accepts either form, but the base URL above
is the clearest value. Its API client adds `/api` automatically.

## 5. Verify the complete flow

1. Visit the Vercel deployment in an incognito window.
2. Register a new account and sign in.
3. Send a chat message and refresh the page to confirm that the saved history
   remains available.

Vercel preview deployments are permitted automatically. For a custom Vercel
domain, add it to `FRONTEND_URL`; multiple custom origins can be comma-separated.
