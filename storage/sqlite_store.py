from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class StoredUserProfile:
    user_id: str
    role: str
    technical_level: str
    response_style: str
    preferred_format: str
    updated_at: str


@dataclass
class StoredChatMessage:
    id: int
    user_id: str
    dataset_name: str
    question: str
    route: str
    answer_preview: str
    created_at: str


class SQLiteStore:
    """
    Persistent storage for user profiles and chat/session history.

    This is not a vector database.
    It stores structured app memory in SQLite.
    """

    def __init__(self, db_path: str = "storage/app_memory.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _initialize_database(self) -> None:
        with self._connect() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    role TEXT NOT NULL,
                    technical_level TEXT NOT NULL,
                    response_style TEXT NOT NULL,
                    preferred_format TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    dataset_name TEXT NOT NULL,
                    question TEXT NOT NULL,
                    route TEXT NOT NULL,
                    answer_preview TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

            connection.commit()

    def save_user_profile(
        self,
        user_id: str,
        role: str,
        technical_level: str,
        response_style: str,
        preferred_format: str,
    ) -> None:
        updated_at = datetime.utcnow().isoformat()

        with self._connect() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO user_profiles (
                    user_id,
                    role,
                    technical_level,
                    response_style,
                    preferred_format,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    role = excluded.role,
                    technical_level = excluded.technical_level,
                    response_style = excluded.response_style,
                    preferred_format = excluded.preferred_format,
                    updated_at = excluded.updated_at
                """,
                (
                    user_id,
                    role,
                    technical_level,
                    response_style,
                    preferred_format,
                    updated_at,
                ),
            )

            connection.commit()

    def load_user_profile(self, user_id: str) -> StoredUserProfile | None:
        with self._connect() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    user_id,
                    role,
                    technical_level,
                    response_style,
                    preferred_format,
                    updated_at
                FROM user_profiles
                WHERE user_id = ?
                """,
                (user_id,),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return StoredUserProfile(
            user_id=row[0],
            role=row[1],
            technical_level=row[2],
            response_style=row[3],
            preferred_format=row[4],
            updated_at=row[5],
        )

    def save_chat_message(
        self,
        user_id: str,
        dataset_name: str,
        question: str,
        route: str,
        answer_preview: str,
    ) -> None:
        created_at = datetime.utcnow().isoformat()

        with self._connect() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO chat_history (
                    user_id,
                    dataset_name,
                    question,
                    route,
                    answer_preview,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    dataset_name,
                    question,
                    route,
                    answer_preview[:500],
                    created_at,
                ),
            )

            connection.commit()

    def load_recent_chat_history(
        self,
        user_id: str,
        limit: int = 10,
    ) -> list[StoredChatMessage]:
        with self._connect() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    id,
                    user_id,
                    dataset_name,
                    question,
                    route,
                    answer_preview,
                    created_at
                FROM chat_history
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_id, limit),
            )

            rows = cursor.fetchall()

        return [
            StoredChatMessage(
                id=row[0],
                user_id=row[1],
                dataset_name=row[2],
                question=row[3],
                route=row[4],
                answer_preview=row[5],
                created_at=row[6],
            )
            for row in rows
        ]

    def clear_chat_history(self, user_id: str) -> None:
        with self._connect() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                DELETE FROM chat_history
                WHERE user_id = ?
                """,
                (user_id,),
            )

            connection.commit()

    def summarize_memory(self, user_id: str) -> dict[str, Any]:
        profile = self.load_user_profile(user_id)
        history = self.load_recent_chat_history(user_id=user_id, limit=5)

        return {
            "has_profile": profile is not None,
            "profile": profile.__dict__ if profile else None,
            "recent_chat_count": len(history),
            "recent_questions": [
                message.question
                for message in history
            ],
        }