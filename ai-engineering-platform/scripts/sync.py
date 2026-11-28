"""AEPの正本を検証し、Antigravity用の配置を生成する。"""

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
PLATFORM = ROOT / "ai-engineering-platform"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def expected_files():
    config = read_json(ROOT / ".aep/project.yaml")
    if config != {
        "stack": "flutter", "project_config": "project-config", "generated_dir": ".agents"
    }:
        raise ValueError("未対応のプロジェクト設定")
    version = (PLATFORM / "VERSION").read_text(encoding="utf-8").strip()
    if read_json(ROOT / ".aep/platform.lock") != {"version": version}:
        raise ValueError("基盤バージョンがロックと一致しない")
    overrides = read_json(ROOT / "project-config/quality-overrides.json")
    if not isinstance(overrides, dict) or set(overrides) != {"additional_required"}:
        raise ValueError("製品設定は必須ゲートの追加のみ可能")
    additional = overrides["additional_required"]
    if not isinstance(additional, list) or any(
        not isinstance(item, str) or not item.strip() for item in additional
    ):
        raise ValueError("必須ゲートの追加設定が不正")
    stack = PLATFORM / "stacks/flutter"
    required = read_json(stack / "quality-gates.json")["required"]
    if not isinstance(required, list) or not {
        "dart-format", "flutter-analyze", "flutter-test", "android-build"
    }.issubset(required):
        raise ValueError("Flutterの必須ゲートが不足")

    result = {}
    for source in (PLATFORM / "core", stack, ROOT / "project-config"):
        for pattern in ("skills/*/SKILL.md", "rules/*.md"):
            for path in sorted(source.glob(pattern)):
                relative = path.relative_to(source)
                if relative in result:
                    raise ValueError(f"配置先が重複: {relative}")
                content = path.read_text(encoding="utf-8")
                if relative.parts[0] == "skills" and not content.startswith(
                    f"---\nname: {relative.parts[1]}\ndescription: "
                ):
                    raise ValueError(f"Skillのメタデータが不正: {path}")
                result[relative] = content.encode("utf-8")
    catalog = read_json(PLATFORM / "catalog.json")
    listed = {item["name"] for item in catalog if item["status"] == "initial"}
    installed = {path.parts[1] for path in result if path.parts[0] == "skills"}
    if listed != installed or len({item["name"] for item in catalog}) != 26:
        raise ValueError("カタログと配置対象が一致しない")
    return result


def sync(check):
    expected = expected_files()
    destination = ROOT / ".agents"
    existing = {
        path.relative_to(destination)
        for pattern in ("skills/**/*", "rules/**/*")
        for path in destination.glob(pattern)
        if path.is_file()
    }
    extra = existing - expected.keys()
    if extra:
        raise ValueError("生成領域に未管理のファイル: " + ", ".join(map(str, sorted(extra))))
    changed = []
    for relative, content in sorted(expected.items()):
        target = destination / relative
        if target.is_file() and target.read_bytes().replace(b"\r\n", b"\n") == content:
            continue
        changed.append(str(relative))
        if not check:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
    if check and changed:
        raise ValueError("生成差分: " + ", ".join(changed))
    print(f"配置対象 {len(expected)} 件、差分 {len(changed)} 件")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="書き込まず差分を検証する")
    try:
        sync(parser.parse_args().check)
    except (OSError, ValueError, TypeError, KeyError) as error:
        sys.exit(str(error))
