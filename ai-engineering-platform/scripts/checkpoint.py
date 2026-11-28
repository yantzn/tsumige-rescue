"""チケット単位のチェックポイントを保存する。"""

import argparse
from contextlib import closing, contextmanager
import json
from pathlib import Path
import re
import sqlite3
import sys


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

    def resume(self, target_sha, requirements_hash):
        state = self.load()
        if state is None:
            raise ValueError("再開できるチェックポイントがありません。")
        if state["targetSha"] != target_sha or state["requirementsHash"] != requirements_hash:
            raise ValueError("対象SHAまたは要件ハッシュが保存済みの証跡と一致しません。")
        return state

    def reserve_pr(self, target_sha, requirements_hash):
        state = self.resume(target_sha, requirements_hash)
        if state["stage"] != "PR_READY":
            raise ValueError("PR_READYの証跡がありません。")
        if self.connection.execute("SELECT 1 FROM pr_reservation WHERE id = 1").fetchone():
            raise ValueError("PR作成の予約済みです。既存PRと実行履歴を確認してください。")
        self.connection.execute("INSERT INTO pr_reservation (id) VALUES (1)")


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
            connection.execute(
                "CREATE TABLE IF NOT EXISTS pr_reservation (id INTEGER PRIMARY KEY CHECK (id = 1))"
            )
            yield Checkpoint(connection, ticket)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("save", "resume", "reserve-pr"))
    parser.add_argument("ticket")
    parser.add_argument("--directory", default=".agent-state")
    parser.add_argument("--target-sha", required=True)
    parser.add_argument("--requirements-hash", required=True)
    parser.add_argument("--stage", choices=sorted(STATES))
    args = parser.parse_args()
    try:
        result = {"status": "PASS"}
        with checkpoint_transaction(args.directory, args.ticket) as checkpoint:
            if args.operation == "save":
                checkpoint.save({
                    "schemaVersion": 1, "ticket": args.ticket, "stage": args.stage,
                    "targetSha": args.target_sha, "requirementsHash": args.requirements_hash,
                })
            elif args.operation == "resume":
                result["checkpoint"] = checkpoint.resume(args.target_sha, args.requirements_hash)
            else:
                checkpoint.reserve_pr(args.target_sha, args.requirements_hash)
        print(json.dumps(result))
        return 0
    except (OSError, ValueError, sqlite3.Error) as error:
        print(str(error), file=sys.stderr)
        print(json.dumps({"status": "BLOCKED"}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
