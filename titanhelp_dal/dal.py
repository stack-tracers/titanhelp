from __future__ import annotations
import sqlite3
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

STATUS_VALUES = ("Open", "In Progress", "Closed")
PRIORITY_VALUES = ("Low", "Medium", "High")

# ---- Row dict factory (must be defined before use) ----
def _dict_factory(cursor: sqlite3.Cursor, row: sqlite3.Row) -> Dict[str, Any]:
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

# ---- Domain model ----
@dataclass(slots=True)
class Ticket:
    id: Optional[int]
    name: str
    description: str
    status: str = "Open"
    priority: str = "Low"
    created_at: Optional[str] = None  # ISO8601 UTC

    def to_db_tuple(self) -> Tuple[Any, ...]:
        return (self.name, self.description, self.status, self.priority)
    
    @property
    def date(self) -> Optional[str]:
        """Alias for created_at (so templates can use ticket.date)."""
        return self.created_at

# ---- DAL ----
class TitanHelpDAL:
    """
    SQLite Data Access Layer for TitanHelp tickets.
    Creates DB and schema on first use.
    """
    def __init__(
        self,
        db_path: str = "titanhelp.db",
        *,
        journal_mode: str = "WAL",      # use "DELETE" in tests on Windows
        synchronous: str = "NORMAL"
    ) -> None:
        self.db_path = db_path
        self.journal_mode = journal_mode
        self.synchronous = synchronous
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = _dict_factory
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute(f"PRAGMA journal_mode = {self.journal_mode};")
        conn.execute(f"PRAGMA synchronous = {self.synchronous};")
        return conn

    def _ensure_schema(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL CHECK(length(name) <= 100),
                    created_at TEXT NOT NULL DEFAULT (strftime('%m-%d-%Y %H:%M:%S','now')),
                    description TEXT NOT NULL CHECK(length(description) <= 1000),
                    status TEXT NOT NULL DEFAULT 'Open' CHECK(status IN ('Open','In Progress','Closed')),
                    priority TEXT NOT NULL DEFAULT 'Low' CHECK(priority IN ('Low','Medium','High'))
                );
                """
            )
            cur.execute("CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_tickets_priority ON tickets(priority);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_tickets_created ON tickets(created_at);")
            conn.commit()

    # ---- validations ----
    @staticmethod
    def _validate_name(name: str) -> None:
        if not name or not name.strip():
            raise ValueError("Name is required")
        if len(name) > 100:
            raise ValueError("Name must be ≤ 100 characters")

    @staticmethod
    def _validate_description(description: str) -> None:
        if not description or not description.strip():
            raise ValueError("Problem Description is required")
        if len(description) > 1000:
            raise ValueError("Problem Description must be ≤ 1000 characters")

    @staticmethod
    def _validate_status(status: str) -> None:
        if status not in STATUS_VALUES:
            raise ValueError(f"Status must be one of {STATUS_VALUES}")

    @staticmethod
    def _validate_priority(priority: str) -> None:
        if priority not in PRIORITY_VALUES:
            raise ValueError(f"Priority must be one of {PRIORITY_VALUES}")

    # ---- CRUD ----
    def create_ticket(self, name: str, description: str, *, priority: str = "Low") -> Ticket:
        self._validate_name(name)
        self._validate_description(description)
        self._validate_priority(priority)
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO tickets(name, description, status, priority) VALUES (?,?,?,?)",
                (name.strip(), description.strip(), "Open", priority),
            )
            ticket_id = cur.lastrowid
            row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        return self._row_to_ticket(row)

    def get_ticket(self, ticket_id: int) -> Optional[Ticket]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
            return self._row_to_ticket(row) if row else None

    def list_tickets(
        self,
        *,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        sort: str = "created_at DESC",
    ) -> List[Ticket]:
        clauses: List[str] = []
        params: List[Any] = []
        if status:
            self._validate_status(status)
            clauses.append("status = ?")
            params.append(status)
        if priority:
            self._validate_priority(priority)
            clauses.append("priority = ?")
            params.append(priority)
        if search:
            clauses.append("(name LIKE ? OR description LIKE ?)")
            like = f"%{search}%"
            params.extend([like, like])
        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        query = f"SELECT * FROM tickets {where} ORDER BY {sort} LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        with self._connect() as conn:
            rows = conn.execute(query, tuple(params)).fetchall()
        return [self._row_to_ticket(r) for r in rows]

    def update_ticket(
        self,
        ticket_id: int,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
    ) -> Optional[Ticket]:
        sets: List[str] = []
        params: List[Any] = []

        if name is not None:
            self._validate_name(name)
            sets.append("name = ?")
            params.append(name.strip())
        if description is not None:
            self._validate_description(description)
            sets.append("description = ?")
            params.append(description.strip())
        if status is not None:
            self._validate_status(status)
            sets.append("status = ?")
            params.append(status)
        if priority is not None:
            self._validate_priority(priority)
            sets.append("priority = ?")
            params.append(priority)

        if not sets:
            return self.get_ticket(ticket_id)

        with self._connect() as conn:
            conn.execute(f"UPDATE tickets SET {', '.join(sets)} WHERE id = ?", (*params, ticket_id))
            row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
            return self._row_to_ticket(row) if row else None

    def delete_ticket(self, ticket_id: int) -> bool:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
            return cur.rowcount > 0

    def set_status(self, ticket_id: int, status: str) -> Optional[Ticket]:
        return self.update_ticket(ticket_id, status=status)

    def set_priority(self, ticket_id: int, priority: str) -> Optional[Ticket]:
        return self.update_ticket(ticket_id, priority=priority)

    @staticmethod
    def _row_to_ticket(row: Dict[str, Any]) -> Ticket:
        return Ticket(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            status=row["status"],
            priority=row["priority"],
            created_at=row["created_at"],
        )


if __name__ == "__main__":
    dal = TitanHelpDAL("titanhelp.db")
    t = dal.create_ticket("Example", "My printer is on fire", priority="High")
    print("Created:", t)
    print("List:", dal.list_tickets())
    t = dal.set_status(t.id, "In Progress")
    print("Updated:", t)
