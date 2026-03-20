"""Supporting scripts and utilities used throughout the AffineDrift toolkit."""

import logging

from .update_navigation import main as update_nav_cli
from .update_navigation import update_navigation

__all__ = ["update_nav_cli", "update_navigation"]
