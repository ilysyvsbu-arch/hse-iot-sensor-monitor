import os
import logging
from fastapi import FastAPI

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# Чтение настроек из переменных окружения
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
MAX_TEMP_THRESHOLD = float(os.getenv("MAX_TEMP_THRESHOLD", "35.0"))

app = FastAPI(
    title="IoT Sensor Monitor API",
    description="Сервис для сбора, фильтрации и контроля показаний температурных IoT-датчиков",
    version=APP_VERSION,
)

logger.info(
    f"Starting IoT Sensor Monitor v{APP_VERSION} (Max temp threshold: {MAX_TEMP_THRESHOLD}°C)"
)


@app.get("/")
def root():
    logger.info("Root endpoint requested")
    return {"message": "IoT Sensor Monitor API is running", "docs": "/docs"}


@app.get("/health")
def health_check():
    logger.info("Health check requested")
    return {"status": "ok"}


@app.get("/version")
def get_version():
    logger.info("Version info requested")
    return {
        "version": APP_VERSION,
        "max_temp_threshold": MAX_TEMP_THRESHOLD,
    }
