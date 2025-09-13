# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Web Crawler Unit Testing System that generates test websites for evaluating web crawler performance. The system uses any OpenAI-compatible API to generate realistic websites with various anti-crawler methods from natural language prompts.

## Core Architecture

The system is built around 4 main modules in `src/`:

1. **SystemPromptReader** (`prompt_reader.py`) - Manages system prompts from JSON files in `prompts/` directory
2. **OpenAIConnector** (`openai_connector.py`) - Handles OpenAI-compatible API communication with sync/async support
3. **EnvironmentBuilder** (`environment_builder.py`) - Creates local test environments and runs web servers
4. **WebsiteGenerator** (`website_generator.py`) - Orchestrates the other modules to generate and deploy websites

The `WebCrawlerUTSystem` class in `src/main.py` coordinates all modules together.

## Key Dependencies

- Python 3.12+
- OpenAI Python SDK (>= 1.68.0) - works with any OpenAI-compatible API
- Requires `OPENAI_API_KEY` environment variable
- Optional: `OPENAI_BASE_URL` for custom API endpoints

## Current Model Configuration

- Default model: `moonshotai/kimi-k2-0905` (Moonshot AI Kimi)
- Supports any OpenAI-compatible API (OpenRouter, DeepSeek, etc.)
- Configure via environment variables or modify `OpenAIConfig` in `openai_connector.py`

## Usage Commands

### Install dependencies:
```bash
uv sync
# or
pip install -r requirements.txt
```

### Run the system:
```bash
python -m src.main generate --type electronics --port 8080
python -m src.main list                    # List all environments
python -m src.main cleanup <env_name>      # Clean up specific environment
python -m src.main remove <env_name>       # Remove specific environment
python -m src.main remove --all            # Remove all environments
python -m src.main stop                    # Stop all servers
```

## System Prompts

The system uses JSON-based prompts in `prompts/` directory:
- `flexible_website_generator.json` - Main prompt for generating any type of website
- `merchant_website_generator.json` - Specific merchant site generation
- `anti_crawler_specialist.json` - Advanced anti-crawler implementations
- `crawler_test_prompt.json` - Test scenario generation

## Website Generation Flow

1. User provides natural language prompt (completely flexible - any website type)
2. SystemPromptReader loads `flexible_website_generator` prompt template
3. OpenAIConnector sends request to configured AI model
4. WebsiteGenerator parses response into HTML/CSS/JS files using `generate_website_from_prompt()`
5. EnvironmentBuilder creates local directory and starts HTTP server
6. Returns localhost URL for testing

## Key Methods

- `WebsiteGenerator.generate_website_from_prompt(user_prompt, additional_requirements)` - Main generation method
- `WebCrawlerUTSystem.remove_environment(env_name)` - Remove specific environment
- `WebCrawlerUTSystem.remove_all_environments()` - Clean up all historical files

## Local Test Environments

- Created in `test_environments/` directory
- Each environment gets its own subdirectory with generated files
- Local HTTP servers run on available ports starting from 8000
- Supports multiple concurrent test environments

## Anti-Crawler Methods

The system can implement various anti-crawler techniques:
- Rate limiting with JavaScript tracking
- User agent detection
- JavaScript-dependent content loading
- CAPTCHA challenges
- Dynamic content via AJAX
- Session tracking
- IP-based blocking simulation
- Honeypot trap links

## Environment Management Commands

- `cleanup <env_name>` - Legacy command (same as remove)
- `remove <env_name>` - Remove specific environment and all files
- `remove --all` - Remove all historical test environments and files
- `stop` - Stop all running servers but keep files
- `list` - Show all environments and their server status

## Important Notes

- Always set `OPENAI_API_KEY` and optionally `OPENAI_BASE_URL` before running
- System automatically finds free ports for web servers
- Generated websites are stored locally and served via Python's HTTP server
- Prompt system allows complete flexibility - any website type can be generated from natural language
- Use `remove --all` to clean up all historical files and start fresh
- Default model is Moonshot AI Kimi but can be changed in configuration