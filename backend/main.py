import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.routers import auth, assessment, market_demand, skill_gap, curriculum, credentials, adaptive, job_readiness

app = FastAPI(
    title="MICRO-CREDENTIAL CURRICULUM GENERATION PLATFORM DRIVEN BY REAL-TIME GLOBAL JOB MARKET SKILL DEMANDS",
    description="Driven by Real-Time Global Job Market Skill Demands",
    version="1.0.0"
)

# Enable CORS for development & cross-origin frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(assessment.router)
app.include_router(market_demand.router)
app.include_router(skill_gap.router)
app.include_router(curriculum.router)
app.include_router(credentials.router)
app.include_router(adaptive.router)
app.include_router(job_readiness.router)

# Mount frontend static directory
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
def serve_index():
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Micro-Credential Curriculum Generation API is running.", "docs": "/docs"}

@app.get("/api/health")
def health_check():
    return {"status": "online", "platform": "Micro-Credential Curriculum Engine", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
