# IoT Sensor Monitor API

REST-сервис на FastAPI для сбора, хранения, фильтрации и анализа показаний температурных IoT-датчиков (серверные комнаты, офисы, лаборатории). Предназначен для системных администраторов и инженеров инфраструктуры, которым нужно отслеживать перегрев оборудования и получать статистику по датчикам.

## Структура проекта
* `app_final.py` — основной код FastAPI-приложения.
* `test_app.py` — автоматические тесты (`pytest`).
* `requirements.txt` / `requirements-dev.txt` — зависимости проекта.
* `.env.example` — пример файла с переменными окружения.
* `.github/workflows/ci.yml` — конфигурация CI и сборки артефакта в GitHub Actions.

## 1. Создание окружения и установка зависимостей

Клонируйте репозиторий и создайте виртуальное окружение:

```bash
git clone [https://github.com/ilysyvsbu-arch/hse-iot-sensor-monitor.git](https://github.com/ilysyvsbu-arch/hse-iot-sensor-monitor.git)
cd hse-iot-sensor-monitor
python3 -m venv .venv