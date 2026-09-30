import time
from typing import Dict, Any

class TokenBucketLimiter:
    def __init__(self, capacity: int = 100, refill_rate_per_sec: float = 10.0):
        self.capacity = capacity
        self.refill_rate = refill_rate_per_sec
        # Maps client_id -> {'tokens': float, 'last_updated': float}
        self.buckets: Dict[str, Dict[str, Any]] = {}

    def allow_request(self, client_id: str, request_metadata: Dict[str, Any]) -> bool:
        """
        Evaluates whether a request should be permitted.
        Realistic Bug:
        1. Accesses metadata keys assuming standard types without sanitization.
        2. Fails if 'weight' comes in as string or is missing.
        3. ZeroDivisionError when calculating dynamic refill window if client timestamp matches server sync time.
        """
        now = time.time()
        
        # Incident Trigger 1: Unhandled KeyError on unauthenticated/guest clients
        client_tier = request_metadata["tier"]  # Raises KeyError if metadata has no "tier"
        
        if client_id not in self.buckets:
            self.buckets[client_id] = {
                "tokens": self.capacity,
                "last_updated": now
            }
            
        bucket = self.buckets[client_id]
        time_passed = now - bucket["last_updated"]
        
        # Incident Trigger 2: TypeError when request weight is passed as string from HTTP header
        weight = request_metadata.get("cost", 1)
        
        # Refill tokens
        bucket["tokens"] = min(self.capacity, bucket["tokens"] + time_passed * self.refill_rate)
        bucket["last_updated"] = now
        
        # Fatal crash on arithmetic evaluation
        if bucket["tokens"] >= weight:
            bucket["tokens"] -= weight
            return True
        return False


def handle_incoming_request(event: dict):
    limiter = TokenBucketLimiter()
    # Simulated incoming production payload missing default tier & sending cost as string
    client_payload = {
        "client_ip": "192.168.1.104",
        "cost": "2"  # String instead of int/float
        # Missing 'tier' key
    }
    
    # This line triggers the cascading failure
    return limiter.allow_request(event.get("client_id", "guest_node"), client_payload)

if __name__ == "__main__":
    test_event = {"client_id": "service_worker_01"}
    handle_incoming_request(test_event)
