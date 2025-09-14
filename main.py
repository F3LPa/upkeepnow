import time
import fastapi
from fastapi.middleware.cors import CORSMiddleware
import routers.auth as auth

upkeep = fastapi.FastAPI(
    title="Backend Upkeep Now",
    description="TCC, consiste em um gerenciador de manutenções",
    version="0.0.1",
)

upkeep.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@upkeep.middleware("http")
async def add_process_time_header(request: fastapi.Request, call_next):
    start_time = time.perf_counter()
    response: fastapi.Response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

upkeep.include_router(auth.router)
