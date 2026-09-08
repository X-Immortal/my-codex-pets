#!/usr/bin/env python3
"""Portable, dependency-free Codex pet installation and export (Python 3.9+)."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import time

ROOT = Path(__file__).resolve().parent


def bundles(root, names):
    if not root.is_dir():
        raise ValueError(f"Pet directory not found: {root}")
    result = {}
    for folder in sorted(root.iterdir()):
        if not folder.is_dir() or (names and folder.name not in names):
            continue
        if folder.is_symlink() or not re.fullmatch(r"[a-zA-Z0-9_-]+", folder.name):
            raise ValueError(f"Unsafe pet directory: {folder}")
        manifest = folder / "pet.json"
        if not manifest.exists():
            continue
        data = json.loads(manifest.read_text(encoding="utf-8-sig"))
        if data.get("id") != folder.name or not data.get("displayName"):
            raise ValueError(f"Invalid id/displayName: {manifest}")
        if data.get("spriteVersionNumber", 1) not in (1, 2):
            raise ValueError(f"Unsupported sprite version: {manifest}")
        sprite = data.get("spritesheetPath", "")
        if not isinstance(sprite, str) or not sprite or "\\" in sprite:
            raise ValueError(f"Invalid spritesheetPath: {manifest}")
        relative = Path(sprite)
        if relative.is_absolute() or ".." in relative.parts or ":" in sprite:
            raise ValueError(f"Unsafe spritesheetPath: {manifest}")
        files = [manifest, folder / relative]
        for file in files:
            if not file.is_file() or not file.resolve().is_relative_to(folder.resolve()):
                raise ValueError(f"Missing or external pet asset: {file}")
            if any(p.is_symlink() for p in [file, *file.parents] if p != root.parent):
                raise ValueError(f"Symlink not supported: {file}")
        result[folder.name] = (data, {str(f.relative_to(folder)): f for f in files})
    missing = set(names or []) - result.keys()
    if missing:
        raise ValueError(f"Unknown pets: {', '.join(sorted(missing))}")
    if not result:
        raise ValueError(f"No pets found in {root}")
    return result


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transfer(source, destination, names, replace, dry_run):
    items = bundles(source, names)
    changes = []
    for name, (_, files) in items.items():
        target = destination / name
        if target.is_symlink() or (target.exists() and not target.is_dir()):
            raise ValueError(f"Unsafe destination: {target}")
        if target.exists() and all((target / rel).is_file() and digest(src) == digest(target / rel)
                                   for rel, src in files.items()):
            print(f"unchanged: {name}")
            continue
        if target.exists() and not replace:
            raise ValueError(f"Conflict: {name}. Review differences, then use --replace to back up and replace.")
        changes.append((name, files, target))
    # Preflight every conflict before writing anything.
    for name, files, target in changes:
        print(f"{'would copy' if dry_run else 'copy'}: {name} -> {target}")
        if dry_run:
            continue
        destination.mkdir(parents=True, exist_ok=True)
        if target.exists():
            backup = destination.parent / "pet-backups" / (str(time.time_ns()) + "-" + name)
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(target, backup)
            print(f"backup: {backup}")
        for relative, src in files.items():
            dest = target / relative
            if dest.is_symlink() or any(p.is_symlink() for p in dest.parents):
                raise ValueError(f"Symlink destination: {dest}")
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            if digest(src) != digest(dest):
                raise ValueError(f"Copy verification failed: {dest}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["list", "validate", "install", "export"])
    parser.add_argument("names", nargs="*", help="Pet ids; omit for all pets")
    parser.add_argument("--codex-home", type=Path, default=Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex"))
    parser.add_argument("--replace", action="store_true", help="Back up conflicting destination files before replacing")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    local = args.codex_home.expanduser().resolve() / "pets"
    repository = ROOT / "pets"
    if args.action in ("list", "validate"):
        for name, (data, files) in bundles(repository, args.names).items():
            print(f"{name}: {data['displayName']} (v{data.get('spriteVersionNumber', 1)})")
            if args.action == "validate":
                for relative, file in files.items():
                    print(f"  {digest(file)}  {name}/{relative}")
    elif args.action == "install":
        transfer(repository, local, args.names, args.replace, args.dry_run)
    else:
        transfer(local, repository, args.names, args.replace, args.dry_run)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        sys.exit(f"Error: {error}")
