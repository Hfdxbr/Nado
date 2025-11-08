# Пакетный  менеджер UV
Установка
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Добавление пакетов
```bash
uv add $package
```
Добавление пакетов для разработки (тесты, профилировщики и т.д.)
```bash
uv add --dev $package
```
Быстрая установка всего
```bash
uv sync
```

# Запуск сервера
```bash
fastapi dev src/main.py
```

# Запуск тестов
```bash
pytest -v
```