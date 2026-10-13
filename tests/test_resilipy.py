"""
ResiliPy Test Suite
Verifies Chaos injection, Circuit Breaker states, Route Inspector, and Middleware.
Author: @xika4
"""

import asyncio
import unittest
from resilipy import ChaosEngine, chaos_inject, CircuitBreaker, CircuitBreakerOpenException, RouteInspector
from fastapi import FastAPI


class TestResiliPy(unittest.TestCase):
    def test_author_metadata(self):
        import resilipy
        self.assertEqual(resilipy.__author__, "@xika4")
        self.assertEqual(resilipy.__author_telegram__, "https://t.me/xika4")

    def test_chaos_engine_sync(self):
        engine = ChaosEngine(failure_rate=1.0, enabled=True)
        with self.assertRaises(Exception):
            engine.apply_sync()

    def test_circuit_breaker(self):
        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1, fallback=lambda: "fallback_val")

        @breaker
        def faulty():
            raise RuntimeError("Internal fault")

        # First failure -> fallback triggered
        res1 = faulty()
        self.assertEqual(res1, "fallback_val")

        # Second failure -> opens circuit
        res2 = faulty()
        self.assertEqual(res2, "fallback_val")
        self.assertEqual(breaker.state.value, "OPEN")

    def test_route_inspector(self):
        app = FastAPI()

        @app.get("/api/v1/users")
        def get_users():
            """Returns users list"""
            return [{"id": 1}]

        inspector = RouteInspector(app)
        routes = inspector.inspect()
        paths = [r["path"] for r in routes]
        self.assertIn("/api/v1/users", paths)


if __name__ == "__main__":
    unittest.main()
