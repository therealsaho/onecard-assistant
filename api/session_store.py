from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time

class SessionStore(ABC):
    """Abstract base class for session storage."""
    
    @abstractmethod
    def create_session(self, user_id: str, client_type: str, metadata: Dict[str, Any]) -> str:
        """Creates a new session and returns the session ID."""
        pass

    @abstractmethod
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves session data by ID."""
        pass

    @abstractmethod
    def update_session(self, session_id: str, data: Dict[str, Any]) -> None:
        """Updates session data."""
        pass

class InMemorySessionStore(SessionStore):
    """In-memory implementation of session store (for local dev)."""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(self, user_id: str, client_type: str, metadata: Dict[str, Any]) -> str:
        # Simple session ID generation (in real app use UUID)
        session_id = f"sess_{user_id}_{int(time.time())}"
        self.sessions[session_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "client_type": client_type,
            "created_at": time.time(),
            "metadata": metadata,
            "state": {} # Agent state
        }
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self.sessions.get(session_id)

    def update_session(self, session_id: str, data: Dict[str, Any]) -> None:
        if session_id in self.sessions:
            self.sessions[session_id].update(data)
