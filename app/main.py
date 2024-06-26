import time
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_versioning import VersionedFastAPI
from redis import asyncio as aioredis
from sqladmin import Admin
from prometheus_fastapi_instrumentator import Instrumentator

from app.admin.auth import authentication_backend
from app.admin.views import BookingsAdmin, HotelsAdmin, RoomsAdmin, UsersAdmin
from app.bookings.router import router as booking_router
from app.config import settings
from app.database import engine
from app.hotels.rooms.router import router as rooms_router
from app.hotels.router import router as hotels_router
from app.images.router import router as images_router
from app.logger import logger
from app.pages.router import router as pages_router
from app.users.router import router as users_router
from app.prometheus.router import router as prometheus_router


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa
    redis = aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        encoding="utf8",
        decode_responses=True,
    )
    FastAPICache.init(RedisBackend(redis), prefix="hotels_cache")
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(users_router)
app.include_router(booking_router)
app.include_router(hotels_router)
app.include_router(rooms_router)

app.include_router(pages_router)
app.include_router(images_router)

app.include_router(prometheus_router)

# Подключение CORS, чтобы запросы к API могли приходить из браузера
origins = [
    # 3000 - порт, на котором работает фронтенд на React.js
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Authorization",
    ],
)

app = VersionedFastAPI(
    app,
    version_format="{major}",
    prefix_format="/v{major}",
    # description='Greet users with a nice message',
    # middleware=[
    #    Middleware(SessionMiddleware, secret_key='mysecretkey')
    # ]
)


instrumentator = Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=[".*admin.*", "/metrics"],
)

instrumentator.instrument(app).expose(app)


admin = Admin(app, engine, authentication_backend=authentication_backend)
admin.add_view(UsersAdmin)
admin.add_view(HotelsAdmin)
admin.add_view(RoomsAdmin)
admin.add_view(BookingsAdmin)

staticFiles = StaticFiles(directory="app/static")
app.mount(path="/static", app=staticFiles, name="static")


# @app.middleware("http")
# async def add_process_time_handler(request: Request, call_next):
#     start_time = time.time()
#     response = await call_next(request)
#     process_time = time.time() - start_time
#     logger.info("Request handling time", extra={"process_time": round(process_time, 4)})
#     return response


sentry_sdk.init(
    dsn="https://5efb5fbe6db600668117a86a4444ee07@o4507176366440448.ingest.us.sentry.io/4507176368275456",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)
