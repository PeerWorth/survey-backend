from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.asset.v1.router import asset_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(asset_router, prefix="/api/asset", tags=["asset"])


@app.get("/health")
async def health():
    return {"status": "ok"}
