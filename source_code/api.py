"""Compatibility entrypoint that delegates API internals to apps.api."""

from apps.api.app import app, serve

__all__ = ["app", "serve"]