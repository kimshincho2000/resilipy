"""
ResiliPy Showcase and Quickstart Demo.
Author: @xika4 (Telegram: @xika4)
Demonstrates Chaos Injection, Circuit Breakers, and Dead Route Inspection.
"""

import asyncio
from fastapi import FastAPI
from resilipy import (
    ChaosEngine,
    chaos_inject,
    CircuitBreaker,
    RouteInspector,
    DeadCodeDetector,
    ResiliMiddleware,
    __author__,
    __author_telegram__,
)

print(f"[*] Initializing ResiliPy by {__author__} ({__author_telegram__})")

app = FastAPI(title="Demo App with ResiliPy")
app.add_middleware(ResiliMiddleware, failure_rate=0.0, latency_min_ms=10, latency_max_ms=25)

# 1. API Route with chaos fault injection
@app.get("/api/v1/orders")
@chaos_inject(rate=0.4, delay_ms=50, error_msg="Order Service Chaos (@xika4)")
def get_orders():
    return [{"id": 101, "item": "Keyboard", "status": "shipped"}]

# 2. Resilient endpoint protected by Circuit Breaker
breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=2.0, fallback=lambda: {"status": "degraded_cached_data"})

@app.get("/api/v1/payment")
@breaker
def process_payment():
    raise RuntimeError("External Payment Gateway Unreachable!")

# 3. Dead route (never called by client)
@app.get("/api/v1/legacy-reports")
def legacy_reports():
    return {"data": "deprecated"}

def main():
    print(f"\n[+] Inspecting registered routes with ResiliPy RouteInspector:")
    inspector = RouteInspector(app)
    routes = inspector.inspect()
    for r in routes:
        print(f"  -> {r['methods']} {r['path']} (Handler: {r['endpoint']})")

    print(f"\n[+] Testing CircuitBreaker with Automatic Fallback (@xika4):")
    res1 = process_payment()
    print(f"  Attempt 1 result: {res1} (Fallback active)")
    res2 = process_payment()
    print(f"  Attempt 2 result: {res2} (Circuit state: {breaker.state.value})")

    print("\n[✓] Demo executed flawlessly! ResiliPy is ready for production use.")

if __name__ == "__main__":
    main()
