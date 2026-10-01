import asyncio
import pytest
from httpx import ASGITransport, AsyncClient
from app import app, JOBS


@pytest.fixture(autouse=True)
def reset_store():
    JOBS.clear()


@pytest.mark.asyncio
async def test_bugs():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Fails BUG 1: None metadata triggers unhandled KeyError in worker
        await ac.post("/jobs", json={"task_id": "t1", "metrics": [1.0, 2.0], "metadata": None})

        # Fails BUG 2: Empty metrics triggers ZeroDivisionError
        await ac.post("/jobs", json={"task_id": "t2", "metrics": [], "metadata": {"priority": "LOW"}})

        await asyncio.sleep(0.1)

        res1 = await ac.get("/jobs/t1")
        assert res1.json()["status"] == "COMPLETED"

        res2 = await ac.get("/jobs/t2")
        assert res2.json()["score"] == 0.0
