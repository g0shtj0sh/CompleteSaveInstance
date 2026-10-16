"""Check published documentation routes and API coverage after a Moonwave build."""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"


class Text(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def main() -> int:
    required = (
        "index.html", "api/CompleteSaveInstance/index.html", "docs/intro/index.html",
        "docs/PRESETS/index.html", "docs/OPTIONS/index.html", "docs/USAGE/index.html", "docs/TROUBLESHOOTING/index.html",
        "docs/ARCHITECTURE/index.html", "docs/ROADMAP/index.html", "changelog/index.html", "logo.png", "favicon.png",
    )
    errors = [f"Missing built route or asset: {name}" for name in required if not (BUILD / name).is_file()]
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    api = Text()
    api.feed((BUILD / "api/CompleteSaveInstance/index.html").read_text(encoding="utf-8"))
    api_text = " ".join(api.parts)
    source = (ROOT / "saveinstance.luau").read_text(encoding="utf-8")
    options_section = source.split("--- @interface CustomOptions table", 1)[1].split("--- @interface OptionsAliases", 1)[0]
    options = re.findall(r"^--- (?:@field |\.)(\w+) ", options_section, re.MULTILINE)
    for name in options:
        if name not in api_text:
            errors.append(f"Option missing from generated API: {name}")

    catalog = json.loads((ROOT / "Script Presets/presets.json").read_text(encoding="utf-8"))
    presets_page = (BUILD / "docs/PRESETS/index.html").read_text(encoding="utf-8")
    home = (BUILD / "index.html").read_text(encoding="utf-8")
    for preset in catalog["presets"]:
        if preset["id"] not in presets_page:
            errors.append(f"Preset missing from website: {preset['id']}")
    if catalog["developmentTarget"] not in home:
        errors.append("Homepage does not identify the current development target")
    if not list(BUILD.glob("*search-doc*.json")) or not list(BUILD.glob("*lunr-index*.json")):
        errors.append("Search document/index files are missing")
    else:
        search = (BUILD / "search-doc.json").read_text(encoding="utf-8")
        for name in options:
            if name not in search:
                errors.append(f"Option missing from searchable documents: {name}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Documentation build checked: {len(required)} routes/assets, {len(options)} API options, {len(catalog['presets'])} presets, search indexes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
