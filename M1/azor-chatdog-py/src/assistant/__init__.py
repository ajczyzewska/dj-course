"""
Assistant module initialization
Exports the Assistant class and assistant factory functions.
"""

from .assistent import Assistant
from .assistants_registry import (
    create_azor_assistant,
    get_assistant,
    list_assistants,
    get_all_assistants,
    register_assistant,
    ASSISTANTS
)

__all__ = [
    'Assistant',
    'create_azor_assistant',
    'get_assistant',
    'list_assistants',
    'get_all_assistants',
    'register_assistant',
    'ASSISTANTS'
]
