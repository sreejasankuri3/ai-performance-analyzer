from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uuid
import time
import random
from datetime import datetime
import asyncio

app = FastAPI(title="AI Performance Analyzer", version="1.0.0")

# CORS middleware - allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory database
jobs_db = []

class JobCreate(BaseModel):
    model_name: str
    batch_size: int = 32

class Job(JobCreate):
    id: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    average_latency: Optional[float] = None
    throughput: Optional[float] = None
    memory_usage: Optional[float] = None
    accuracy: Optional[float] = None

async def simulate_ai_processing(job_id: str, model_name: str):
    """Simulate AI model processing"""
    await asyncio.sleep(2)  # Simulate processing time
    
    # Generate realistic performance metrics based on model name
    if "large" in model_name.lower():
        latency = random.uniform(50, 100)
        throughput = random.uniform(10, 20)
        memory = random.uniform(400, 800)
        accuracy = random.uniform(0.85, 0.95)
    elif "medium" in model_name.lower():
        latency = random.uniform(20, 50)
        throughput = random.uniform(20, 40)
        memory = random.uniform(200, 400)
        accuracy = random.uniform(0.75, 0.85)
    else:
        latency = random.uniform(5, 20)
        throughput = random.uniform(40, 80)
        memory = random.uniform(50, 200)
        accuracy = random.uniform(0.65, 0.75)
    
    return {
        "average_latency": latency,
        "throughput": throughput,
        "memory_usage": memory,
        "accuracy": accuracy
    }

@app.post("/jobs/", response_model=Job)
async def create_job(job: JobCreate):
    """Create a new performance analysis job"""
    job_id = str(uuid.uuid4())
    new_job = Job(
        model_name=job.model_name,
        batch_size=job.batch_size,
        id=job_id,
        status="running",
        created_at=datetime.utcnow()
    )
    jobs_db.append(new_job)
    
    # Start background processing
    asyncio.create_task(process_job(job_id, job.model_name))
    
    return new_job

async def process_job(job_id: str, model_name: str):
    """Process job in background"""
    try:
        # Simulate AI processing
        metrics = await simulate_ai_processing(job_id, model_name)
        
        # Update job with results
        for job in jobs_db:
            if job.id == job_id:
                job.status = "completed"
                job.completed_at = datetime.utcnow()
                job.average_latency = metrics["average_latency"]
                job.throughput = metrics["throughput"]
                job.memory_usage = metrics["memory_usage"]
                job.accuracy = metrics["accuracy"]
                break
                
    except Exception as e:
        # Mark job as failed
        for job in jobs_db:
            if job.id == job_id:
                job.status = "failed"
                break

@app.get("/jobs/", response_model=List[Job])
def read_jobs():
    """Get all jobs"""
    return jobs_db

@app.get("/jobs/{job_id}", response_model=Job)
def read_job(job_id: str):
    """Get a specific job by ID"""
    for job in jobs_db:
        if job.id == job_id:
            return job
    raise HTTPException(status_code=404, detail="Job not found")

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": time.time(), "total_jobs": len(jobs_db)}

@app.get("/")
def read_root():
    return {"message": "AI Performance Analyzer API is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)