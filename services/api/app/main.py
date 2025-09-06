from __future__ import annotations

import os
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from app.routers import goals, questions, plan, feedback


def create_app() -> FastAPI:
    app = FastAPI(
        title="SMB Goal→Plan API",
        default_response_class=ORJSONResponse,
    )

    @app.get("/health")
    def health():
        return {"ok": True}

    app.include_router(goals.router)
    app.include_router(questions.router)
    app.include_router(plan.router)
    app.include_router(feedback.router)

    return app


app = create_app()

# Convenience for local run: `uvicorn app.main:app --reload --app-dir services/api/app`
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)

