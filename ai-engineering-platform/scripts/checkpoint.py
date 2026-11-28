"""チケット単位のチェックポイントを保存する。"""

from contextlib import closing, contextmanager
import json
from pathlib import Path
import re
import sqlite3


STATES = {
    "PLANNED", "DESIGNED", "DESIGN_REVIEWED", "IMPLEMENTED", "TESTED",
    "REVIEWED", "FIXED", "FIX_VERIFIED", "PR_READY", "BLOCKED",
}


def validate(ticket, state):
    fields = {"schemaVersion", "ticket", "stage", "targetSha", "requirementsHash"}
    if not isinstance(state, dict) or state.keys() != fields:
        raise ValueError("チェックポイントの項目が不正です。")
    if type(state["schemaVersion"]) is not int or state["schemaVersion"] != 1:
        raise ValueError("未対応のスキーマ版です。")
    if state["ticket"] != ticket or not isinstance(state["stage"], str) or state["stage"] not in STATES:
        raise ValueError("チケットまたは工程が不正です。")
    for field, pattern in (("targetSha", r"[0-9a-f]{40}"), ("requirementsHash", r"[0-9a-f]{64}")):
        value = state[field]
        if not isinstance(value, str) or not re.fullmatch(pattern, value):
            raise ValueError(f"{field} が不正です。")


class Checkpoint:
    def __init__(self, connection, ticket):
        self.connection = connection
        self.ticket = ticket

    def load(self):
        row = self.connection.execute("SELECT payload FROM checkpoint WHERE id = 1").fetchone()
        if row is None:
            return None
        state = json.loads(row[0])
        validate(self.ticket, state)
        return state

    def save(self, state):
        validate(self.ticket, state)
        self.load()
        self.connection.execute(
            "INSERT OR REPLACE INTO checkpoint (id, payload) VALUES (1, ?)",
            (json.dumps(state, ensure_ascii=False, sort_keys=True),),
        )


@contextmanager
def checkpoint_transaction(directory, ticket):
    """ロックを保持したまま読み取り、検証、更新を行う。"""
    if not re.fullmatch(r"TMGR-[1-9][0-9]*", ticket):
        raise ValueError("TMGRチケットキーが不正です。")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(directory / f"{ticket}.sqlite3", timeout=0)) as connection:
        connection.execute("PRAGMA synchronous = FULL")
        with connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                "CREATE TABLE IF NOT EXISTS checkpoint ("
                "id INTEGER PRIMARY KEY CHECK (id = 1), payload TEXT NOT NULL)"
            )
            yield Checkpoint(connection, ticket)
