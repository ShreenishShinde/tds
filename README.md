# TDS Vercel latency endpoint

This project follows the assignment's required structure:
- `api/index.py`
- `requirements.txt` containing `fastapi`
- root `vercel.json` using `@vercel/python` and a catch-all route
- bundled telemetry JSON

## Deploy
Replace the files in the GitHub repository connected to Vercel with these files and push to `main`, or import this folder as a new repository. Wait for the production deployment to complete.

## Endpoint
The assignment's catch-all route forwards incoming paths to `api/index.py`. Test the submitted URL:
`https://YOUR-PROJECT.vercel.app/api/latency`

```bash
curl -i -X POST 'https://YOUR-PROJECT.vercel.app/api/latency' \
  -H 'Content-Type: application/json' \
  -d '{"regions":["apac","emea"],"threshold_ms":176}'
```
