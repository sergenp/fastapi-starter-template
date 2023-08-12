from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth.v1 import router as auth_router
from app.api.users.v1 import router as users_router
from app.config import settings
from app.exceptions import get_exception_handlers


def create_app():
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="Fastapi Starter Template",
        version="0.0.1",
        terms_of_service="https://mit-license.org",
        contact={
            "name": "Sergen Pekşen",
            "url": "https://mit-license.org",
            "email": "peksensergen@gmail.com",
        },
        license_info={
            "name": "MIT",
            "url": "https://mit-license.org",
        },
    )
    return app


def add_routers(app: FastAPI):
    app.include_router(users_router, prefix=f"/{settings.API_V1_STR}", tags=["users"])
    app.include_router(auth_router, prefix=f"/{settings.API_V1_STR}", tags=["auth"])


def add_middlewares(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def add_exception_handlers(app: FastAPI):
    for exc, handler in get_exception_handlers():
        app.add_exception_handler(exc, handler)


app = create_app()
add_routers(app)
add_middlewares(app)
add_exception_handlers(app)
