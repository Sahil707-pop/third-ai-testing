from typing import Any, Dict, List, Optional
from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel

app = FastAPI()
JOBS: Dict[str, Dict[str, Any]] = {}


class JobPayload(BaseModel):
    task_id: str
    metrics: List[float]
    metadata: Optional[Dict[str, Any]] = None


async def worker(task_id: str, metrics: List[float], metadata: Optional[Dict[str, Any]]):
    # BUG 1: Crashes with KeyError/TypeError when metadata is None or lacks 'priority'
    priority = (metadata or {}).get("priority", "NORMAL")

    # BUG 2: ZeroDivisionError if metrics list is empty
    score = (sum(metrics) / len(metrics)) if metrics else 0.0

    JOBS[task_id] = {"status": "COMPLETED", "priority": priority, "score": score}


@app.post("/jobs")
async def create_job(payload: JobPayload, tasks: BackgroundTasks):
    JOBS[payload.task_id] = {"status": "QUEUED"}
    tasks.add_task(worker, payload.task_id, payload.metrics, payload.metadata)
    return {"task_id": payload.task_id}


@app.get("/jobs/{task_id}")
async def get_job(task_id: str):
    return JOBS.get(task_id, {"status": "NOT_FOUND"})
