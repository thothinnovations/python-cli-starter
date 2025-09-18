from typing import Callable, Dict, List, Optional

# Each entry can optionally include an "arguments" or "flags" list for argparse
COMMAND_REGISTRY: Dict[str, Dict[str, object]] = {}

def cli_command(*, name: str, help: str, arguments: Optional[List[dict]] = None):  # noqa for `help` argument name
    """
    Decorator to register a function as a CLI command.

    `arguments` is an optional list of argparse specs.
    Each item can be either:
      - {"name": "person", "kwargs": {"help": "...", "type": str}}     # positional
      - {"flags": ["-p", "--person"], "kwargs": {"help": "...", "required": True}}  # option(s)

    Example:
        @cli_command(
            name="greet",
            help="Greet a person with age.",
            arguments=[
                {"name": "person", "kwargs": {"help": "Person's name", "type": str}},
                {"name": "age", "kwargs": {"help": "Age in years", "type": int}},
            ],
        )
        def greet(args) -> int:
            print(f"Hello, {args.person}! You are {args.age} years old!!!")
            return 0
    """
    def decorator(func: Callable):
        COMMAND_REGISTRY[name] = {"func": func, "help": help, "arguments": arguments or []}
        return func
    return decorator
