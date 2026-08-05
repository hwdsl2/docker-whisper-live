#!/usr/bin/env python3
"""Exercise the running WhisperLive WebSocket authentication handshake."""

import os
from http import HTTPStatus

from websockets.exceptions import InvalidStatus
from websockets.sync.client import connect


WS_URL = "ws://127.0.0.1:9090/"
API_KEY = os.environ.get("WS_API_KEY", "")
EXPECT_AUTH = os.environ.get("WS_EXPECT_AUTH", "1") == "1"


def expect_success(url=WS_URL, **kwargs):
    with connect(url, open_timeout=5, close_timeout=1, **kwargs):
        pass


def expect_unauthorized(url=WS_URL, **kwargs):
    try:
        expect_success(url, **kwargs)
    except InvalidStatus as exc:
        status = getattr(exc.response, "status_code", None)
        if status != HTTPStatus.UNAUTHORIZED:
            raise AssertionError(f"Expected HTTP 401, received {status}") from exc
    else:
        raise AssertionError("Expected the WebSocket handshake to be rejected")


if EXPECT_AUTH:
    if not API_KEY:
        raise AssertionError("WS_API_KEY must be set when authentication is expected")

    expect_success(additional_headers={"Authorization": f"Bearer {API_KEY}"})
    expect_success(f"{WS_URL}?token={API_KEY}")
    expect_unauthorized()
    expect_unauthorized(additional_headers={"Authorization": "Bearer incorrect-key"})
    expect_unauthorized(f"{WS_URL}?token=incorrect-key")
else:
    expect_success()

print("WebSocket authentication handshake checks passed")
