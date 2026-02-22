# Nuroly-Observer

A lightweight, modular bot framework designed for flexibility. 

## Features
- **Plug-and-Play Commands:** Add new functionality by simply dropping a `.py` file into the `commands/` directory.
- **Provider Agnostic:** Built to support multiple platforms (Telegram, Slack, etc.) with a unified interface.

## Project Structure
- `main.py`: The core engine that orchestrates providers and commands.
- `router.py`: Handles command mapping and dynamic module loading.
- `providers/`: Platform-specific implementations (e.g., Telegram).
- `commands/`: Individual logic for bot features.

## Getting Started
1. **Clone the repo:** `git clone https://github.com/baldoor/nuroly-observer.git`
2. **Setup Environment:** - `python -m venv venv`
   - `source venv/bin/activate` (Windows: `venv\Scripts\activate`)
   - `pip install -r requirements.txt`
3. **Configure:** - `cp .env.example .env`
   - Fill in your configuration parameters
4. **Run:** `python main.py`