from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import products, inventory, branches
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Laxmi Bags House API",
    description="Backend API for Inventory Management System",
    version="1.0.0"
)

# CORS middleware - Allow React frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router)
app.include_router(inventory.router)
app.include_router(branches.router)

@app.get("/")
async def root():
    return {
        "message": "Laxmi Bags House API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)