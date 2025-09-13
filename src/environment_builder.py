"""
Auto Local Environment Builder Module

This module handles automatic setup and management of local testing environments,
including directory structures, configurations, and web server hosting.
"""

import os
import shutil
import subprocess
import threading
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import TCPServer
import socket
from contextlib import closing


class LocalWebServer:
    """
    Simple HTTP server for hosting generated websites locally
    """

    def __init__(self, directory: Path, port: int = 8000):
        """
        Initialize the local web server

        Args:
            directory: Directory to serve files from
            port: Port to run the server on
        """
        self.directory = directory
        self.port = port
        self.server = None
        self.server_thread = None
        self.is_running = False

    def find_free_port(self, start_port: int = 8000) -> int:
        """
        Find a free port starting from the given port

        Args:
            start_port: Starting port to check

        Returns:
            int: Free port number
        """
        port = start_port
        while port < 65535:
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                if sock.connect_ex(('localhost', port)) != 0:
                    return port
            port += 1
        raise RuntimeError("No free ports available")

    def start(self) -> int:
        """
        Start the web server

        Returns:
            int: Port the server is running on
        """
        if self.is_running:
            return self.port

        # Find a free port if the specified one is taken
        try:
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                if sock.connect_ex(('localhost', self.port)) == 0:
                    self.port = self.find_free_port(self.port + 1)
        except:
            pass

        class CustomHandler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(directory), **kwargs)

        directory = self.directory

        try:
            self.server = HTTPServer(('localhost', self.port), CustomHandler)
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            self.is_running = True
            print(f"Server started at http://localhost:{self.port}")
            return self.port
        except Exception as e:
            raise RuntimeError(f"Failed to start server: {e}")

    def stop(self):
        """Stop the web server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.is_running = False
            print("Server stopped")

    def get_url(self) -> Optional[str]:
        """Get the server URL"""
        if self.is_running:
            return f"http://localhost:{self.port}"
        return None


class EnvironmentBuilder:
    """
    Handles automatic setup and management of local testing environments
    """

    def __init__(self, base_directory: Optional[Path] = None):
        """
        Initialize the environment builder

        Args:
            base_directory: Base directory for all test environments
        """
        self.base_directory = base_directory or Path("test_environments")
        self.base_directory.mkdir(exist_ok=True)
        self.active_servers: Dict[str, LocalWebServer] = {}

    def create_test_environment(self, name: str, clean: bool = True) -> Path:
        """
        Create a new test environment directory

        Args:
            name: Name of the test environment
            clean: Whether to clean existing environment

        Returns:
            Path: Path to the created environment directory
        """
        env_path = self.base_directory / name

        if env_path.exists() and clean:
            shutil.rmtree(env_path)

        env_path.mkdir(exist_ok=True)

        # Create standard subdirectories
        (env_path / "static").mkdir(exist_ok=True)
        (env_path / "templates").mkdir(exist_ok=True)
        (env_path / "assets").mkdir(exist_ok=True)
        (env_path / "css").mkdir(exist_ok=True)
        (env_path / "js").mkdir(exist_ok=True)
        (env_path / "images").mkdir(exist_ok=True)

        return env_path

    def setup_environment_variables(self, env_vars: Dict[str, str], env_file: Optional[Path] = None):
        """
        Setup environment variables

        Args:
            env_vars: Dictionary of environment variables
            env_file: Optional path to .env file to create
        """
        # Set environment variables for current session
        for key, value in env_vars.items():
            os.environ[key] = value

        # Optionally create .env file
        if env_file:
            with open(env_file, 'w') as f:
                for key, value in env_vars.items():
                    f.write(f"{key}={value}\n")

    def create_website_files(self, env_path: Path, website_content: Dict[str, str]):
        """
        Create website files in the environment

        Args:
            env_path: Environment directory path
            website_content: Dictionary of filename -> content
        """
        for filename, content in website_content.items():
            file_path = env_path / filename

            # Create subdirectories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write content to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

    def start_local_server(self, env_name: str, port: Optional[int] = None) -> str:
        """
        Start a local web server for the environment

        Args:
            env_name: Name of the environment
            port: Optional port number (will find free port if not specified)

        Returns:
            str: URL of the started server
        """
        env_path = self.base_directory / env_name

        if not env_path.exists():
            raise ValueError(f"Environment '{env_name}' does not exist")

        if env_name in self.active_servers:
            return self.active_servers[env_name].get_url()

        port = port or 8000
        server = LocalWebServer(env_path, port)
        actual_port = server.start()

        self.active_servers[env_name] = server

        return f"http://localhost:{actual_port}"

    def stop_local_server(self, env_name: str):
        """
        Stop the local server for an environment

        Args:
            env_name: Name of the environment
        """
        if env_name in self.active_servers:
            self.active_servers[env_name].stop()
            del self.active_servers[env_name]

    def stop_all_servers(self):
        """Stop all running servers"""
        for env_name in list(self.active_servers.keys()):
            self.stop_local_server(env_name)

    def cleanup_environment(self, env_name: str):
        """
        Clean up a test environment

        Args:
            env_name: Name of the environment to clean up
        """
        # Stop server if running
        self.stop_local_server(env_name)

        # Remove directory
        env_path = self.base_directory / env_name
        if env_path.exists():
            shutil.rmtree(env_path)

    def list_environments(self) -> List[str]:
        """
        List all available test environments

        Returns:
            List[str]: List of environment names
        """
        return [d.name for d in self.base_directory.iterdir() if d.is_dir()]

    def get_environment_info(self, env_name: str) -> Dict[str, Any]:
        """
        Get information about a test environment

        Args:
            env_name: Name of the environment

        Returns:
            Dict[str, Any]: Environment information
        """
        env_path = self.base_directory / env_name

        if not env_path.exists():
            raise ValueError(f"Environment '{env_name}' does not exist")

        info = {
            "name": env_name,
            "path": str(env_path),
            "exists": env_path.exists(),
            "server_running": env_name in self.active_servers,
            "server_url": self.active_servers[env_name].get_url() if env_name in self.active_servers else None,
            "files": []
        }

        # List files in the environment
        if env_path.exists():
            for file_path in env_path.rglob('*'):
                if file_path.is_file():
                    info["files"].append(str(file_path.relative_to(env_path)))

        return info

    def install_dependencies(self, requirements: List[str], env_path: Optional[Path] = None):
        """
        Install Python dependencies (useful for more complex test environments)

        Args:
            requirements: List of package requirements
            env_path: Optional path to install dependencies in
        """
        if env_path:
            # Create a requirements.txt file
            req_file = env_path / "requirements.txt"
            with open(req_file, 'w') as f:
                for req in requirements:
                    f.write(f"{req}\n")

        # Install using uv if available, otherwise pip
        try:
            subprocess.run(["uv", "pip", "install"] + requirements, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                subprocess.run(["pip", "install"] + requirements, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Failed to install dependencies: {e}")

    def __del__(self):
        """Cleanup when object is destroyed"""
        self.stop_all_servers()