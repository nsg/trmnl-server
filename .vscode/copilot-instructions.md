# TRMNL Server Project - AI Assistant Instructions

## Project Overview
This is a FastAPI-based server for TRMNL e-ink displays. The server handles device logging, setup, and serves bitmap images to the devices.

## Key Technologies
- FastAPI
- SQLAlchemy
- Pydantic V2
- SQLite
- uvicorn
- uv

## Development Guidelines

### Code Style Preferences
- Use **black** for Python formatting
- Prefer **async/await** for database operations

### Frontend Patterns
- Use vanilla JavaScript (no frameworks)

### Git Workflow
- Write clear, descriptive commit messages
- Use present tense ("Fix bug" not "Fixed bug")
- Include context about what and why, not just what changed
- Keep commits focused on single changes
- Keep commit messages concise, only list what changed from HEAD

### Common Tasks
- Server restart: `uv run uvicorn main:app --reload --host 0.0.0.0 --port 4711`
