from internals.decorator import cli_command


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
