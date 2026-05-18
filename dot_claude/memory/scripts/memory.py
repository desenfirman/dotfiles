#!/usr/bin/env python3
"""
memory.py — MemPalace Spatial retrieval script (stdlib only)
Usage:
  python3 memory.py recall --wing <wing> --room <room> [--hall <hall>]
  python3 memory.py search --keyword <keyword> [--wing <wing>]
  python3 memory.py wake_up --wing <wing>
  python3 memory.py list --wing <wing> [--room <room>]
  python3 memory.py tunnel --file <relative_path>
"""

import argparse
import json
import re
import sys
from pathlib import Path

MEMORY_ROOT = Path(__file__).parent.parent  # ~/.claude/memory/
VALID_HALLS = {"hall_facts", "hall_events", "hall_discoveries", "hall_preferences", "hall_advice"}
MAX_CONTENT_LINES = 30  # per drawer, prevent prompt flooding


# ─── Helpers ───────────────────────────────────────────────────────────────

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Extract YAML-style frontmatter and body from a markdown file."""
    meta = {}
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    k, _, v = line.partition(":")
                    raw = v.strip()
                    # parse refs list: [a, b] or []
                    if raw.startswith("[") and raw.endswith("]"):
                        inner = raw[1:-1].strip()
                        meta[k.strip()] = [x.strip() for x in inner.split(",") if x.strip()]
                    else:
                        meta[k.strip()] = raw
            body = parts[2].strip()
    return meta, body


def read_drawer(path: Path) -> dict:
    """Read a single drawer file, return dict with meta + body."""
    text = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)
    lines = body.splitlines()
    if len(lines) > MAX_CONTENT_LINES:
        body = "\n".join(lines[:MAX_CONTENT_LINES]) + f"\n... [{len(lines) - MAX_CONTENT_LINES} lines truncated]"
    return {"path": str(path.relative_to(MEMORY_ROOT)), "meta": meta, "body": body}


def resolve_wing_path(wing: str) -> list[Path]:
    """Return all matching wing dirs for a given name, checking both prv and pub prefixes."""
    if wing is None:
        return sorted(MEMORY_ROOT.glob("wing_*"))
    candidates = [
        MEMORY_ROOT / f"wing_{wing}",
        MEMORY_ROOT / f"wing_pub_{wing}",
    ]
    return [p for p in candidates if p.exists()]


def wing_visibility(path: Path) -> str:
    """Return 'public' or 'private' based on wing dir name prefix."""
    return "public" if path.name.startswith("wing_pub_") else "private"


def find_drawers(wing: str = None, room: str = None, hall: str = None) -> list[Path]:
    """Glob drawers based on wing/room/hall filters. Transparent to pub/prv prefix."""
    room_pat = f"room_{room}" if room else "room_*"
    hall_pat = hall if hall else "*"
    results = []
    if wing is None:
        # search all wings regardless of visibility
        results = sorted(MEMORY_ROOT.glob(f"wing_*/{room_pat}/{hall_pat}/*.md"))
    else:
        for wing_path in resolve_wing_path(wing):
            results.extend(wing_path.glob(f"{room_pat}/{hall_pat}/*.md"))
        results = sorted(results)
    return results


def format_drawer(d: dict) -> str:
    meta = d["meta"]
    out = [f"### [{d['path']}]"]
    if meta:
        out.append(f"date: {meta.get('date', '?')} | hall: {meta.get('hall', '?')}")
    out.append(d["body"])
    return "\n".join(out)


# ─── Commands ──────────────────────────────────────────────────────────────

def cmd_recall(args):
    """Retrieve drawers by wing/room/hall — addressed recall."""
    files = find_drawers(wing=args.wing, room=args.room, hall=args.hall)
    if not files:
        print(f"[memory] No drawers found for wing={args.wing} room={args.room} hall={args.hall}")
        return
    print(f"[memory] recall: {len(files)} drawer(s) found\n")
    for f in files:
        d = read_drawer(f)
        print(format_drawer(d))
        print()


def cmd_search(args):
    """Keyword grep across memory — blind retrieval fallback."""
    scope = find_drawers(wing=args.wing)
    if not scope:
        print("[memory] No drawers to search.")
        return
    keyword = args.keyword.lower()
    hits = []
    for f in scope:
        text = f.read_text(encoding="utf-8")
        if keyword in text.lower():
            hits.append(f)
    if not hits:
        print(f"[memory] No results for '{args.keyword}'")
        return
    print(f"[memory] search '{args.keyword}': {len(hits)} hit(s)\n")
    for f in hits:
        d = read_drawer(f)
        # highlight matched lines
        highlighted = []
        for line in d["body"].splitlines():
            if keyword in line.lower():
                highlighted.append(f"  >> {line}")
        d["body"] = "\n".join(highlighted) if highlighted else d["body"]
        print(format_drawer(d))
        print()


def cmd_wake_up(args):
    """L0 identity + top facts from a wing — session warm-up."""
    identity = MEMORY_ROOT / "identity.md"
    if identity.exists():
        print("=== IDENTITY (L0) ===")
        print(identity.read_text(encoding="utf-8"))
        print()

    facts = find_drawers(wing=args.wing, hall="hall_facts")
    if facts:
        print(f"=== TOP FACTS: wing_{args.wing} ({len(facts)} drawer(s)) ===")
        for f in facts[:10]:  # cap at 10 for token budget
            d = read_drawer(f)
            print(format_drawer(d))
            print()
    else:
        print(f"[memory] No facts found for wing={args.wing}")


def cmd_list(args):
    """List available wings, rooms, or halls."""
    if args.room:
        wing_paths = resolve_wing_path(args.wing) if args.wing else []
        if not wing_paths:
            print(f"[memory] Wing not found: {args.wing}")
            return
        for wing_path in wing_paths:
            room_path = wing_path / f"room_{args.room}"
            if not room_path.exists():
                print(f"[memory] Room not found: {room_path}")
                continue
            vis = wing_visibility(wing_path)
            halls = [p.name for p in sorted(room_path.iterdir()) if p.is_dir()]
            print(f"Halls in {wing_path.name}/room_{args.room} [{vis}]:")
            for hall in halls:
                drawers = list((room_path / hall).glob("*.md"))
                print(f"  {hall}/  ({len(drawers)} drawer(s))")
    elif args.wing:
        wing_paths = resolve_wing_path(args.wing)
        if not wing_paths:
            print(f"[memory] Wing not found: {args.wing}")
            return
        for wing_path in wing_paths:
            vis = wing_visibility(wing_path)
            rooms = [p.name for p in sorted(wing_path.iterdir()) if p.is_dir()]
            print(f"Rooms in {wing_path.name} [{vis}]: {rooms}")
    else:
        # list all wings with visibility flag
        wings = [p for p in sorted(MEMORY_ROOT.iterdir())
                 if p.is_dir() and p.name.startswith("wing_")]
        if wings:
            print("Wings:")
            for w in wings:
                vis = wing_visibility(w)
                rooms = [p.name for p in w.iterdir() if p.is_dir()]
                print(f"  {w.name}  [{vis}]  ({len(rooms)} room(s))")
        else:
            print("[memory] No wings found. Memory is empty.")


def cmd_publish(args):
    """Mark a wing as public (rename wing_{name} → wing_pub_{name})."""
    src = MEMORY_ROOT / f"wing_{args.wing}"
    dst = MEMORY_ROOT / f"wing_pub_{args.wing}"
    if dst.exists():
        print(f"[memory] Wing already public: wing_pub_{args.wing}")
        return
    if not src.exists():
        print(f"[memory] Wing not found: wing_{args.wing}")
        return
    src.rename(dst)
    print(f"[memory] Published: wing_{args.wing} → wing_pub_{args.wing}")
    print(f"  Run 'chezmoi add ~/.claude/memory/wing_pub_{args.wing}' to track it.")


def cmd_unpublish(args):
    """Mark a wing as private (rename wing_pub_{name} → wing_{name})."""
    src = MEMORY_ROOT / f"wing_pub_{args.wing}"
    dst = MEMORY_ROOT / f"wing_{args.wing}"
    if dst.exists():
        print(f"[memory] Private wing already exists: wing_{args.wing}")
        return
    if not src.exists():
        print(f"[memory] Public wing not found: wing_pub_{args.wing}")
        return
    src.rename(dst)
    print(f"[memory] Unpublished: wing_pub_{args.wing} → wing_{args.wing}")
    print(f"  Run 'chezmoi forget ~/.claude/memory/wing_pub_{args.wing}' if it was tracked.")


def cmd_tunnel(args):
    """Follow refs[] links from a drawer — tunnel traversal."""
    target = MEMORY_ROOT / args.file
    if not target.exists():
        print(f"[memory] File not found: {args.file}")
        return
    d = read_drawer(target)
    refs = d["meta"].get("refs", [])
    if not refs:
        print(f"[memory] No tunnel refs in {args.file}")
        return
    print(f"[memory] Tunnel from {args.file} → {len(refs)} ref(s)\n")
    for ref in refs:
        ref_path = MEMORY_ROOT / ref
        if ref_path.exists():
            rd = read_drawer(ref_path)
            print(format_drawer(rd))
            print()
        else:
            print(f"  [broken tunnel] {ref} — file not found")


# ─── CLI ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="MemPalace memory retrieval (stdlib only)")
    sub = parser.add_subparsers(dest="cmd")

    p_recall = sub.add_parser("recall")
    p_recall.add_argument("--wing", required=True)
    p_recall.add_argument("--room", required=True)
    p_recall.add_argument("--hall", choices=list(VALID_HALLS), default=None)

    p_search = sub.add_parser("search")
    p_search.add_argument("--keyword", required=True)
    p_search.add_argument("--wing", default=None)

    p_wake = sub.add_parser("wake_up")
    p_wake.add_argument("--wing", required=True)

    p_list = sub.add_parser("list")
    p_list.add_argument("--wing", default=None)
    p_list.add_argument("--room", default=None)

    p_tunnel = sub.add_parser("tunnel")
    p_tunnel.add_argument("--file", required=True,
                          help="Relative path from memory root, e.g. wing_x/room_y/hall_facts/file.md")

    p_publish = sub.add_parser("publish", help="Mark a wing as public (safe to commit)")
    p_publish.add_argument("--wing", required=True, help="Wing name without prefix, e.g. 'data-eng'")

    p_unpublish = sub.add_parser("unpublish", help="Mark a wing as private (exclude from commit)")
    p_unpublish.add_argument("--wing", required=True, help="Wing name without prefix, e.g. 'data-eng'")

    args = parser.parse_args()
    dispatch = {
        "recall": cmd_recall,
        "search": cmd_search,
        "wake_up": cmd_wake_up,
        "list": cmd_list,
        "tunnel": cmd_tunnel,
        "publish": cmd_publish,
        "unpublish": cmd_unpublish,
    }
    if args.cmd not in dispatch:
        parser.print_help()
        sys.exit(1)
    dispatch[args.cmd](args)


if __name__ == "__main__":
    main()
