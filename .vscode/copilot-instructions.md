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
- **Minimal commenting**: Only add comments for complex logic that needs explanation
- Function docstrings are fine, but avoid file-level descriptions and obvious comments
- If the code is self-explanatory, don't add comments explaining what it does

### Frontend Patterns
- Use vanilla JavaScript (no frameworks)

### Terminal Command Guidelines
- **ALWAYS** disable pagers when running git commands or other commands that might use a pager
- Use `git --no-pager` for git commands (e.g., `git --no-pager diff`, `git --no-pager show`)
- Alternatively, pipe commands through `cat` to prevent pager activation (e.g., `git diff | cat`)
- Commands that commonly use pagers: `git diff`, `git show`, `git log`, `less`, `man`
- This prevents the terminal from getting stuck in pager mode which cannot be handled programmatically

### Git Workflow
- Write clear, descriptive commit messages
- Use present tense ("Fix bug" not "Fixed bug")
- Include context about what and why, not just what changed
- Keep commits focused on single changes
- Keep commit messages concise, only list what changed from HEAD
- Always add `&& echo "Commit completed"` to git commit commands to prevent terminal hanging

### Common Tasks
- Server restart: `uv run uvicorn main:app --reload --host 0.0.0.0 --port 4711 --loop asyncio`

### Server Management Guidelines
- **DO NOT** start a new server if one is already running
- Always check if server is running before starting, check terminal output for that
- If uncertain whether server is running, assume it IS running and ask user for assistance
- Only start or stop the server when explicitly needed for testing or when user requests it
