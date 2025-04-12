import fastapi
import routers.auth as auth
from logger import logger

if __name__ == "__main__":
    logger.info("started")

upkeep = fastapi.FastAPI(
    title="Backend Upkeep Now",
    description="TCC, consiste em um gerenciador de manutenções",
    version="0.0.1",
)

upkeep.include_router(auth.router)
