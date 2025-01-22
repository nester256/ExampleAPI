from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from webapp.api.base.router import base_router
from webapp.integrations.metrics.metrics import metrics
from webapp.integrations.middleware.middleware import LogServerMiddleware, prometheus_metrics


def setup_middleware(app: FastAPI) -> None:
    app.add_middleware(
        LogServerMiddleware,
    )
    # CORS Middleware should be the last.
    # See https://github.com/tiangolo/fastapi/issues/1663 .
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    app.middleware('http')(prometheus_metrics)


def setup_routers(app: FastAPI) -> None:
    app.add_route('/metrics', metrics)
    routers = [
        base_router,
    ]
    for router in routers:
        app.include_router(router)


def create_app() -> FastAPI:
    app = FastAPI(docs_url='/swagger')
    setup_middleware(app)
    setup_routers(app)
    return app