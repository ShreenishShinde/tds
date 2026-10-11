# eShopCo latency endpoint (Vercel)

## Deploy
1. Extract this folder.
2. Push its contents to a GitHub repository.
3. Import that repository at https://vercel.com/new and deploy with the default settings.
4. The POST endpoint is `https://YOUR-PROJECT.vercel.app/api`.

## Test
```bash
curl -X POST 'https://YOUR-PROJECT.vercel.app/api' \
  -H 'Content-Type: application/json' \
  -d '{"regions":["apac","emea"],"threshold_ms":176}'
```

The response contains one object per requested region with `avg_latency`,
`p95_latency`, `avg_uptime`, and `breaches`. Percentiles use linear interpolation
(the common NumPy default). CORS allows any origin for POST/OPTIONS.
