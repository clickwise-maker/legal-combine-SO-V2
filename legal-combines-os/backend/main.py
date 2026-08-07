from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import auth_routes, payment_routes, marketplace_routes

app = FastAPI(
    title="Legal Combines OS API",
    description="AI-powered legal compliance platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(payment_routes.router)
app.include_router(marketplace_routes.router)


@app.get("/")
async def root():
    return {"message": "Legal Combines OS API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
