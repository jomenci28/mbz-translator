#!/usr/bin/env python3
"""Helpers para extraer y reempaquetar Moodle MBZ.

Uso típico desde una sesión de traducción:

    python3 mbz_tools.py extract /ruta/al.mbz /tmp/curso/
    # ...edita los XML extraídos...
    python3 mbz_tools.py pack /tmp/curso/ /ruta/al_traducido.mbz

`extract` deja además una copia de `.ARCHIVE_INDEX` en `<dest>/.ARCHIVE_INDEX.orig`
para preservar el orden y los timestamps originales.

`pack` regenera `.ARCHIVE_INDEX` con los tamaños actuales antes de comprimir, así
Moodle no se queja al importar.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


S3_IMAGES_BASE = "https://robotixc360-content.s3.eu-south-2.amazonaws.com/imagenes"
# Files we should never rewrite: structural / binary content.
RELOCALIZE_SKIP = {".ARCHIVE_INDEX", ".ARCHIVE_INDEX.orig"}


def cmd_relocalize_images(args: argparse.Namespace) -> int:
    """Force every workspace_<id>_<lang>.png reference to the target language.

    Applies two rewrites:
      1. Any S3 URL `…/imagenes/workspace_<id>_<lang>.png` → same URL but with
         `_<target>.png`.
      2. Any Moodle `@@PLUGINFILE@@/workspace_<id>_<lang>.png` → the full S3 URL
         `<S3_IMAGES_BASE>/workspace_<id>_<target>.png`.

    Reasoning: ROBOTIX hosts a per-language copy of each workspace screenshot
    on S3 (`_en`, `_es`, `_ca`, …). When we localize a course we want the
    Spanish images to show, regardless of how the original markup referenced
    them.
    """
    root = Path(args.root).resolve()
    target = args.target

    s3_pattern = re.compile(
        r"(https?://[^/\s\"']+/imagenes/workspace_)(\d+)_[a-z]{2,5}(\.png)"
    )
    plugin_pattern = re.compile(
        r"@@PLUGINFILE@@/+workspace_(\d+)_[a-z]{2,5}\.png"
    )

    s3_total = 0
    plugin_total = 0
    files_touched = 0
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.name in RELOCALIZE_SKIP:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        new, n_s3 = s3_pattern.subn(rf"\g<1>\g<2>_{target}\g<3>", text)
        new, n_plugin = plugin_pattern.subn(
            rf"{S3_IMAGES_BASE}/workspace_\1_{target}.png", new
        )
        if new != text:
            path.write_text(new, encoding="utf-8")
            files_touched += 1
            s3_total += n_s3
            plugin_total += n_plugin
            print(f"  {path.relative_to(root)}: {n_s3} S3, {n_plugin} PLUGINFILE")

    print(
        f"relocalize-images target={target}: "
        f"{files_touched} files, {s3_total} S3 URLs, {plugin_total} PLUGINFILE refs"
    )
    return 0


def cmd_extract(args: argparse.Namespace) -> int:
    src = Path(args.src).resolve()
    dest = Path(args.dest).resolve()
    if dest.exists():
        if args.force:
            shutil.rmtree(dest)
        else:
            print(f"refusing to overwrite {dest} (use --force)", file=sys.stderr)
            return 1
    dest.mkdir(parents=True)
    subprocess.run(["tar", "-xzf", str(src), "-C", str(dest)], check=True)

    archive_index = dest / ".ARCHIVE_INDEX"
    if archive_index.exists():
        shutil.copy2(archive_index, dest / ".ARCHIVE_INDEX.orig")
    print(f"extracted to {dest}")
    return 0


def _rebuild_archive_index(root: Path) -> None:
    orig = root / ".ARCHIVE_INDEX.orig"
    target = root / ".ARCHIVE_INDEX"
    if not orig.exists():
        print("no .ARCHIVE_INDEX.orig found - skipping index rebuild", file=sys.stderr)
        return

    with orig.open("r", encoding="utf-8") as fh:
        lines = fh.read().splitlines()

    new_entries: list[str] = []
    count = 0
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split("\t")
        count += 1
        if len(parts) != 4:
            new_entries.append(line)
            continue
        path, kind, _size, ts = parts
        if kind == "d":
            new_entries.append(line)
            continue
        fs_path = root / path
        if not fs_path.is_file():
            print(f"warning: {path} missing on disk", file=sys.stderr)
            new_entries.append(line)
            continue
        new_entries.append(f"{path}\t{kind}\t{fs_path.stat().st_size}\t{ts}")

    with target.open("w", encoding="utf-8") as fh:
        fh.write(f"Moodle archive file index. Count: {count}\n")
        fh.write("\n".join(new_entries) + "\n")


# Top-level entries we expect inside a Moodle 4.x MBZ.
TOP_LEVEL = [
    ".ARCHIVE_INDEX",
    "activities",
    "badges.xml",
    "completion.xml",
    "course",
    "files",
    "files.xml",
    "grade_history.xml",
    "gradebook.xml",
    "groups.xml",
    "moodle_backup.log",
    "moodle_backup.xml",
    "outcomes.xml",
    "questions.xml",
    "roles.xml",
    "scales.xml",
    "sections",
]


def cmd_pack(args: argparse.Namespace) -> int:
    src = Path(args.src).resolve()
    dest = Path(args.dest).resolve()
    if not src.is_dir():
        print(f"{src} is not a directory", file=sys.stderr)
        return 1

    _rebuild_archive_index(src)

    entries = [name for name in TOP_LEVEL if (src / name).exists()]
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        dest.unlink()

    # COPYFILE_DISABLE=1 + --no-mac-metadata avoid macOS appending AppleDouble
    # `._*` resource fork entries to the tar, which would inflate the file
    # count and trip Moodle's progress() guard ("value out of range") on
    # restore.
    env = {**os.environ, "COPYFILE_DISABLE": "1"}
    subprocess.run(
        [
            "tar",
            "-czf",
            str(dest),
            "--no-xattrs",
            "--no-mac-metadata",
            *entries,
        ],
        check=True,
        cwd=src,
        env=env,
    )
    print(f"packed -> {dest}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_extract = sub.add_parser("extract", help="Extract MBZ to a folder")
    p_extract.add_argument("src", help="Path to source .mbz")
    p_extract.add_argument("dest", help="Destination folder")
    p_extract.add_argument("--force", action="store_true", help="Overwrite dest")
    p_extract.set_defaults(func=cmd_extract)

    p_pack = sub.add_parser("pack", help="Repackage folder into MBZ")
    p_pack.add_argument("src", help="Folder containing extracted MBZ")
    p_pack.add_argument("dest", help="Output .mbz path")
    p_pack.set_defaults(func=cmd_pack)

    p_reloc = sub.add_parser(
        "relocalize-images",
        help="Rewrite workspace_<id>_<lang>.png refs to the target language",
    )
    p_reloc.add_argument("root", help="Folder with extracted MBZ")
    p_reloc.add_argument("--target", default="es", help="Target language code")
    p_reloc.set_defaults(func=cmd_relocalize_images)

    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
