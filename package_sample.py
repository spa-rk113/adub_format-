#!/usr/bin/env python3
"""Package examples/anime-scene.json as a ZIP-based .adub sample."""
import json
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = root / "examples" / "anime-scene.json"
output = root / "examples" / "anime-scene.adub"
data = json.loads(source.read_text(encoding="utf-8"))
with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
    archive.writestr("project.json", json.dumps(data, ensure_ascii=False, indent=2) + "\n")
print(f"Created {output}")
