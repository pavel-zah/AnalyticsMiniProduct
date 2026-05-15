import asyncio
import threading
import uuid
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator, Dict, List
from pathlib import Path


@dataclass
class SessionData:
    session_id: str
    file_path: str
    user_message: str
    status: str = "pending"  # pending, processing, completed, error
    artifacts: List[Dict[str, Any]] = field(default_factory=list)
    error_message: str = ""
    lock: threading.Lock = field(default_factory=threading.Lock)


class SessionStore:
    def __init__(self):
        self.sessions: Dict[str, SessionData] = {}
        self.lock = threading.Lock()

    def create_session(self, user_message: str = "") -> str:
        """Create a new session and return session_id"""
        session_id = str(uuid.uuid4())
        with self.lock:
            self.sessions[session_id] = SessionData(
                session_id=session_id,
                file_path="",
                user_message=user_message,
            )
        return session_id

    def get_session(self, session_id: str) -> SessionData | None:
        """Get session by id"""
        with self.lock:
            return self.sessions.get(session_id)

    def update_session_file(self, session_id: str, file_path: str) -> bool:
        """Update file path for session"""
        with self.lock:
            if session_id in self.sessions:
                self.sessions[session_id].file_path = file_path
                return True
            return False

    def set_status(self, session_id: str, status: str) -> bool:
        """Set session status"""
        session = self.get_session(session_id)
        if session:
            with session.lock:
                session.status = status
                return True
        return False

    def add_artifact(self, session_id: str, artifact: Dict[str, Any]) -> bool:
        """Add artifact to session"""
        session = self.get_session(session_id)
        if session:
            with session.lock:
                session.artifacts.append(artifact)
                return True
        return False

    def set_error(self, session_id: str, error_message: str) -> bool:
        """Set error for session"""
        session = self.get_session(session_id)
        if session:
            with session.lock:
                session.status = "error"
                session.error_message = error_message
                return True
        return False

    def get_artifacts(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all artifacts for session"""
        session = self.get_session(session_id)
        if session:
            with session.lock:
                return session.artifacts.copy()
        return []


# Global session store instance
session_store = SessionStore()
