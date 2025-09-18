# CLI Starter

A tiny Python CLI scaffold that **auto-discovers commands** via a decorator.  
Drop functions into `commands/`, annotate them with `@cli_command(...)`, and they’re registered automatically.

> Requires **Python 3.12 or later**.

---

- [Project Layout](#project-layout)
- [Quick Start](#quick-start)
    - [Expected outputs (examples)](#expected-outputs-(examples):)

<br/>

- [Adding Your Own Commands](#adding-your-own-commands)
  - [Option A) Without Arguments](#[Option-A]-Without-Arguments)
  - [Option B) Using Positional Arguments](#option-b)-using-positional-arguments)
  - [Option C) Using Flag Arguments](#option-c)-using-flag-arguments)

<br/>

- [How the `@cli_command` decorator works?](#how-the-@cli_command-decorator-works)
- [Built-in Commands](#built-in-commands)
- [App Configuration](#app-configuration)
- [Packaging](#packaging-(optional))
- [License](#license)

---
<br/>


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
- `commands/__init__.py` – imports each command module so they are discovered
- `cli.py` – sets up logging/argparse, imports `commands`, and wires everything up

---
<br/>


## Quick Start

1) Ensure **Python 3.12+** is installed and on your PATH.
2) From the project root, run the CLI as you like:
    - `py -m cli hello` or
    - `python cli.py hello` or
    - `python3 cli.py hello`

#### Expected outputs (examples):

```
py -m cli hello
```
> Hello World!!!

```
py -m cli greet Bob 42
```
> Hello, Bob! You are 42 years old!!!

```
py -m cli greet-flags -p Alice -a 30
```
> Hello, Alice! You are 30 years old!!!

```
py -m cli greet-flags --person Bob --age 25 --excited
```
> HELLO, BOB! YOU ARE 25 YEARS OLD!!!

---
<br/>


## Adding Your Own Commands

1- Create a new file in `commands/` like `my_command.py` and:
   - import the decorator: `from internals.decorator import cli_command`
   - create a function that accepts a single `(args)` argument and **returns an integer** (an exit code).  

2- Import your function in `commands/__init__.py` so the CLI loads it:
```python
from .my_command import my_function
```

3- Choose one of the options below to decorate your function with `@cli_command`:

### [Option A] Without Arguments

**Example `commands/hello_world.py`:**
```python
from internals.decorator import cli_command

@cli_command(
    name="hello",
    help="Prints a hello world message."
)
def hello_world(args) -> int:
    print("Hello World!!!")
    return 0
```

**Usage example:**
```
py -m cli hello
```
> Hello World!!!


### [Option B] Using Positional Arguments

**Example `commands/greet_with_positional.py`:**
```python
@cli_command(
    name="greet",
    help="Greets a {person} with their {age}. (USAGE: `greet Bob 42`)",
    arguments=[
        {
            "name": "person",
            "kwargs": {
                "help": "Person's name",
                "type": str
            }
        },
        {
            "name": "age",
            "kwargs": {
                "help": "Age in years",
                "type": int
            }
        },
    ],
)
def greet_with_positional(args) -> int:
    print(f"Hello, {args.person}! You are {args.age} years old!!!")
    return 0
```

**Usage example:**
```
py -m cli greet Bob 42
```
> Hello, Bob! You are 42 years old!!!


### [Option C] Using Flag Arguments

**Example `commands/greet_with_flags.py`:**
```python
@cli_command(
    name="greet-flags",
    help="Greets a person using flags for name and age.",
    arguments=[
        {
            "flags": ["-p", "--person"],
            "kwargs": {
                "help": "Person's name",
                "type": str,
                "required": True
            }
        },
        {
            "flags": ["-a", "--age"],
            "kwargs": {
                "help": "Age in years",
                "type": int,
                "required": True
            }
        },
        {
            "flags": ["-e", "--excited"],
            "kwargs": {
                "help": "Make it all caps",
                "action": "store_true"
            }
        },
    ],
)
def greet_with_flags(args) -> int:
    message = f"Hello, {args.person}! You are {args.age} years old!!!"
    if args.excited:
        message = message.upper()
    print(message)
    return 0
```

**Usage examples:**
```
py -m cli greet-flags -p Alice -a 30
```
> Hello, Alice! You are 30 years old!!!

```
py -m cli greet-flags --person Bob --age 25 --excited
```
> HELLO, BOB! YOU ARE 25 YEARS OLD!!!
---
<br/>


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
<br/>


## Built-in Commands
  
#### `-h` or `--help` — shows app help with loaded commands:
```
py -m cli -h
```
> output:
```
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

#### `status` — shows app config and the list of loaded commands:
```
py -m cli status
```
> output:
```
{
  "APP_NAME": "cli",
  "APP_VERSION": "0.1.0",
  "DISPLAY_NAME": "Dynamic CLI Application",
  "DESCRIPTION": "A minimal CLI application with dynamically loaded commands.",
  "COMMAND_REGISTRY": [
    "greet",
    "greet-flags",
    "hello"
  ]
}
```

---
<br/>


## App Configuration

`internals/config.py` centralizes the app constants:

```python
APP_NAME = "cli"
APP_VERSION = "0.3.0"
DISPLAY_NAME = "Dynamic CLI Application"
DESCRIPTION = "A minimal CLI application with dynamically loaded commands."
```

---
<br/>


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
<br/>


## License

MIT
