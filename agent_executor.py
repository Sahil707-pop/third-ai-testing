import asyncio
import logging
from typing import Dict, Any

logger = logging.getLogger("agent_core")

# Simulated state store and locks
ACTIVE_LOCKS: Dict[str, asyncio.Lock] = {}
ENTITY_STATES: Dict[str, str] = {}

class AgentExecutionEngine:
    async def execute_task(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Ensure 'user_id' is present and truthy
        if "user_id" not in payload:
            raise KeyError("'user_id' must be provided in payload")
        user_id = payload["user_id"]
        if not user_id:
            raise KeyError("'user_id' must be a non‑empty value")

        # Obtain or create lock for the user
        if user_id not in ACTIVE_LOCKS:
            ACTIVE_LOCKS[user_id] = asyncio.Lock()
        lock = ACTIVE_LOCKS[user_id]

        # Acquire lock for entity execution
        await lock.acquire()
        try:
            ENTITY_STATES[user_id] = "RUNNING"
            logger.info(f"Starting execution for user {user_id}")

            # Simulate complex multi-step agent tool call that might fail
            await asyncio.sleep(0.1)

            if payload.get("trigger_failure", False):
                raise RuntimeError("Tool execution failed: LLM timeout or invalid syntax.")

            ENTITY_STATES[user_id] = "COMPLETED"
            return {"status": "success", "user_id": user_id}

        except Exception as e:
            logger.error(f"Task failed for {user_id}: {str(e)}")
            ENTITY_STATES[user_id] = "FAILED"
            raise e
        finally:
            # Release the lock only if it was acquired
            lock.release()
