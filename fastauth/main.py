from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from fastauth.common.settings import settings
from fastauth.db import get_async_engine, init_db
from fastauth.routers import auth_router, google_auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire de cycle de vie de l'application."""
    await init_db(engine=get_async_engine())
    yield


app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan)

# Necessary for OAuth2
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.JWT_SECRET_KEY,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix=f"{settings.API_PREFIX}/auth")
app.include_router(google_auth_router, prefix=f"{settings.API_PREFIX}/auth/google")


@app.get("/")
def read_root():
    """Test endpoint to check if the server is running."""
    return {"message": "Server is running"}
