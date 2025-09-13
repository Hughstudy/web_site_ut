"""
Web Crawler UT System

A comprehensive system for generating test merchant websites with anti-crawler methods
for testing web crawlers and scrapers.

Modules:
- prompt_reader: System prompt management and templating
- openai_connector: OpenAI API integration with sync/async support
- environment_builder: Local test environment and server management
- website_generator: AI-powered website generation with anti-crawler methods
"""

from .prompt_reader import SystemPromptReader, PromptTemplate
from .openai_connector import OpenAIConnector, AsyncOpenAIConnector, OpenAIConfig
from .environment_builder import EnvironmentBuilder, LocalWebServer
from .website_generator import WebsiteGenerator
from .main import WebCrawlerUTSystem

__version__ = "0.1.0"
__author__ = "Web Crawler UT System"

__all__ = [
    "SystemPromptReader",
    "PromptTemplate",
    "OpenAIConnector",
    "AsyncOpenAIConnector",
    "OpenAIConfig",
    "EnvironmentBuilder",
    "LocalWebServer",
    "WebsiteGenerator",
    "WebCrawlerUTSystem"
]