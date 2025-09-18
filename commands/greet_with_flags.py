from internals.decorator import cli_command


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
