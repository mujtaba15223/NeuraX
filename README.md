## Deployment

### Frontend on Vercel

1. Import this repository into Vercel.
2. Set the project root to `frontend`.
3. Vercel detects the Vite build automatically. The build command is `npm run build` and the output directory is `dist`.
4. Add an environment variable named `VITE_API_URL` containing the public URL of the deployed FastAPI backend, for example `https://your-api.example.com`.

The React SPA fallback is configured in `frontend/vercel.json`, so refreshing routes such as `/inspection` works correctly.

### Backend

Deploy the FastAPI backend on Render using the included `render.yaml`, or on another Python host that supports PyTorch. Start it with:

```text
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

Set `FRONTEND_ORIGIN` to the deployed Vercel URL, then use that backend URL as the frontend `VITE_API_URL` value.

The connection is:

```text
Vercel React frontend --VITE_API_URL--> Render FastAPI backend
									  --loads--> ai/vision and data/raw
```

Vercel cannot reliably host this backend as a frontend deployment because the inspection service loads PyTorch and the local vision dataset. The repository root still contains both services, with Vercel and Render deploying their respective folders from the same repository.
