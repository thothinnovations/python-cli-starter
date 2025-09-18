"""
cli.py — Minimal CLI app (pure Python)

Usage:
  python cli.py --help
  python cli.py run
  python cli.py status
"""
import argparse
import json
import logging
import sys
from typing import Optional, cast, List, Dict, Any

import commands  # noqa: F401 (this will populate and register the commands)
from internals.config import APP_NAME, APP_VERSION, DISPLAY_NAME, DESCRIPTION
from internals.decorator import COMMAND_REGISTRY


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def cmd_status(_: argparse.Namespace) -> int:
    status = {
        "APP_NAME": APP_NAME,
        "APP_VERSION": APP_VERSION,
        "DISPLAY_NAME": DISPLAY_NAME,
        "DESCRIPTION": DESCRIPTION,
        "COMMAND_REGISTRY": sorted(COMMAND_REGISTRY.keys()),
    }
    print(json.dumps(status, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=APP_NAME,
        description=DESCRIPTION,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # Built-ins
    p_status = sub.add_parser("status", help="Show current configuration.")
    p_status.set_defaults(func=cmd_status)

    # Dynamic commands from the registry
    for cmd_name, meta in COMMAND_REGISTRY.items():
        p = sub.add_parser(cmd_name, help=str(meta.get("help", "")))
        args_list = cast(List[Dict[str, Any]], meta.get("arguments", []))
        for arg in args_list:
            if "flags" in arg:
                p.add_argument(*arg["flags"], **arg.get("kwargs", {}))
            else:
                p.add_argument(arg["name"], **arg.get("kwargs", {}))
        p.set_defaults(func=meta["func"])

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    setup_logging()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except KeyboardInterrupt:
        logging.getLogger(APP_NAME).warning("Interrupted by user.")
        return 130
    except Exception as e:
        logging.getLogger(APP_NAME).exception("Unhandled error: %s", e)
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
