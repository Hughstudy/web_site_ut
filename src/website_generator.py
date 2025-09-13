"""
Website Generator Module

This module generates test merchant websites with various anti-crawler methods
and different styles for testing web crawlers.
"""

import json
import random
from typing import Dict, Any, List, Optional
from pathlib import Path

from .prompt_reader import SystemPromptReader
from .openai_connector import OpenAIConnector, AsyncOpenAIConnector
from .environment_builder import EnvironmentBuilder


class WebsiteGenerator:
    """
    Generates test merchant websites with anti-crawler methods
    """

    def __init__(self,
                 openai_connector: Optional[OpenAIConnector] = None,
                 prompt_reader: Optional[SystemPromptReader] = None,
                 env_builder: Optional[EnvironmentBuilder] = None):
        """
        Initialize the website generator

        Args:
            openai_connector: OpenAI connector instance
            prompt_reader: System prompt reader instance
            env_builder: Environment builder instance
        """
        self.openai_connector = openai_connector or OpenAIConnector()
        self.prompt_reader = prompt_reader or SystemPromptReader()
        self.env_builder = env_builder or EnvironmentBuilder()

    def generate_website_from_prompt(self,
                                   user_prompt: str,
                                   additional_requirements: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a website based on user's natural language prompt

        Args:
            user_prompt: Natural language description of what website to generate
            additional_requirements: Additional requirements or constraints

        Returns:
            Dict[str, Any]: Generated website data including files and metadata
        """
        # Get system prompt for website generation
        try:
            system_prompt = self.prompt_reader.get_prompt("flexible_website_generator")
        except KeyError:
            # Use default system prompt if custom one doesn't exist
            system_prompt = self._get_default_system_prompt()

        # Construct full prompt
        full_prompt = f"User Request: {user_prompt}"

        if additional_requirements:
            full_prompt += f"\n\nAdditional Requirements: {additional_requirements}"

        full_prompt += """

Please generate a complete, functional website based on the user's request. Include:
1. HTML files (at minimum index.html, plus any other pages that make sense)
2. CSS file for styling
3. JavaScript file for functionality
4. Any data files (JSON/XML) if needed for content
5. robots.txt if appropriate

Make the website realistic and functional for testing purposes.
"""

        # Generate website content
        try:
            response = self.openai_connector.generate_text(
                prompt=full_prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=4000
            )

            # Parse the generated content and create files
            website_files = self._parse_generated_content(response)

            # Add metadata
            metadata = {
                "user_prompt": user_prompt,
                "additional_requirements": additional_requirements,
                "generation_timestamp": str(Path().resolve())
            }

            return {
                "files": website_files,
                "metadata": metadata,
                "raw_response": response
            }

        except Exception as e:
            raise Exception(f"Failed to generate website: {e}")

    def deploy_to_local_environment(self,
                                  website_data: Dict[str, Any],
                                  env_name: Optional[str] = None,
                                  port: Optional[int] = None) -> str:
        """
        Deploy generated website to local environment

        Args:
            website_data: Website data from generate_merchant_website
            env_name: Environment name (auto-generated if None)
            port: Port to run server on

        Returns:
            str: URL of the deployed website
        """
        if env_name is None:
            metadata = website_data.get("metadata", {})
            merchant_type = metadata.get("merchant_type", "merchant")
            env_name = f"{merchant_type}_test_{random.randint(1000, 9999)}"

        # Create environment
        env_path = self.env_builder.create_test_environment(env_name, clean=True)

        # Write website files
        files = website_data.get("files", {})
        self.env_builder.create_website_files(env_path, files)

        # Write metadata
        metadata_path = env_path / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(website_data.get("metadata", {}), f, indent=2)

        # Start local server
        server_url = self.env_builder.start_local_server(env_name, port)

        return server_url

    def generate_and_deploy(self,
                          user_prompt: str,
                          additional_requirements: Optional[str] = None,
                          env_name: Optional[str] = None,
                          port: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate and deploy a website in one step

        Args:
            user_prompt: Natural language description of website to generate
            additional_requirements: Additional requirements or constraints
            env_name: Environment name
            port: Server port

        Returns:
            Dict[str, Any]: Deployment information including URL
        """
        # Generate website
        website_data = self.generate_website_from_prompt(
            user_prompt=user_prompt,
            additional_requirements=additional_requirements
        )

        # Deploy to local environment
        server_url = self.deploy_to_local_environment(
            website_data=website_data,
            env_name=env_name,
            port=port
        )

        return {
            "website_data": website_data,
            "server_url": server_url,
            "environment_name": env_name or "generated_test",
            "success": True
        }

    def _get_default_system_prompt(self) -> str:
        """Get default system prompt for website generation"""
        return """
        You are an expert web developer specializing in creating realistic e-commerce websites for testing purposes.

        Your task is to generate complete, functional websites with the following characteristics:
        - Realistic product listings and data
        - Professional styling and layout
        - Implement specified anti-crawler methods effectively
        - Include multiple pages (home, products, about, contact)
        - Use modern web technologies (HTML5, CSS3, JavaScript)
        - Make the website look and feel like a real merchant site

        Anti-crawler methods to implement when requested:
        - rate_limiting: Add JavaScript to track request frequency
        - user_agent_detection: Check for common bot user agents
        - javascript_rendering: Require JS to load content
        - captcha_challenges: Add CAPTCHA-like challenges
        - dynamic_content_loading: Load content dynamically with AJAX
        - session_tracking: Track user sessions
        - ip_blocking: Simulate IP-based blocking
        - honeypot_links: Add hidden links to catch bots

        Return the complete code for each file clearly separated and labeled.
        """

    def _parse_generated_content(self, response: str) -> Dict[str, str]:
        """
        Parse the generated content and extract individual files

        Args:
            response: Raw response from OpenAI

        Returns:
            Dict[str, str]: Dictionary of filename -> content
        """
        files = {}
        current_file = None
        current_content = []

        lines = response.split('\n')

        for line in lines:
            # Look for file markers (various formats)
            if any(marker in line.lower() for marker in ['filename:', 'file:', '<!-- file:', '// file:', '# file:']):
                # Save previous file if exists
                if current_file and current_content:
                    files[current_file] = '\n'.join(current_content)

                # Extract filename
                for marker in ['filename:', 'file:', '<!-- file:', '// file:', '# file:']:
                    if marker in line.lower():
                        current_file = line.lower().split(marker)[1].strip().replace('-->', '').strip()
                        break

                current_content = []

            elif line.strip().startswith('```') and current_file:
                # Skip code block markers
                continue

            elif current_file:
                current_content.append(line)

        # Save last file
        if current_file and current_content:
            files[current_file] = '\n'.join(current_content)

        # If no files were parsed, create default structure
        if not files:
            files = self._create_default_website_structure(response)

        return files

    def _create_default_website_structure(self, content: str) -> Dict[str, str]:
        """
        Create default website structure if parsing fails

        Args:
            content: Raw content from OpenAI

        Returns:
            Dict[str, str]: Default website files
        """
        return {
            "index.html": f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Merchant Site</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <h1>Test Merchant Website</h1>
    <p>Generated content:</p>
    <pre>{content[:1000]}...</pre>
    <script src="script.js"></script>
</body>
</html>""",
            "styles.css": """
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
    background-color: #f5f5f5;
}

h1 {
    color: #333;
    text-align: center;
}

pre {
    background: #fff;
    padding: 15px;
    border-radius: 5px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}""",
            "script.js": """
// Basic anti-crawler functionality
console.log('Website loaded');

// Simple rate limiting
let requestCount = 0;
const MAX_REQUESTS = 10;

function checkRateLimit() {
    requestCount++;
    if (requestCount > MAX_REQUESTS) {
        alert('Too many requests!');
        return false;
    }
    return true;
}

// User agent detection
if (navigator.userAgent.includes('bot') || navigator.userAgent.includes('crawler')) {
    console.warn('Bot detected!');
}"""
        }