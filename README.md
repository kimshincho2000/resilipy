# ResiliPy 🛡️⚡

[![Python Versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)
[![License: Proprietary](https://img.shields.io/badge/License-Protected%20by%20@xika4-red.svg)](https://t.me/xika4)
[![Author](https://img.shields.io/badge/Author-@xika4-blueviolet.svg)](https://t.me/xika4)
[![Telegram](https://img.shields.io/badge/Telegram-@xika4-0088cc.svg)](https://t.me/xika4)

**ResiliPy** is a next-generation Python Enterprise Resilience, Fault-Injection (Chaos Engineering), and Dead Route Analysis framework designed for modern FastAPI and Starlette microservices.

Created and engineered by **[@xika4](https://t.me/xika4)**.

---

## 🔒 Code Security & Protection Notice / Shifrlanganlik haqida

> [!NOTE]
> Ushbu kutubxonaning ichki yadrosi va biznes mantiqi nusxalash va ruxsatsiz o'zgartirishlardan himoyalangan (PyArmor runtime encrypted). Kod faqat ishga tushirilganda xotirada xavfsiz holda bajariladi va to'liq quvvatda ishlaydi.
> 
> Barcha mualliflik huquqlari va intellektual mulk **@xika4** ga tegishli.

---

## ✨ Features / Imkoniyatlar

1. ⚡ **Chaos Fault Injection (`@chaos_inject`, `ChaosEngine`)**:
   - Random HTTP status failures (500, 503, 429).
   - Jitter and latency simulation (ms delay ranges).
   - Zero-overhead async & sync wrapper decorators.
2. 🛡️ **Self-Healing Circuit Breaker (`CircuitBreaker`)**:
   - Closed ➔ Open ➔ Half-Open self-healing state transitions.
   - Configurable failure threshold & automatic fallback responses.
3. 🌐 **High-Performance ASGI Middleware (`ResiliMiddleware`)**:
   - Global network latency injection for FastAPI / Starlette applications.
   - Header-triggered chaos injection (`X-ResiliPy-Chaos: true`).
4. 🔍 **API Route Inspector & Dead Code Detector (`RouteInspector`, `DeadCodeDetector`)**:
   - Auto-discovers all registered endpoints, parameters, and HTTP verbs.
   - Cross-analyzes server routes with client repositories (Vue, React, Swift, Kotlin, Dart) to flag unused/dead API routes.

---

## 📦 Quick Installation / O'rnatish

```bash
git clone https://github.com/kimshincho2000/resilipy.git
cd resilipy
pip install -r requirements.txt
```

---

## 🚀 Quickstart Example / Misol

```python
from fastapi import FastAPI
from resilipy import chaos_inject, CircuitBreaker, ResiliMiddleware, RouteInspector

app = FastAPI(title="Resilient Microservice")

# 1. Attach Global ResiliPy Middleware
app.add_middleware(ResiliMiddleware, failure_rate=0.05, latency_min_ms=10, latency_max_ms=50)

# 2. Resilient endpoint with automatic fallback
breaker = CircuitBreaker(failure_threshold=3, fallback=lambda: {"message": "Service degraded, cached result"})

@app.get("/api/v1/billing")
@breaker
def billing():
    # If external gateway fails, fallback is safely returned
    raise RuntimeError("Payment gateway timeout")

# 3. Chaos simulation for stress testing
@app.get("/api/v1/orders")
@chaos_inject(rate=0.2, delay_ms=100)
def orders():
    return [{"order_id": 1001, "status": "shipped"}]
```

Run demo:
```bash
PYTHONPATH=obfuscated python3 examples/demo.py
```

---

## 👨‍💻 Author & Contacts / Muallif

- **Author**: @xika4
- **Telegram**: [@xika4](https://t.me/xika4)
- **GitHub**: [kimshincho2000](https://github.com/kimshincho2000)

Copyright (c) 2026 @xika4. All rights reserved.
