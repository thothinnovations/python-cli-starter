# CLI Starter

A tiny Python CLI scaffold that **auto-discovers commands** via a decorator.  
Drop functions into `commands/`, annotate them with `@cli_command(...)`, and they’re registered automatically.

> Requires **Python 3.12 or later**.

---

## Project Layout

```
cli-starter/
├─ cli.py
├─ commands/
│  ├─ __init__.py
│  ├─ hello_world.py
│  ├─ greet_with_positional.py
│  └─ greet_with_flags.py
└─ internals/
   ├─ config.py
   └─ decorator.py
```

- `internals/config.py` – app constants (name, version, display name, description)
- `internals/decorator.py` – the decorator + registry used by `cli.py`
- `commands/` – command modules that call the decorator (imported for side effects)
- `cli.py` – sets up logging/argparse, imports `commands`, and wires everything up

---

## Quick Start

1) Ensure **Python 3.12+** is installed and on your PATH.
2) From the project root, run the CLI as you like:
    - `py -m cli hello` or
    - `python cli.py hello` or
    - `python3 cli.py hello`

#### Expected outputs (examples):

```
> py -m cli hello
Hello World!!!
```

```
> py -m cli greet Bob 42
Hello, Bob! You are 42 years old!!!
```

```
> py -m cli greet-flags -p Alice -a 30
Hello, Alice! You are 30 years old!!!
```

```
> py -m cli greet-flags --person Bob --age 25 --excited
HELLO, BOB! YOU ARE 25 YEARS OLD!!!
```

---

## Adding Your Own Commands

1- Create a new file in `commands/` like `my_command.py` and:
   - import the decorator: `from internals.decorator import cli_command`
   - create a function that accepts a single `(args)` argument and **returns an integer** (an exit code).  

2- Import your function in `commands/__init__.py` so the CLI loads it:
```python
from .my_command import my_function
```

3- Choose one of the options below to decorate your function with `@cli_command`:

### Option A) Using Positional Arguments

**Example `commands/greet_pet.py`:**
```python
from internals.decorator import cli_command

@cli_command(
    name="greet-pet",
    help="Greet a pet by name and species (positional).",
    arguments=[
        {"name": "name", "kwargs": {"help": "Pet's name", "type": str}},
        {"name": "species", "kwargs": {"help": "Pet's species", "type": str}},
    ],
)
def greet_pet(args) -> int:
    print(f"Nice to meet you, {args.name} the {args.species}!")
    return 0  # Ensure the function returns an integer
```
> Remember to add `from . import greet_pet` in `commands/__init__.py` so the module is imported.

**Usage example:**
```
> py -m cli greet-pet Coco parrot
Nice to meet you, Coco the parrot!
```


### Option B) Using Flag Arguments

**Example `commands/say.py`:**
```python
from internals.decorator import cli_command

@cli_command(
    name="say",
    help="Say a message a number of times (flags).",
    arguments=[
        {"flags": ["-m", "--message"], "kwargs": {"help": "Message to print", "type": str, "required": True}},
        {"flags": ["-n", "--times"], "kwargs": {"help": "How many times", "type": int, "default": 1}},
        {"flags": ["-e", "--excited"], "kwargs": {"help": "Make it ALL CAPS", "action": "store_true"}},
    ],
)
def say(args) -> int:
    msg = args.message.upper() if args.excited else args.message
    for _ in range(args.times):
        print(msg)
    return 0  # Ensure the function returns an integer
```
> Remember to add `from . import say` in `commands/__init__.py` so the module is imported.

**Usage example:**
```
> py -m cli say -m "hi"
hi
```

```
> py -m cli say -m "hi" -n 3 --excited
HI
HI
HI
```

---

## How the `@cli_command` decorator works?

### 1) The Decorator & Registry

`internals/decorator.py` exposes a decorator and a global registry:

```python
from typing import Callable, Dict, List, Optional

COMMAND_REGISTRY: Dict[str, Dict[str, object]] = {}

def cli_command(*, name: str, help: str, arguments: Optional[List[dict]] = None):
    def decorator(func: Callable):
        COMMAND_REGISTRY[name] = {
            "func": func,
            "help": help,
            "arguments": arguments or [],
        }
        return func
    return decorator
```

Each command is a function annotated with `@cli_command(...)`. When its module is imported, the decorator runs and stores metadata in `COMMAND_REGISTRY`.

### 2) Auto-wiring in `cli.py`

`cli.py` imports `commands` (which imports each command module) so the decorators execute, then loops over `COMMAND_REGISTRY` to create subparsers and attach handlers.

```python
from typing import Any, Dict, List, cast

for cmd_name, meta in COMMAND_REGISTRY.items():
    p = sub.add_parser(cmd_name, help=str(meta.get("help", "")))
    args_list = cast(List[Dict[str, Any]], meta.get("arguments", []))
    for arg in args_list:
        if "flags" in arg:
            p.add_argument(*arg["flags"], **arg.get("kwargs", {}))
        else:
            p.add_argument(arg["name"], **arg.get("kwargs", {}))
    p.set_defaults(func=meta["func"])
```

---

## Built-in Commands
  
#### `-h` or `--help` — shows app help with loaded commands:
```
> py -m cli -h
usage: cli [-h] {status,hello,greet,greet-flags} ...

A minimal CLI application with dynamically loaded commands.

positional arguments:
  {status,hello,greet,greet-flags}
    status              Show current configuration.
    hello               Prints a hello world message.
    greet               Greets a {person} with their {age}. (USAGE: `greet Bob 42`)
    greet-flags         Greets a person using flags for name and age.

options:
  -h, --help            show this help message and exit
```

<br/>

#### `status` — shows app config and the list of loaded commands:
```
> py -m cli status
{
  "APP_VERSION": "0.3.0",
  "APP_NAME": "myapp",
  "DISPLAY_NAME": "Dynamic CLI Application",
  "dynamic_commands": [
    "greet",
    "greet-flags",
    "hello"
  ]
}
```

---

## App Configuration

`internals/config.py` centralizes the app constants:

```python
APP_NAME = "cli"
APP_VERSION = "0.3.0"
DISPLAY_NAME = "Dynamic CLI Application"
DESCRIPTION = "A minimal CLI application with dynamically loaded commands."
```

---

## Packaging (optional)

You can turn this into an installable package with a console script:

1. Add a `pyproject.toml`:

```toml
[project]
name = "cli-starter"
version = "0.1.0"
requires-python = ">=3.12"

[project.scripts]
cli-starter = "cli:main"
```

2. Install locally:
```
pip install -e .
cli-starter status
```

---

## License

MIT
