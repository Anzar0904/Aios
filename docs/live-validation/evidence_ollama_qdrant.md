# Ollama & Qdrant — Live Validation Evidence
**Date:** 2026-07-13T20:01:54+05:30

---

## Ollama

### Discovery

| Item | Value |
|------|-------|
| Binary | `/usr/local/bin/ollama` ✅ |
| Version | Detected (binary present) |
| `OLLAMA_MODELS` env | `/Volumes/AI_MODELS/models` |
| Models volume mounted | ❌ `/Volumes/AI_MODELS/models` does not exist |
| Daemon on `localhost:11434` | ❌ Connection refused |
| `ollama list` output | Empty (no models loaded) |

### Commands Executed

```bash
GET http://localhost:11434/api/tags  # → ConnectError: [Errno 61] Connection refused
GET http://127.0.0.1:11434/api/tags # → ConnectError: [Errno 61] Connection refused
which ollama                         # → /usr/local/bin/ollama
ollama list                          # → NAME  ID  SIZE  MODIFIED (empty)
```

### Code Assessment

- ✅ `NineRouterProvider` at `core/src/aios/providers/ninerouter.py` — implemented
- ✅ `test_ninerouter.py` — all tests PASS
- ✅ Ollama is installed but daemon is stopped
- ❌ No models are downloaded (external volume not mounted)
- ❌ Live inference: **BLOCKED** — daemon not running, no models

**VERDICT: SKIP — ENVIRONMENTAL BLOCKER (Ollama daemon not started, no models loaded)**

### To activate
```bash
ollama serve &     # Start daemon
ollama pull qwen2.5-coder  # Download a model
```

---

## Qdrant

### Discovery

| Item | Value |
|------|-------|
| Binary | `./qdrant/qdrant` — version 1.18.2 ✅ |
| Config | `./qdrant/config/production.yaml` ✅ |
| Storage | `./qdrant/storage/` ✅ |
| `.qdrant-initialized` | Present (empty file) |
| Daemon on `localhost:6333` | ❌ Connection refused |
| Daemon on `localhost:6334` | ❌ Connection refused |

### Commands Executed

```bash
GET http://localhost:6333/health  # → ConnectError: [Errno 61] Connection refused
GET http://localhost:6334/health  # → ConnectError: [Errno 61] Connection refused
./qdrant/qdrant --version         # → qdrant 1.18.2
```

### Platform Tests (in-memory mode)

`core/tests/test_qdrant_platform.py` — **48 tests PASS** using `qdrant_client` in local/in-memory mode.

`core/tests/test_qdrant_production_validation.py` — **1 test FAIL** — explicitly requires live Qdrant server:
```
RuntimeError: Qdrant live server is unreachable on 127.0.0.1:6333. Production validation aborted.
```

### Code Assessment

- ✅ Qdrant client integration fully implemented
- ✅ Graceful fallback to in-memory mode (48/48 platform tests pass)
- ✅ All Qdrant semantic memory integration tests PASS
- ❌ Live server: daemon not started

### To activate
```bash
cd qdrant && ./qdrant  # Start Qdrant server
```

**VERDICT: ⚠️ PARTIAL — In-memory mode PASS (48 tests), live server daemon not started (environmental)**
