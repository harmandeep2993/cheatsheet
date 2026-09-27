# 14 - pytest

Quick reference for testing Python code with pytest: writing tests, fixtures, parametrising, mocking APIs and LLM calls, testing FastAPI, and coverage.

## Introduction

### What is testing and what is pytest?

A **test** is a small piece of code that runs your code and checks the result is what you expect. **pytest** is the most popular Python testing tool: you write plain functions starting with `test_` that use `assert`, and pytest finds them, runs them and reports which passed or failed with a clear explanation.

### Mental model

Tests are a **safety net** under your code. Every test follows three steps, often called **Arrange - Act - Assert**:

```text
Arrange  -> prepare inputs and fake dependencies    df = make_sample_df()
Act      -> call the thing you are testing          result = clean(df)
Assert   -> check the outcome                       assert result["age"].isna().sum() == 0
```

The **test pyramid** tells you how many of each kind to write:

```text
            /\         end-to-end tests (few, slow): full app + real services
           /  \
          /----\       integration tests (some): API endpoint + database
         /      \
        /--------\     unit tests (many, fast): one function, fake dependencies
```

For AI apps, deterministic tests check your **code** (parsing, tool routing, prompts built correctly) with the LLM **mocked**; **evals** check the **model's behaviour** (see [34 - Evals and Observability](34_evals-observability.md)).

### Why use it?

- **Change code without fear**: tests tell you instantly if you broke something.
- **Faster debugging**: a failing test points to the exact function and input.
- **Living documentation**: tests show how code is meant to be used.
- **Required in teams and CI**: pull requests run tests automatically ([43 - GitHub Actions](43_github-actions.md)).

### Key terms

| Term | Meaning |
|---|---|
| Test function | `def test_something():` with `assert` statements |
| Assertion | A check that must be true |
| Fixture | Reusable setup (data, client, temp folder) injected by name |
| Parametrize | Run the same test with many inputs |
| Mock / fake / stub | A stand-in for a real dependency (API, database, LLM) |
| Monkeypatch | Temporarily replace an attribute or env var during a test |
| Coverage | Share of code lines executed by tests |
| Regression test | Test that reproduces a fixed bug so it never returns |
| Flaky test | Sometimes passes, sometimes fails (timing, randomness, network) |

**Where it fits:** tests code from [09 - Python Basics](09_python-basics.md) to [39 - FastAPI](39_fastapi.md); runs in CI via [43 - GitHub Actions](43_github-actions.md); LLM quality is measured with [34 - Evals](34_evals-observability.md).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| pytest documentation | https://docs.pytest.org/ |
| unittest.mock | https://docs.python.org/3/library/unittest.mock.html |
| pytest-asyncio | https://pytest-asyncio.readthedocs.io/ |
| pytest-cov | https://pytest-cov.readthedocs.io/ |

---

## Contents

