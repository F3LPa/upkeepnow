import time
import fastapi
import fastapi.middleware
import routers.auth as auth
from logger import logger

upkeep = fastapi.FastAPI(
    title="Backend Upkeep Now",
    description="TCC, consiste em um gerenciador de manutenções",
    version="0.0.1",
)


@upkeep.middleware("https")
async def add_process_time_header(request: fastapi.Request, call_next):
    start_time = time.perf_counter()
    response: fastapi.Response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


upkeep.include_router(auth.router)
