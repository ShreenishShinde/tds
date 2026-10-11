from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    if request.method == "OPTIONS":
        response = JSONResponse(content={})
    else:
        response = await call_next(request)

    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

@app.post("/")
@app.post("/api/latency")
@app.post("/latency")
async def latency_metrics(request: Request):
    # Keep your existing metrics calculation here.
    ...
