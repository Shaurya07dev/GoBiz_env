# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
FastAPI application for the businessenv Environment.

Endpoints:
    - POST /reset: Reset the environment
    - POST /step: Execute an action
    - GET /state: Get current environment state
    - GET /schema: Get action/observation schemas
    - WS /ws: WebSocket endpoint for persistent sessions
    - GET /health: Health check
    - GET /web: Interactive web interface

Usage:
    uvicorn server.app:app --reload --host 0.0.0.0 --port 8000
"""

try:
    from openenv.core.env_server import create_fastapi_app
except Exception:
    # Backward-compatible fallback for older openenv versions.
    from openenv.core.env_server.http_server import create_app as create_fastapi_app

try:
    from .environment import BusinessEnv
    from ..models import BusinessAction, BusinessObservation
except (ImportError, ModuleNotFoundError):
    from businessenv.server.environment import BusinessEnv
    from businessenv.models import BusinessAction, BusinessObservation


from fastapi.responses import RedirectResponse

app = create_fastapi_app(BusinessEnv, BusinessAction, BusinessObservation)

@app.get("/")
def read_root():
    return RedirectResponse(url="/web")


def main(host: str = "0.0.0.0", port: int = 8000):
    """Entry point for direct execution via uv run or python -m.

    Usage:
        uv run --project . server
        python -m businessenv.server.app
    """
    import uvicorn

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