0. [Flags and Parameters](#0-flags-and-parameters)
1. [Install and First Test](#1-install-and-first-test)
2. [Project Layout and Discovery](#2-project-layout-and-discovery)
3. [Assertions](#3-assertions)
4. [Testing Exceptions and Warnings](#4-testing-exceptions-and-warnings)
5. [Fixtures](#5-fixtures)
6. [Fixture Scope and conftest.py](#6-fixture-scope-and-conftestpy)
7. [Built-in Fixtures](#7-built-in-fixtures)
8. [Parametrize](#8-parametrize)
9. [Markers (skip, xfail, custom)](#9-markers-skip-xfail-custom)
10. [Mocking with unittest.mock](#10-mocking-with-unittestmock)
11. [Mocking LLM Calls](#11-mocking-llm-calls)
12. [Mocking HTTP Requests](#12-mocking-http-requests)
13. [Testing pandas Code](#13-testing-pandas-code)
14. [Testing FastAPI](#14-testing-fastapi)
15. [Async Tests](#15-async-tests)
16. [Coverage](#16-coverage)
17. [Configuration (pyproject.toml)](#17-configuration-pyprojecttoml)
18. [Good Testing Habits](#18-good-testing-habits)
19. [Troubleshooting](#19-troubleshooting)

---

## 0. Flags and Parameters

> - **What:** The pytest command-line options you use every day.
> - **How:** `pytest [options] [paths or node ids]`.
> - **When to use:** You see `pytest -x -k "login and not slow" -vv tests/` and want to know what each part does.

```text
pytest  -x  -k "login and not slow"  -vv  tests/test_auth.py::test_login_ok
|       |   |                        |    |
|       |   |                        |    +-- node id: one file, one test
|       |   |                        +------- very verbose: full diffs
|       |   +-------------------------------- only tests whose name matches the expression
|       +------------------------------------ stop at the first failure
+-------------------------------------------- test runner
```

| Flag | Meaning |
|---|---|
| `-q` / `-v` / `-vv` | Quiet / verbose / very verbose |
| `-x` | Stop after the first failure |
| `--maxfail=3` | Stop after 3 failures |
| `-k "expr"` | Run tests whose names match (`and`, `or`, `not`) |
| `-m slow` | Run tests with a marker (`-m "not slow"` to skip them) |
| `--lf` | Re-run only the tests that failed last time |
| `--ff` | Run failed tests first, then the rest |
| `-s` | Show `print()` output (disable capture) |
| `--pdb` | Open the debugger at the failure |
| `-l` | Show local variables in tracebacks |
| `--durations=10` | Show the 10 slowest tests |
| `-n auto` | Run in parallel on all cores (plugin `pytest-xdist`) |
| `--cov=src --cov-report=term-missing` | Coverage report (plugin `pytest-cov`) |
| `file.py::TestClass::test_name` | Run one specific test |

---

## 1. Install and First Test

> - **What:** Writing and running the simplest test.
> - **How:** A file named `test_*.py` with functions named `test_*` that use `assert`.
> - **When to use:** Start of every project, even with one function.

```powershell
pip install pytest            # or: uv add --dev pytest
```

```python
# src/pricing.py
def add_tax(price: float, rate: float = 0.19) -> float:
    """Return price including tax, rounded to cents."""
    return round(price * (1 + rate), 2)
```

```python
# tests/test_pricing.py
from pricing import add_tax


def test_add_tax_default_rate():
    assert add_tax(100) == 119.0


def test_add_tax_custom_rate():
    assert add_tax(100, rate=0.07) == 107.0
```

```powershell
pytest            # finds and runs all tests
```

## 2. Project Layout and Discovery

> - **What:** Where tests live and how pytest finds them.
> - **How:** pytest collects files `test_*.py` / `*_test.py`, functions `test_*`, classes `Test*` (no `__init__`).
> - **When to use:** Setting up a new project.

```text
project/
  pyproject.toml
  src/
    myapp/
      __init__.py
      pricing.py
  tests/
    conftest.py          shared fixtures
    test_pricing.py
    test_api.py
```

With a `src/` layout install your package in editable mode (`pip install -e .` / `uv sync`) or set `pythonpath = ["src"]` in the pytest config so imports work.

## 3. Assertions

> - **What:** Checking results with plain `assert`.
> - **How:** pytest rewrites asserts to show both sides of a failed comparison.
> - **When to use:** Every test.

```python
assert result == 42
assert "error" not in message
assert items == ["a", "b"]
assert user.is_active
assert len(rows) > 0
assert 0.1 + 0.2 == pytest.approx(0.3)                     # floats: never use == directly
assert {"a": 1}.items() <= result.items()                   # dict contains these keys / values
assert result == 42, f"unexpected result for input {x}"     # custom message
```

## 4. Testing Exceptions and Warnings

> - **What:** Checking that bad input raises the right error.
> - **How:** `pytest.raises` as a context manager; `match=` checks the message with a regex.
> - **When to use:** Validation logic, error paths.

```python
import pytest


def test_negative_price_raises():
    with pytest.raises(ValueError, match="must be positive"):
        add_tax(-5)


def test_deprecation():
    with pytest.warns(DeprecationWarning):
        old_function()
```

## 5. Fixtures

> - **What:** Reusable setup code that tests receive as arguments.
> - **How:** Decorate a function with `@pytest.fixture`; any test with a parameter of the same name gets its return value. Code after `yield` runs as cleanup.
> - **When to use:** Sample data, clients, temp files, database connections.

```python
import pandas as pd
import pytest


@pytest.fixture
def sample_df():
    return pd.DataFrame({"age": [25, None, 40], "city": ["Berlin", "Paris", None]})


@pytest.fixture
def db():
    conn = connect_test_db()
    yield conn                   # the test runs here
    conn.close()                 # cleanup, even if the test failed


def test_clean_fills_missing(sample_df):
    cleaned = clean(sample_df)
    assert cleaned["age"].isna().sum() == 0
```

Fixtures can use other fixtures by listing them as parameters.

## 6. Fixture Scope and conftest.py

> - **What:** How often a fixture is created, and where shared fixtures live.
> - **How:** `scope="function"` (default, fresh per test), `"module"`, `"session"` (once per run); fixtures in `conftest.py` are available to all tests in that folder.
> - **When to use:** Expensive setup (load a model, start a DB) shared by many tests.

```python
# tests/conftest.py
import pytest


@pytest.fixture(scope="session")
def embedding_model():
    return load_small_model()          # loaded once for the whole test run


@pytest.fixture(autouse=True)
def no_real_api_keys(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")   # applied to every test automatically
```

## 7. Built-in Fixtures

> - **What:** Fixtures pytest provides out of the box.
> - **How:** Just add their name as a test parameter.
> - **When to use:** Temp files, env vars, captured output, logs.

| Fixture | Gives you |
|---|---|
| `tmp_path` | A fresh temporary folder (`pathlib.Path`) |
| `monkeypatch` | Set / delete env vars, attributes, dict items temporarily |
| `capsys` | Captured `print` output (`capsys.readouterr().out`) |
| `caplog` | Captured log records |
| `request` | Info about the running test (for advanced fixtures) |

```python
def test_writes_report(tmp_path):
    out = tmp_path / "report.csv"
    write_report(out)
    assert out.read_text().startswith("date,total")


def test_reads_model_from_env(monkeypatch):
    monkeypatch.setenv("LLM_MODEL", "test-model")
    assert get_settings().llm_model == "test-model"
```

## 8. Parametrize

> - **What:** Running one test function with many input / expected pairs.
> - **How:** `@pytest.mark.parametrize("args", [cases])`; each case is reported as its own test.
> - **When to use:** Edge cases, tables of inputs, regex / parser tests.

```python
@pytest.mark.parametrize(
    ("price", "rate", "expected"),
    [
        (100, 0.19, 119.0),
        (0, 0.19, 0.0),
        (9.99, 0.07, 10.69),
    ],
    ids=["normal", "zero", "reduced-rate"],
)
def test_add_tax(price, rate, expected):
    assert add_tax(price, rate) == expected
```

## 9. Markers (skip, xfail, custom)

> - **What:** Labels that change how tests run.
> - **How:** `@pytest.mark.<name>`; select or skip with `-m`.
> - **When to use:** Slow tests, tests needing real API keys, known bugs.

```python
import os
import sys

import pytest


@pytest.mark.skip(reason="feature not ready")
def test_future(): ...


@pytest.mark.skipif(sys.platform == "win32", reason="Linux only")
def test_permissions(): ...


@pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="needs a real key")
@pytest.mark.integration
def test_real_llm_call(): ...


@pytest.mark.xfail(reason="bug #123, fix pending")
def test_known_bug(): ...
```

Register custom markers in `pyproject.toml` (section 17), then run `pytest -m "not integration"` locally and in fast CI.

## 10. Mocking with unittest.mock

> - **What:** Replacing a real dependency with a fake object you control.
> - **How:** `unittest.mock.patch` swaps an attribute during the test; `MagicMock` records calls and returns what you tell it.
> - **When to use:** External APIs, time, randomness, anything slow or non-deterministic.

```python
from unittest.mock import MagicMock, patch


def test_sends_email_on_signup():
    with patch("myapp.users.send_email") as fake_send:      # patch WHERE IT IS USED
        signup("ana@example.com")
    fake_send.assert_called_once_with("ana@example.com", subject="Welcome")


fake = MagicMock(return_value=42)
fake()                             # 42
fake.side_effect = ValueError("boom")   # raise instead
fake.side_effect = [1, 2, 3]            # return different values on each call
fake.call_count ; fake.call_args
```

Patch the name in the module that **uses** it (`myapp.users.send_email`), not where it is defined.

## 11. Mocking LLM Calls

> - **What:** Testing your LLM app code without calling a real model.
> - **How:** Inject a fake client (dependency injection) or patch the SDK method to return a canned response.
> - **When to use:** Unit tests for prompt building, output parsing, tool routing, error handling. Fast, free and deterministic.

```python
# app.py - the client is a parameter, so tests can pass a fake one
def summarize(text: str, client) -> str:
    msg = client.messages.create(
        model="claude-opus-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": f"Summarize:\n\n{text}"}],
    )
    return next(b.text for b in msg.content if b.type == "text")
```

```python
# tests/test_app.py
from types import SimpleNamespace
from unittest.mock import MagicMock

from app import summarize


def fake_message(text: str):
    return SimpleNamespace(content=[SimpleNamespace(type="text", text=text)], stop_reason="end_turn")


def test_summarize_returns_text_and_sends_prompt():
    client = MagicMock()
    client.messages.create.return_value = fake_message("Short summary.")

    result = summarize("Long article...", client)

    assert result == "Short summary."
    sent = client.messages.create.call_args.kwargs
    assert "Long article..." in sent["messages"][0]["content"]
```

Also test the unhappy paths: empty response, `stop_reason == "max_tokens"`, API errors (`side_effect=...`), invalid JSON.

## 12. Mocking HTTP Requests

> - **What:** Faking HTTP responses for code that uses requests or httpx.
> - **How:** Plugins intercept outgoing calls: `responses` (requests), `respx` (httpx).
> - **When to use:** Testing API clients and error handling (404, 429, timeouts).

```python
import responses


@responses.activate
def test_get_user():
    responses.get("https://api.example.com/users/1", json={"id": 1, "name": "Ana"}, status=200)
    assert get_user(1)["name"] == "Ana"


@responses.activate
def test_retries_on_429():
    responses.get("https://api.example.com/x", status=429)
    responses.get("https://api.example.com/x", json={"ok": True})
    assert fetch_with_retry("https://api.example.com/x") == {"ok": True}
```

## 13. Testing pandas Code

> - **What:** Comparing DataFrames and Series in tests.
> - **How:** `pandas.testing` helpers give readable diffs and handle NaN and dtypes.
> - **When to use:** Data cleaning and feature engineering functions.

```python
import pandas as pd
from pandas.testing import assert_frame_equal, assert_series_equal


def test_clean_names():
    df = pd.DataFrame({"name": ["  ana ", "BO"]})
    expected = pd.DataFrame({"name": ["Ana", "Bo"]})
    assert_frame_equal(clean_names(df), expected)

assert_frame_equal(a, b, check_dtype=False, check_like=True)   # ignore dtypes / column order
```

## 14. Testing FastAPI

> - **What:** Calling your API endpoints in tests without starting a server.
> - **How:** `TestClient(app)` sends requests directly to the app; `dependency_overrides` swaps dependencies (DB, settings, LLM client).
> - **When to use:** Every endpoint: status codes, validation errors, response shape.

```python
import pytest
from fastapi.testclient import TestClient

from app.main import app, get_llm_client


@pytest.fixture
def client():
    fake_llm = MagicMock()
    fake_llm.messages.create.return_value = fake_message("positive")
    app.dependency_overrides[get_llm_client] = lambda: fake_llm
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_classify_ok(client):
    r = client.post("/classify", json={"text": "I love it"})
    assert r.status_code == 200
    assert r.json() == {"label": "positive"}


def test_classify_validation_error(client):
    assert client.post("/classify", json={}).status_code == 422
```

## 15. Async Tests

> - **What:** Testing `async def` functions.
> - **How:** The `pytest-asyncio` plugin runs async tests in an event loop.
> - **When to use:** Async clients, agents, async FastAPI dependencies.

```powershell
pip install pytest-asyncio
```

```python
import pytest
from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_classify_async():
    client = MagicMock()
    client.messages.create = AsyncMock(return_value=fake_message("neutral"))
    assert await classify("ok", client) == "neutral"
```

Set `asyncio_mode = "auto"` in config to skip the decorator.

## 16. Coverage

> - **What:** Measuring which lines your tests execute.
> - **How:** `pytest-cov` runs coverage.py during the test run.
> - **When to use:** Finding untested code; CI quality gates. High coverage does not guarantee good tests.

```powershell
pip install pytest-cov
pytest --cov=src --cov-report=term-missing        # shows missing line numbers
pytest --cov=src --cov-report=html                # open htmlcov/index.html
pytest --cov=src --cov-fail-under=80              # fail if below 80%
```

## 17. Configuration (pyproject.toml)

> - **What:** Project-wide pytest settings.
> - **How:** `[tool.pytest.ini_options]` in `pyproject.toml` is read automatically.
> - **When to use:** Set test paths, default flags and markers once.

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
addopts = "-q --strict-markers"
asyncio_mode = "auto"
markers = [
    "integration: calls real external services (deselect with -m 'not integration')",
    "slow: takes more than a few seconds",
]
filterwarnings = ["error::DeprecationWarning"]
```

## 18. Good Testing Habits

> - **What:** Practices that keep tests useful.
> - **How:** Small, independent, fast, deterministic tests with clear names.
> - **When to use:** Always.

- Name tests after behaviour: `test_refund_fails_when_order_already_refunded`.
- One behaviour per test; several asserts about that behaviour are fine.
- Tests must not depend on each other or on execution order.
- No real network / LLM calls in unit tests; mark real ones `integration`.
- Fix randomness with seeds (`random.seed(0)`, `np.random.default_rng(0)`).
- When you fix a bug, first write a test that reproduces it.
- Run tests before every commit and in CI.

## 19. Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` for your package | `pythonpath = ["src"]` in config or `pip install -e .` |
| `collected 0 items` | File / function names must start with `test_`; check `testpaths` |
| Fixture `'x' not found` | Typo, or fixture defined in a `conftest.py` outside the test's folder |
| Patch has no effect | Patch where the name is used (`myapp.module.func`), not where it is defined |
| Float comparison fails (`0.30000000000000004`) | `pytest.approx` |
| `PytestUnknownMarkWarning` | Register the marker in `pyproject.toml` |
| Async test "passes" without running / coroutine never awaited | Install `pytest-asyncio`, add marker or `asyncio_mode = "auto"` |
| Tests pass alone, fail together | Shared state between tests; use fresh fixtures, reset globals, `dependency_overrides.clear()` |
| Flaky test | Remove time / network / randomness dependencies; mock them |
| `print` output not shown | `pytest -s` |
