"""
HENU OS 3.0 — Build Engine
File: src/core/event_bus.py
Purpose: Lightweight publish/subscribe event system.
         Decouples plugins from pipeline stage implementations.
         Stages emit events; plugins subscribe to them.

         No global instances. EventBus is created by main.py and
         injected into the pipeline and plugin loader.

Usage:
    bus = EventBus()
    bus.subscribe("packages.installed", my_plugin_fn)
    bus.emit("packages.installed", context)
"""

from __future__ import annotations

from collections import defaultdict
from typing import Callable, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.build_context import BuildContext

# Type alias for event handler callbacks.
EventHandler = Callable[["BuildContext"], None]


class EventBus:
    """
    Simple publish/subscribe event bus for build pipeline events.

    Events are identified by string names (e.g., 'packages.installed').
    Multiple handlers can subscribe to the same event.
    Handlers are called in subscription order.

    Standard event names emitted by the pipeline:
        'build.started'
        'config.loaded'
        'validation.passed'
        'workspace.prepared'
        'packages.installed'
        'branding.applied'
        'desktop.configured'
        'components.deployed'
        'iso.created'
        'verification.passed'
        'checksums.generated'
        'manifest.generated'
        'build.released'
        'build.failed'
    """

    def __init__(self) -> None:
        self._handlers: Dict[str, List[EventHandler]] = defaultdict(list)

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        """
        Register a handler function for an event.

        Args:
            event_name — The event identifier string.
            handler    — Callable accepting BuildContext.
        """
        self._handlers[event_name].append(handler)

    def emit(self, event_name: str, context: "BuildContext") -> None:
        """
        Emit an event, invoking all registered handlers in order.
        Handler exceptions are caught and logged to context.errors
        to prevent one plugin failure from breaking the pipeline.

        Args:
            event_name — The event identifier string.
            context    — Current BuildContext passed to each handler.
        """
        for handler in self._handlers.get(event_name, []):
            try:
                handler(context)
            except Exception as exc:
                context.add_error(
                    f"EventBus handler for '{event_name}' raised: {exc}"
                )

    def subscribers(self, event_name: str) -> List[EventHandler]:
        """Returns list of handlers registered for an event."""
        return list(self._handlers.get(event_name, []))

    def clear(self) -> None:
        """Remove all registered handlers. Useful in test teardown."""
        self._handlers.clear()
