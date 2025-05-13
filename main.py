from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.asset.v1.router import asset_router
from app.api.auth.v1.router import auth_router
from app.common.middleware.logger import LoggingMiddleware

app = FastAPI()

app.add_middleware(LoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(asset_router, prefix="/api/asset", tags=["asset"])
app.include_router(auth_router, prefix="/api/user", tags=["user"])


@app.get("/health")
async def health():
    return {"status": "ok"}
