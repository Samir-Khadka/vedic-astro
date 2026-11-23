"""Shared pytest fixtures for the Vedic Astro suite.

Rate-limiter isolation
----------------------
main.py keeps a per-IP sliding-window limiter (60 heavy requests per 60s
by default) in the module-level ``main._RL_BUCKETS``. Every TestClient
request comes from the same fake client address, so the whole suite
shares ONE bucket. On a slow machine the window slides and nothing
trips; on a fast runner (GitHub Actions) more than 60 heavy requests
land inside one 60s window and unrelated tests get ``429`` instead of
``200`` — which is what turned CI red on tests/test_worldclass2.py.

The fixture below empties the buckets before and after every test, so
each test starts with a clean limiter regardless of machine speed or
test order. It changes nothing in production code: the limiter, its
limit and its window are untouched, and the tests that assert the
limiter works (tests/test_api.py::test_rate_limit_*) still set their
own low ``VEDIC_RL_LIMIT`` and trip it within a single test.
"""
from __future__ import annotations

import pytest

import main as main_module


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    main_module._RL_BUCKETS.clear()
    yield
    main_module._RL_BUCKETS.clear()
