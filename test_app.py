from fastapi import FastAPI, Request

app = FastAPI()
JOBS = {}

@app.post("/jobs")
async def create_job(request: Request):
    data = await request.json()
    task_id = data.get("task_id")
    metrics = data.get("metrics", [])
    metadata = data.get("metadata") or {}
    JOBS[task_id] = {"metrics": metrics, "metadata": metadata}
    return {"task_id": task_id}

@app.get("/jobs/{task_id}")
async def get_job(task_id: str):
    job = JOBS.get(task_id)
    if not job:
        return {"status": "FAILED"}
    job["status"] = "COMPLETED"
    if job["metrics"]:
        job["score"] = sum(job["metrics"]) / len(job["metrics"])
    else:
        job["score"] = 0.0
    return {"status": job["status"], "score": job["score"]}