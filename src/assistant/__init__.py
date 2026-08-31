"""Somali-first conversational assistant layer.

This package connects a general reasoning model to the project's reviewed Somali
language foundation. External/imported evidence may be retrieved as context, but
it is never promoted to trusted grammar by the assistant.
"""

from .model import ModelAdapter, OpenAIResponsesAdapter, StaticModelAdapter
from .pipeline import ConversationSession, SomaliAssistant
from .retrieval import KnowledgeHit, KnowledgeIndex
from .types import AssistantResult, ChatMessage

__all__ = [
    "AssistantResult",
    "ChatMessage",
    "ConversationSession",
    "KnowledgeHit",
    "KnowledgeIndex",
    "ModelAdapter",
    "OpenAIResponsesAdapter",
    "SomaliAssistant",
    "StaticModelAdapter",
]
