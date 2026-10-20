import os
import logging
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

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


class SensorReading(BaseModel):
    sensor_id: str = Field(..., min_length=2, description="Уникальный ID датчика (например, sensor-01)")
    location: str = Field(..., description="Помещение (например, Server Room)")
    temperature: float = Field(..., ge=-50.0, le=150.0, description="Температура в °C")
    humidity: float = Field(..., ge=0.0, le=100.0, description="Влажность в %")


# Предзаполненные данные в оперативной памяти
READINGS_DB: list[dict] = [
    {"sensor_id": "srv-01", "location": "Server Room", "temperature": 22.5, "humidity": 40.0, "alert": False},
    {"sensor_id": "srv-02", "location": "Server Room", "temperature": 38.0, "humidity": 35.0, "alert": True},
    {"sensor_id": "off-01", "location": "Office 101", "temperature": 24.0, "humidity": 50.0, "alert": False},
]


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


# Полезный маршрут №1: Добавление нового показания датчика
@app.post("/readings", status_code=201)
def add_reading(reading: SensorReading):
    is_overheated = reading.temperature > MAX_TEMP_THRESHOLD
    record = reading.model_dump()
    record["alert"] = is_overheated
    READINGS_DB.append(record)

    if is_overheated:
        logger.warning(
            f"ALERT! High temperature from {reading.sensor_id}: {reading.temperature}°C > {MAX_TEMP_THRESHOLD}°C"
        )
    else:
        logger.info(f"Recorded reading from {reading.sensor_id}: {reading.temperature}°C")

    return record


# Полезный маршрут №2: Список показаний с фильтрацией по query-параметрам
@app.get("/readings")
def list_readings(
    location: str | None = Query(default=None, description="Фильтр по названию помещения"),
    alert_only: bool = Query(default=False, description="Показать только превышения порога температуры"),
):
    logger.info(f"Listing readings (location={location}, alert_only={alert_only})")
    results = READINGS_DB
    if location:
        results = [r for r in results if r["location"].lower() == location.lower()]
    if alert_only:
        results = [r for r in results if r["alert"] is True]
    return {"count": len(results), "items": results}


# Полезный маршрут №3: Статистика по конкретному датчику (path-параметр sensor_id)
@app.get("/sensors/{sensor_id}/stats")
def get_sensor_stats(sensor_id: str):
    logger.info(f"Calculating stats for sensor_id={sensor_id}")
    sensor_data = [r for r in READINGS_DB if r["sensor_id"] == sensor_id]
    if not sensor_data:
        logger.error(f"Sensor '{sensor_id}' not found")
        raise HTTPException(status_code=404, detail=f"Sensor '{sensor_id}' not found")

    temps = [r["temperature"] for r in sensor_data]
    return {
        "sensor_id": sensor_id,
        "location": sensor_data[-1]["location"],
        "readings_count": len(temps),
        "min_temperature": min(temps),
        "max_temperature": max(temps),
        "avg_temperature": round(sum(temps) / len(temps), 2),
        "has_alerts": any(r["alert"] for r in sensor_data),
    }
