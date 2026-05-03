"""Global registry: all entities, skills, and event bus."""
from typing import Dict, List, Any, Callable
import json

class Registry:
    def __init__(self):
        self.entities: Dict[str, Any] = {}       # all game objects by ID
        self.skills: Dict[str, Any] = {}         # loaded skill modules
        self.event_handlers: Dict[str, List[Callable]] = {}  # event → callbacks
        self.config: Dict[str, Any] = {}
        self.rom_database: Dict[str, Any] = {}
        self.zones: List[Dict[str, Any]] = []
        self.player_state: Dict[str, Any] = {}
        self.state: Dict[str, Any] = {}
        
    def emit(self, event: str, **data):
        """Call all handlers for an event."""
        for handler in self.event_handlers.get(event, []):
            try:
                handler(**data)
            except Exception as e:
                print(f"[Event] handler error for {event}: {e}")
    
    def on(self, event: str, callback: Callable):
        """Register event handler."""
        self.event_handlers.setdefault(event, []).append(callback)

# Global singleton
reg = Registry()
