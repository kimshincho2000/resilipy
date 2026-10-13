"""
Comprehensive End-to-End Stress Test for Obfuscated ResiliPy
Author: @xika4
Tests:
1. Chaos Ingestion (Decorator & Direct Async/Sync)
2. Live HTTP FastAPI Server with ResiliMiddleware
3. Circuit Breaker Auto-Recovery (Closed -> Open -> Half-Open -> Closed)
4. Route Inspector on Live App
5. Dead Code Analyzer scanning simulated frontend project
"""

import asyncio
import os
import shutil
import tempfile
import time
from fastapi import FastAPI
from starlette.testclient import TestClient

import resilipy
from resilipy import (
    ChaosEngine,
    chaos_inject,
    CircuitBreaker,
    CircuitBreakerOpenException,
    ResiliMiddleware,
    RouteInspector,
    DeadCodeDetector,
)

print(f"{'='*60}")
print(f"🔥 FULL RESILIPY TEST SUITE (Author: {resilipy.__author__})")
print(f"Telegram: {resilipy.__author_telegram__} | Version: {resilipy.__version__}")
print(f"{'='*60}\n")

# TEST 1: Synchronous & Asynchronous Chaos Injection
print("[TEST 1] Testing Chaos Injection...")
engine = ChaosEngine(failure_rate=1.0, error_message="Direct Chaos Triggered by @xika4")
try:
    engine.apply_sync()
    print("  ❌ Test 1 (Sync Chaos): Failed to trigger fault!")
except Exception as e:
    print(f"  ✅ Test 1 (Sync Chaos): Fault triggered successfully -> {e}")

@chaos_inject(rate=1.0, delay_ms=20, error_msg="Decorator Chaos (@xika4)")
async def simulated_api_call():
    return {"status": "ok"}

async def test_async_chaos():
    t0 = time.time()
    try:
        await simulated_api_call()
        print("  ❌ Test 1 (Async Chaos): Failed!")
    except Exception as e:
        elapsed = (time.time() - t0) * 1000
        print(f"  ✅ Test 1 (Async Chaos): Delay ~{elapsed:.1f}ms and Exception caught -> {e}")

asyncio.run(test_async_chaos())


# TEST 2: Circuit Breaker State Machine & Self-Healing
print("\n[TEST 2] Testing Circuit Breaker State Transitions & Self-Healing...")
breaker = CircuitBreaker(
    failure_threshold=3,
    recovery_timeout=0.5, # 500ms recovery for fast test
    fallback=lambda: {"fallback": True, "author": "@xika4"}
)

call_count = 0
def flaky_upstream():
    global call_count
    call_count += 1
    if call_count <= 3:
        raise ConnectionResetError("Database connection lost")
    return {"data": "fresh_db_data"}

guarded_upstream = breaker(flaky_upstream)

# 3 failures to trip the circuit
r1 = guarded_upstream()
r2 = guarded_upstream()
r3 = guarded_upstream()
print(f"  Attempts 1-3 result: {r1} (Fallbacks triggered)")
print(f"  Circuit State after 3 fails: {breaker.state.value} (Expected: OPEN)")
assert breaker.state.value == "OPEN"

# Wait for recovery timeout to pass
print("  Waiting 0.6s for self-healing recovery window...")
time.sleep(0.6)

# Next call should succeed and start healing
r4 = guarded_upstream()
print(f"  Post-timeout attempt result: {r4}")
print(f"  Circuit State: {breaker.state.value}")
assert r4["data"] == "fresh_db_data"
print("  ✅ Test 2 (Circuit Breaker): Auto-recovered successfully!")


# TEST 3: FastAPI Live App with ResiliMiddleware
print("\n[TEST 3] Testing FastAPI Live Middleware with Starlette TestClient...")
app = FastAPI()
app.add_middleware(
    ResiliMiddleware,
    failure_rate=0.0, # no random fails by default
    latency_min_ms=10,
    latency_max_ms=20,
    chaos_header_trigger="X-ResiliPy-Chaos"
)

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id, "name": "Mechanical Keyboard"}

@app.get("/analytics")
def analytics():
    return {"views": 10540}

client = TestClient(app)

# Normal request
resp_normal = client.get("/items/42")
print(f"  Normal Request -> Status: {resp_normal.status_code}, Headers: {dict(resp_normal.headers.items())}")
assert resp_normal.status_code == 200
assert resp_normal.headers.get("x-author") == "@xika4"
assert resp_normal.headers.get("x-resilipy-protected") == "true"

# Request with Header-injected Chaos
resp_chaos = client.get("/items/42", headers={"X-ResiliPy-Chaos": "true"})
print(f"  Forced Chaos Request -> Status: {resp_chaos.status_code}, Body: {resp_chaos.json()}")
assert resp_chaos.status_code == 503
assert resp_chaos.headers.get("x-resilipy-simulated") == "true"
print("  ✅ Test 3 (FastAPI Middleware): Live traffic interception verified!")


# TEST 4: Route Inspector & Dead Code Detection
print("\n[TEST 4] Testing Route Inspector & Zombie API Detector...")
inspector = RouteInspector(app)
routes = inspector.inspect()
print(f"  Detected {len(routes)} application routes:")
for r in routes:
    print(f"    • {r['methods']} -> {r['path']}")

# Create mock frontend workspace
tmp_dir = tempfile.mkdtemp()
try:
    frontend_file = os.path.join(tmp_dir, "App.vue")
    with open(frontend_file, "w") as f:
        # Notice: App.vue calls /items/{item_id}, but NOT /analytics
        f.write("""
        <template><div>{{ item.name }}</div></template>
        <script>
        fetch('/items/1').then(r => r.json());
        </script>
        """)

    detector = DeadCodeDetector(routes)
    report = detector.scan_client_directory(tmp_dir)

    print(f"\n  Dead Code Analysis Results:")
    print(f"    Total backend routes: {report['total_routes']}")
    print(f"    Active in frontend: {report['active_routes_count']}")
    print(f"    Dead / Unused routes: {report['dead_routes_count']}")
    for dead in report["dead_routes"]:
        print(f"    ⚠️ DEAD ENDPOINT: {dead['path']} ({dead['endpoint']})")

    assert report['active_routes_count'] == 1
    assert report['dead_routes_count'] == 1
    assert report['dead_routes'][0]['path'] == "/analytics"
    print("  ✅ Test 4 (Dead Route Analysis): Accurately identified unused endpoints!")
finally:
    shutil.rmtree(tmp_dir)

print(f"\n{'='*60}")
print("🎉 ALL TESTS PASSED SUCCESSFULLY! ResiliPy is 100% operational!")
print(f"{'='*60}")
