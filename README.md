# TRMNL Server

A FastAPI-based server for TRMNL e-ink displays that handles device logging, setup, and serves dynamic bitmap images.

## Quick Start

```bash
# Install dependencies
uv sync

# Start development server
uv run uvicorn main:app --reload --host 0.0.0.0 --port 4711
```

## Features

- Device log collection and storage
- Device setup and registration  
- Dynamic bitmap generation for e-ink displays
- Web-based log viewer with real-time updates
- RESTful API with automatic documentation

## API Documentation

Once running, visit:
- **Web interface**: http://localhost:4711
- **Log viewer**: http://localhost:4711/logs  
- **API docs**: http://localhost:4711/docs
