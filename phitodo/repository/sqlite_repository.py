"""SQLite repository for data persistence."""

import json
import os
from pathlib import Path
from typing import Optional

import aiosqlite

from phitodo.domain.models import StateSnapshot

# Default database path - compatible with Tauri version
DEFAULT_DB_PATH = Path.home() / ".local" / "share" / "phitodo" / "phitodo.db"


class SQLiteRepository:
    """SQLite repository for persisting application state."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize repository with database path."""
        self.db_path = db_path or DEFAULT_DB_PATH
        self._connection: Optional[aiosqlite.Connection] = None

    async def _get_connection(self) -> aiosqlite.Connection:
        """Get or create database connection."""
        if self._connection is None:
            # Ensure directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._connection = await aiosqlite.connect(self.db_path)
            await self._connection.execute("PRAGMA foreign_keys = ON")
        return self._connection

    async def close(self) -> None:
        """Close database connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None

    async def init_db(self) -> None:
        """Initialize database schema."""
        conn = await self._get_connection()

        await conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                due_date TEXT,
                start_date TEXT,
                completed_at TEXT,
                project_id TEXT,
                section_id TEXT,
                parent_task_id TEXT,
                priority TEXT NOT NULL DEFAULT 'none',
                status TEXT NOT NULL DEFAULT 'inbox',
                repeat_rule TEXT,
                order_index REAL NOT NULL DEFAULT 0,
                deleted INTEGER NOT NULL DEFAULT 0,
                kind TEXT,
                size TEXT,
                assignee TEXT,
                context_url TEXT,
                metadata TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id),
                FOREIGN KEY (section_id) REFERENCES sections(id),
                FOREIGN KEY (parent_task_id) REFERENCES tasks(id)
            );

            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                color TEXT,
                icon TEXT,
                order_index REAL NOT NULL DEFAULT 0,
                is_inbox INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                deleted INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS sections (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                name TEXT NOT NULL,
                order_index REAL NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                deleted INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            );

            CREATE TABLE IF NOT EXISTS tags (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                color TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                deleted INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS task_tags (
                task_id TEXT NOT NULL,
                tag_id TEXT NOT NULL,
                PRIMARY KEY (task_id, tag_id),
                FOREIGN KEY (task_id) REFERENCES tasks(id),
                FOREIGN KEY (tag_id) REFERENCES tags(id)
            );

            CREATE TABLE IF NOT EXISTS reminders (
                id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                cancelled_at TEXT,
                deleted INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            );

            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
            CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id);
            CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
            CREATE INDEX IF NOT EXISTS idx_task_tags_tag ON task_tags(tag_id);
        """
        )

        await conn.commit()

    async def get_snapshot(self) -> StateSnapshot:
        """Load state snapshot from database."""
        conn = await self._get_connection()

        # Try to load from JSON snapshot first (for compatibility)
        cursor = await conn.execute(
            "SELECT value FROM metadata WHERE key = 'snapshot'"
        )
        row = await cursor.fetchone()

        if row and row[0]:
            try:
                data = json.loads(row[0])
                return StateSnapshot.from_dict(data)
            except (json.JSONDecodeError, KeyError):
                pass

        # Fall back to loading from individual tables
        return await self._load_from_tables()

    async def _load_from_tables(self) -> StateSnapshot:
        """Load state from individual tables."""
        conn = await self._get_connection()
        from phitodo.domain.models import Project, Reminder, Section, Tag, Task

        # Load tasks
        tasks = {}
        cursor = await conn.execute("SELECT * FROM tasks")
        async for row in cursor:
            task_data = {
                "id": row[0],
                "title": row[1],
                "notes": row[2],
                "created_at": row[3],
                "updated_at": row[4],
                "due_date": row[5],
                "start_date": row[6],
                "completed_at": row[7],
                "project_id": row[8],
                "section_id": row[9],
                "parent_task_id": row[10],
                "priority": row[11],
                "status": row[12],
                "repeat_rule": row[13],
                "order_index": row[14],
                "deleted": bool(row[15]),
                "kind": row[16],
                "size": row[17],
                "assignee": row[18],
                "context_url": row[19],
                "metadata": json.loads(row[20]) if row[20] else {},
                "tags": [],
            }
            tasks[row[0]] = Task.from_dict(task_data)

        # Load task tags
        cursor = await conn.execute("SELECT task_id, tag_id FROM task_tags")
        async for row in cursor:
            if row[0] in tasks:
                tasks[row[0]].tags.append(row[1])

        # Load projects
        projects = {}
        cursor = await conn.execute("SELECT * FROM projects")
        async for row in cursor:
            project_data = {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "color": row[3],
                "icon": row[4],
                "order_index": row[5],
                "is_inbox": bool(row[6]),
                "created_at": row[7],
                "updated_at": row[8],
                "deleted": bool(row[9]),
            }
            projects[row[0]] = Project.from_dict(project_data)

        # Load sections
        sections = {}
        cursor = await conn.execute("SELECT * FROM sections")
        async for row in cursor:
            section_data = {
                "id": row[0],
                "project_id": row[1],
                "name": row[2],
                "order_index": row[3],
                "created_at": row[4],
                "updated_at": row[5],
                "deleted": bool(row[6]),
            }
            sections[row[0]] = Section.from_dict(section_data)

        # Load tags
        tags = {}
        cursor = await conn.execute("SELECT * FROM tags")
        async for row in cursor:
            tag_data = {
                "id": row[0],
                "name": row[1],
                "color": row[2],
                "created_at": row[3],
                "updated_at": row[4],
                "deleted": bool(row[5]),
            }
            tags[row[0]] = Tag.from_dict(tag_data)

        # Load reminders
        reminders = {}
        cursor = await conn.execute("SELECT * FROM reminders")
        async for row in cursor:
            reminder_data = {
                "id": row[0],
                "task_id": row[1],
                "at": row[2],
                "created_at": row[3],
                "updated_at": row[4],
                "cancelled_at": row[5],
                "deleted": bool(row[6]),
            }
            reminders[row[0]] = Reminder.from_dict(reminder_data)

        return StateSnapshot(
            tasks=tasks,
            projects=projects,
            sections=sections,
            tags=tags,
            reminders=reminders,
        )

    async def save_snapshot(self, snapshot: StateSnapshot) -> None:
        """Save state snapshot to database."""
        conn = await self._get_connection()

        # Save as JSON snapshot for quick loading
        snapshot_json = json.dumps(snapshot.to_dict())
        await conn.execute(
            "INSERT OR REPLACE INTO metadata (key, value) VALUES ('snapshot', ?)",
            (snapshot_json,),
        )

        # Also save to individual tables for compatibility
        await self._save_to_tables(snapshot)

        await conn.commit()

    async def _save_to_tables(self, snapshot: StateSnapshot) -> None:
        """Save state to individual tables."""
        conn = await self._get_connection()

        # Save tasks
        for task in snapshot.tasks.values():
            await conn.execute(
                """
                INSERT OR REPLACE INTO tasks
                (id, title, notes, created_at, updated_at, due_date, start_date,
                 completed_at, project_id, section_id, parent_task_id, priority,
                 status, repeat_rule, order_index, deleted, kind, size, assignee,
                 context_url, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    task.id,
                    task.title,
                    task.notes,
                    task.created_at,
                    task.updated_at,
                    task.due_date,
                    task.start_date,
                    task.completed_at,
                    task.project_id,
                    task.section_id,
                    task.parent_task_id,
                    task.priority.value,
                    task.status.value,
                    task.repeat_rule,
                    task.order_index,
                    int(task.deleted),
                    task.kind.value if task.kind else None,
                    task.size.value if task.size else None,
                    task.assignee,
                    task.context_url,
                    json.dumps(task.metadata) if task.metadata else None,
                ),
            )

            # Save task tags
            await conn.execute("DELETE FROM task_tags WHERE task_id = ?", (task.id,))
            for tag_id in task.tags:
                await conn.execute(
                    "INSERT OR IGNORE INTO task_tags (task_id, tag_id) VALUES (?, ?)",
                    (task.id, tag_id),
                )

        # Save projects
        for project in snapshot.projects.values():
            await conn.execute(
                """
                INSERT OR REPLACE INTO projects
                (id, name, description, color, icon, order_index, is_inbox,
                 created_at, updated_at, deleted)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    project.id,
                    project.name,
                    project.description,
                    project.color,
                    project.icon,
                    project.order_index,
                    int(project.is_inbox),
                    project.created_at,
                    project.updated_at,
                    int(project.deleted),
                ),
            )

        # Save sections
        for section in snapshot.sections.values():
            await conn.execute(
                """
                INSERT OR REPLACE INTO sections
                (id, project_id, name, order_index, created_at, updated_at, deleted)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    section.id,
                    section.project_id,
                    section.name,
                    section.order_index,
                    section.created_at,
                    section.updated_at,
                    int(section.deleted),
                ),
            )

        # Save tags
        for tag in snapshot.tags.values():
            await conn.execute(
                """
                INSERT OR REPLACE INTO tags
                (id, name, color, created_at, updated_at, deleted)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    tag.id,
                    tag.name,
                    tag.color,
                    tag.created_at,
                    tag.updated_at,
                    int(tag.deleted),
                ),
            )

        # Save reminders
        for reminder in snapshot.reminders.values():
            await conn.execute(
                """
                INSERT OR REPLACE INTO reminders
                (id, task_id, at, created_at, updated_at, cancelled_at, deleted)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    reminder.id,
                    reminder.task_id,
                    reminder.at,
                    reminder.created_at,
                    reminder.updated_at,
                    reminder.cancelled_at,
                    int(reminder.deleted),
                ),
            )
