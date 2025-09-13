"""
System Prompt Reader Module

This module handles reading, validating, and managing system prompts
from various file formats (JSON, YAML, TXT).
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
from pydantic import BaseModel, ValidationError


class PromptTemplate(BaseModel):
    """Pydantic model for prompt template validation"""
    name: str
    description: Optional[str] = None
    template: str
    variables: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class SystemPromptReader:
    """
    Handles reading and processing system prompts from files
    """

    def __init__(self, prompts_directory: Union[str, Path] = "prompts"):
        """
        Initialize the prompt reader

        Args:
            prompts_directory: Directory containing prompt files
        """
        self.prompts_directory = Path(prompts_directory)
        self.prompts_directory.mkdir(exist_ok=True)

    def read_prompt_from_file(self, file_path: Union[str, Path]) -> PromptTemplate:
        """
        Read a single prompt from a file

        Args:
            file_path: Path to the prompt file

        Returns:
            PromptTemplate: Validated prompt template

        Raises:
            FileNotFoundError: If file doesn't exist
            ValidationError: If prompt format is invalid
            ValueError: If file format is unsupported
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {file_path}")

        suffix = file_path.suffix.lower()

        try:
            if suffix == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            elif suffix in ['.yaml', '.yml']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
            elif suffix == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    data = {
                        "name": file_path.stem,
                        "template": content,
                        "description": f"Prompt from {file_path.name}"
                    }
            else:
                raise ValueError(f"Unsupported file format: {suffix}")

            return PromptTemplate(**data)

        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ValueError(f"Error parsing {file_path}: {e}")
        except ValidationError as e:
            raise ValidationError(f"Invalid prompt format in {file_path}: {e}")

    def load_all_prompts(self) -> Dict[str, PromptTemplate]:
        """
        Load all prompts from the prompts directory

        Returns:
            Dict[str, PromptTemplate]: Dictionary of loaded prompts
        """
        prompts = {}
        supported_extensions = ['.json', '.yaml', '.yml', '.txt']

        for file_path in self.prompts_directory.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                try:
                    prompt = self.read_prompt_from_file(file_path)
                    prompts[prompt.name] = prompt
                except Exception as e:
                    print(f"Warning: Failed to load prompt from {file_path}: {e}")

        return prompts

    def substitute_variables(self, template: str, variables: Dict[str, Any]) -> str:
        """
        Substitute variables in a template string

        Args:
            template: Template string with {variable} placeholders
            variables: Dictionary of variable values

        Returns:
            str: Template with variables substituted
        """
        try:
            return template.format(**variables)
        except KeyError as e:
            raise ValueError(f"Missing variable for template substitution: {e}")

    def get_prompt(self, name: str, variables: Optional[Dict[str, Any]] = None) -> str:
        """
        Get a processed prompt by name

        Args:
            name: Name of the prompt
            variables: Variables to substitute in the template

        Returns:
            str: Processed prompt text

        Raises:
            KeyError: If prompt name not found
        """
        prompts = self.load_all_prompts()

        if name not in prompts:
            raise KeyError(f"Prompt '{name}' not found. Available prompts: {list(prompts.keys())}")

        prompt = prompts[name]
        template = prompt.template

        if variables:
            template = self.substitute_variables(template, variables)
        elif prompt.variables:
            template = self.substitute_variables(template, prompt.variables)

        return template

    def create_prompt_template(self, name: str, template: str,
                             description: Optional[str] = None,
                             variables: Optional[Dict[str, Any]] = None,
                             save_to_file: bool = False) -> PromptTemplate:
        """
        Create a new prompt template

        Args:
            name: Name of the prompt
            template: Prompt template string
            description: Optional description
            variables: Default variables
            save_to_file: Whether to save to file

        Returns:
            PromptTemplate: Created prompt template
        """
        prompt = PromptTemplate(
            name=name,
            description=description,
            template=template,
            variables=variables
        )

        if save_to_file:
            file_path = self.prompts_directory / f"{name}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(prompt.dict(), f, indent=2, ensure_ascii=False)

        return prompt