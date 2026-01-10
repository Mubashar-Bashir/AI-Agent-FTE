"""
Utility functions module for the Automated Workspace Observer.

This module contains helper functions for logging, YAML parsing, and file operations.
"""
import logging
import os
from pathlib import Path
import sys
from datetime import datetime


def setup_logger(name: str = "workspace_observer", log_file: str = "logs/observer.log"):
    """
    Set up a logger for the observer.

    Args:
        name: Name of the logger
        log_file: Path to the log file

    Returns:
        Logger instance
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Prevent duplicate handlers if logger already exists
    if logger.handlers:
        return logger

    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def safe_read_file(file_path: str) -> str:
    """
    Safely read a file with error handling.

    Args:
        file_path: Path to the file to read

    Returns:
        File content as string, or empty string if error occurs
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception:
            return ""
    except FileNotFoundError:
        return ""
    except Exception as e:
        logger = setup_logger()
        logger.error(f"Error reading file {file_path}: {e}")
        return ""


def safe_write_file(file_path: str, content: str) -> bool:
    """
    Safely write content to a file with error handling.

    Args:
        file_path: Path to the file to write
        content: Content to write

    Returns:
        True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        logger = setup_logger()
        logger.error(f"Error writing file {file_path}: {e}")
        return False


def extract_yaml_front_matter(content: str) -> tuple:
    """
    Extract YAML front matter from content (between --- delimiters).

    Args:
        content: String content to extract YAML from

    Returns:
        Tuple of (yaml_content, remaining_content)
    """
    try:
        lines = content.split('\n')
        yaml_start_idx = -1
        yaml_end_idx = -1

        for i, line in enumerate(lines):
            if line.strip() == '---' and yaml_start_idx == -1:
                yaml_start_idx = i
            elif line.strip() == '---' and yaml_start_idx != -1 and yaml_end_idx == -1:
                yaml_end_idx = i
                break

        if yaml_start_idx != -1 and yaml_end_idx != -1 and yaml_start_idx < yaml_end_idx:
            yaml_content = '\n'.join(lines[yaml_start_idx + 1:yaml_end_idx])
            remaining_content = '\n'.join(lines[yaml_end_idx + 1:])
            return yaml_content.strip(), remaining_content.strip()
        else:
            return "", content
    except Exception as e:
        logger = setup_logger()
        logger.error(f"Error extracting YAML front matter: {e}")
        return "", content


def validate_yaml_structure(data: dict) -> list:
    """
    Validate common YAML metadata structures.

    Args:
        data: Dictionary containing YAML data

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    if data is None:
        return ["YAML data is None"]

    if not isinstance(data, dict):
        return ["YAML data is not a dictionary"]

    # Check for common expected fields if they exist
    if 'status' in data:
        if not isinstance(data['status'], str):
            errors.append("status field should be a string")

    if 'percentage' in data or 'percent' in data:
        percent_val = data.get('percentage') or data.get('percent')
        if not isinstance(percent_val, (int, float)) and not str(percent_val).isdigit():
            errors.append("percentage field should be a number")

    if 'next_step' in data or 'next' in data:
        next_val = data.get('next_step') or data.get('next')
        if not isinstance(next_val, str):
            errors.append("next_step field should be a string")

    return errors