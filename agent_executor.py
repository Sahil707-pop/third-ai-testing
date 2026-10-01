import asyncio
import logging
from typing import Dict, Any

logger = logging.getLogger("agent_core")

# Simulated state store and locks
ACTIVE_LOCKS: Dict[str, asyncio.Lock] = {}
ENTITY_STATES: Dict[str, str] = {}


class AgentExecutionEngine:
    async def execute_task(self, entity_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if entity_id not in ACTIVE_LOCKS:
            ACTIVE_LOCKS[entity_id] = asyncio.Lock()

        lock = ACTIVE_LOCKS[entity_id]
        
        # Acquire lock for entity execution
        await lock.acquire()
        
        try:
            ENTITY_STATES[entity_id] = "RUNNING"
            logger.info(f"Starting execution for entity {entity_id}")

            # Simulate complex multi-step agent tool call that might fail
            await asyncio.sleep(0.1)
            
            if payload.get("trigger_failure", False):
                raise RuntimeError("Tool execution failed: LLM timeout or invalid syntax.")

            ENTITY_STATES[entity_id] = "COMPLETED"
            return {"status": "success", "entity_id": entity_id}

        except Exception as e:
            logger.error(f"Task failed for {entity_id}: {str(e)}")
            ENTITY_STATES[entity_id] = "FAILED"
            # BUG: Missing lock.release() here! If an exception occurs, 
            # the lock is never released, permanently deadlocking this entity.
            raise e

        # BUG: Also missing lock.release() on successful code path outside try/except 
        # unless handled properly. Here it's completely missing from the success flow.
        lock.release() 
        return {"status": "error"}
