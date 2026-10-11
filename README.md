# Fixed Vercel FastAPI project

This version uses the root `app.py` entrypoint supported by Vercel's FastAPI integration.

1. Replace the files in your GitHub repository with these files (or import this as a new repository).
2. Redeploy on Vercel.
3. Since this is a root FastAPI app with `@app.post("/")`, use the POST endpoint:
   `https://YOUR-PROJECT.vercel.app/`

Test:
```bash
curl -X POST 'https://YOUR-PROJECT.vercel.app/' \
  -H 'Content-Type: application/json' \
  -d '{"regions":["apac","emea"],"threshold_ms":176}'
```
