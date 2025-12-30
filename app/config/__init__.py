"""
Config Package
"""

# Import settings from app/config.py (the file, not this directory)
# Use importlib to avoid circular import
import importlib.util
import os

# Get the parent directory (app/)
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_file = os.path.join(parent_dir, "config.py")

# Load config.py as a module
spec = importlib.util.spec_from_file_location("app_config", config_file)
config_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config_module)

# Export settings
settings = config_module.settings

__all__ = ["settings"]
