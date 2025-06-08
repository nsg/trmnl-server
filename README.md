# TRMNL Server

⚠️ **EXPERIMENTAL - NOT FINISHED** ⚠️

This is an experimental server that **isn't finished and doesn't really work yet**. The firmware is quite picky about the specifics of the bitmap format, making it difficult to debug and figure out what's going wrong. Due to time constraints, I've moved on to using a finished implementation instead of continuing to experiment with this approach.

While the TRMNL protocol is theoretically simple and elegant, and it would be nice to have a very lean and clean implementation, I don't have the time to debug the firmware compatibility issues. 

**Feel free to take inspiration from this code**, but don't count on it working out of the box. Most of the code is AI-generated, so the quality may not be the best. I wouldn't recommend using it as-is, but rather as a template or inspiration source.

I'll leave this up on GitHub in case anyone can benefit from it or wants to continue where I left off.

---

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
- Gradient bitmap generation for e-ink displays using Pillow
- Web-based log viewer with real-time updates
- RESTful API with automatic documentation

## API Documentation

Once running, visit:
- **Web interface**: http://localhost:4711
- **Log viewer**: http://localhost:4711/logs  
- **API docs**: http://localhost:4711/docs
