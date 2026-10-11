#!/usr/bin/env python3
"""Validate a ZIP-based ADUB project file using Python's standard library."""

import json
import math
import sys
import zipfile
from pathlib import Path


def validate(path: Path) -> dict:
    if not path.is_file():
        raise ValueError(f"File not found: {path}")
    if not zipfile.is_zipfile(path):
        raise ValueError("The .adub file is not a valid ZIP archive.")

    with zipfile.ZipFile(path, "r") as archive:
        bad_file = archive.testzip()
        if bad_file:
            raise ValueError(f"Corrupted archive entry: {bad_file}")
        names = archive.namelist()
        if "project.json" not in names:
            raise ValueError("Missing project.json at the archive root.")
        try:
            data = json.loads(archive.read("project.json").decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"project.json is not valid UTF-8 JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("project.json must contain a JSON object.")

    required = ["format", "format_version", "project", "speakers", "scenes", "events"]
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")
    if data["format"] != "adub":
        raise ValueError("Invalid format identifier; expected 'adub'.")
    version = data["format_version"]
    if not isinstance(version, str) or not version.startswith("1."):
        raise ValueError(f"Unsupported format version: {version!r}")

    for key in ("speakers", "scenes", "events"):
        if not isinstance(data[key], list):
            raise ValueError(f"'{key}' must be a JSON array.")

    def valid_time(value):
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0

    speaker_ids = set()
    for i, speaker in enumerate(data["speakers"]):
        if not isinstance(speaker, dict):
            raise ValueError(f"speakers[{i}] must be an object.")
        sid = speaker.get("id")
        if not isinstance(sid, str) or not sid:
            raise ValueError(f"speakers[{i}] needs a non-empty string 'id'.")
        if sid in speaker_ids:
            raise ValueError(f"Duplicate speaker ID: {sid}")
        speaker_ids.add(sid)

    scene_ids = set()
    for i, scene in enumerate(data["scenes"]):
        if not isinstance(scene, dict):
            raise ValueError(f"scenes[{i}] must be an object.")
        sid = scene.get("id")
        if not isinstance(sid, str) or not sid:
            raise ValueError(f"scenes[{i}] needs a non-empty string 'id'.")
        if sid in scene_ids:
            raise ValueError(f"Duplicate scene ID: {sid}")
        scene_ids.add(sid)
        start, end = scene.get("start"), scene.get("end")
        if not valid_time(start) or not valid_time(end) or start > end:
            raise ValueError(f"scenes[{i}] has invalid start/end timestamps.")

    event_ids = set()
    for i, event in enumerate(data["events"]):
        if not isinstance(event, dict):
            raise ValueError(f"events[{i}] must be an object.")
        eid = event.get("id")
        if not isinstance(eid, str) or not eid:
            raise ValueError(f"events[{i}] needs a non-empty string 'id'.")
        if eid in event_ids:
            raise ValueError(f"Duplicate event ID: {eid}")
        event_ids.add(eid)
        start, end = event.get("start"), event.get("end")
        if not valid_time(start) or not valid_time(end) or start > end:
            raise ValueError(f"events[{i}] has invalid start/end timestamps.")
        speaker_id = event.get("speaker_id")
        if speaker_id is not None and speaker_id not in speaker_ids:
            raise ValueError(f"events[{i}] refers to unknown speaker ID: {speaker_id}")
        scene_id = event.get("scene_id")
        if scene_id is not None and scene_id not in scene_ids:
            raise ValueError(f"events[{i}] refers to unknown scene ID: {scene_id}")

    return {
        "format_version": version,
        "speakers": len(data["speakers"]),
        "scenes": len(data["scenes"]),
        "events": len(data["events"]),
        "archive_entries": len(names),
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python tools/validate_adub.py path/to/project.adub", file=sys.stderr)
        return 2
    try:
        result = validate(Path(sys.argv[1]))
    except (ValueError, OSError, KeyError, TypeError, zipfile.BadZipFile) as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 1
    print("ADUB package checks passed!")
    print(f"Format version: {result['format_version']}")
    print(f"Speakers: {result['speakers']}")
    print(f"Scenes: {result['scenes']}")
    print(f"Events: {result['events']}")
    print(f"Archive entries: {result['archive_entries']}")
    print("Note: structural checks only; this is not a full JSON Schema validator.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
