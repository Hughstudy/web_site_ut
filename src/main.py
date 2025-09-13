"""
Web Crawler UT System - Main Application

This is the main entry point for the web crawler unit testing system.
It integrates all three modules and provides a simple CLI interface.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Optional, List

from .prompt_reader import SystemPromptReader
from .openai_connector import OpenAIConnector, OpenAIConfig
from .environment_builder import EnvironmentBuilder
from .website_generator import WebsiteGenerator


class WebCrawlerUTSystem:
    """
    Main system class that coordinates all modules
    """

    def __init__(self):
        """Initialize all system components"""
        self.prompt_reader = SystemPromptReader()
        self.openai_config = OpenAIConfig()
        self.openai_connector = OpenAIConnector(self.openai_config)
        self.env_builder = EnvironmentBuilder()
        self.website_generator = WebsiteGenerator(
            openai_connector=self.openai_connector,
            prompt_reader=self.prompt_reader,
            env_builder=self.env_builder
        )

    def generate_test_merchant_website(self,
                                     merchant_type: str = "electronics",
                                     style: str = "modern",
                                     anti_crawler_methods: Optional[List[str]] = None,
                                     custom_requirements: Optional[str] = None,
                                     port: int = 8000) -> dict:
        """
        Generate and deploy a test merchant website

        Args:
            merchant_type: Type of merchant (electronics, clothing, books, etc.)
            style: Website style (modern, classic, minimalist, etc.)
            anti_crawler_methods: List of anti-crawler methods to implement
            custom_requirements: Additional custom requirements
            port: Port to run the local server on

        Returns:
            dict: Deployment information including URL and details
        """
        print(f"🔄 Generating {merchant_type} merchant website with {style} style...")

        result = self.website_generator.generate_and_deploy(
            merchant_type=merchant_type,
            style=style,
            anti_crawler_methods=anti_crawler_methods,
            custom_requirements=custom_requirements,
            port=port
        )

        if result.get("success"):
            print(f"✅ Website generated and deployed successfully!")
            print(f"🌐 Access your test site at: {result['server_url']}")
            print(f"📁 Environment: {result['environment_name']}")

            # Print anti-crawler methods implemented
            metadata = result["website_data"]["metadata"]
            methods = metadata.get("anti_crawler_methods", [])
            if methods:
                print(f"🛡️  Anti-crawler methods: {', '.join(methods)}")

        return result

    def list_environments(self):
        """List all available test environments"""
        environments = self.env_builder.list_environments()
        if environments:
            print("📋 Available test environments:")
            for env in environments:
                info = self.env_builder.get_environment_info(env)
                status = "🟢 Running" if info["server_running"] else "⚫ Stopped"
                url = info["server_url"] or "N/A"
                print(f"  • {env}: {status} - {url}")
        else:
            print("📋 No test environments found.")

    def cleanup_environment(self, env_name: str):
        """Clean up a specific environment"""
        try:
            self.env_builder.cleanup_environment(env_name)
            print(f"🧹 Environment '{env_name}' cleaned up successfully.")
        except Exception as e:
            print(f"❌ Failed to cleanup environment '{env_name}': {e}")

    def stop_all_servers(self):
        """Stop all running servers"""
        self.env_builder.stop_all_servers()
        print("🛑 All servers stopped.")

    def remove_environment(self, env_name: str):
        """Remove a specific environment and its files"""
        try:
            self.env_builder.cleanup_environment(env_name)
            print(f"🗑️ Environment '{env_name}' removed successfully.")
        except Exception as e:
            print(f"❌ Failed to remove environment '{env_name}': {e}")

    def remove_all_environments(self):
        """Remove all test environments and files"""
        environments = self.env_builder.list_environments()
        if not environments:
            print("📋 No environments to remove.")
            return

        try:
            for env in environments:
                self.env_builder.cleanup_environment(env)
                print(f"🗑️ Removed: {env}")
            print(f"✅ All {len(environments)} environments removed successfully.")
        except Exception as e:
            print(f"❌ Error removing environments: {e}")


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Web Crawler UT System")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate a test merchant website')
    gen_parser.add_argument('--type', default='electronics',
                           choices=['electronics', 'clothing', 'books', 'furniture', 'jewelry', 'sports'],
                           help='Type of merchant website')
    gen_parser.add_argument('--style', default='modern',
                           choices=['modern', 'classic', 'minimalist', 'colorful', 'dark'],
                           help='Website style')
    gen_parser.add_argument('--port', type=int, default=8000, help='Port to run server on')
    gen_parser.add_argument('--anti-crawler', nargs='+',
                           choices=['rate_limiting', 'user_agent_detection', 'javascript_rendering',
                                   'captcha_challenges', 'dynamic_content_loading', 'session_tracking',
                                   'ip_blocking', 'honeypot_links'],
                           help='Anti-crawler methods to implement')
    gen_parser.add_argument('--requirements', help='Additional custom requirements')

    # List command
    subparsers.add_parser('list', help='List all test environments')

    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Cleanup a test environment')
    cleanup_parser.add_argument('env_name', help='Environment name to cleanup')

    # Stop command
    subparsers.add_parser('stop', help='Stop all running servers')

    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Remove test environments')
    remove_parser.add_argument('env_name', nargs='?', help='Environment name to remove (optional)')
    remove_parser.add_argument('--all', action='store_true', help='Remove all environments')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize system
    try:
        system = WebCrawlerUTSystem()
    except Exception as e:
        print(f"❌ Failed to initialize system: {e}")
        print("💡 Make sure you have set the OPENAI_API_KEY environment variable")
        return

    # Execute commands
    try:
        if args.command == 'generate':
            system.generate_test_merchant_website(
                merchant_type=args.type,
                style=args.style,
                anti_crawler_methods=args.anti_crawler,
                custom_requirements=args.requirements,
                port=args.port
            )

        elif args.command == 'list':
            system.list_environments()

        elif args.command == 'cleanup':
            system.cleanup_environment(args.env_name)

        elif args.command == 'stop':
            system.stop_all_servers()

        elif args.command == 'remove':
            if args.all:
                system.remove_all_environments()
            elif args.env_name:
                system.remove_environment(args.env_name)
            else:
                print("❌ Please specify an environment name or use --all flag")
                print("   Examples:")
                print("     python -m src.main remove my_environment")
                print("     python -m src.main remove --all")

    except Exception as e:
        print(f"❌ Error executing command: {e}")


if __name__ == "__main__":
    main()