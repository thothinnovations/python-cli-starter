from internals.decorator import cli_command


@cli_command(
    name="hello",
    help="Prints a hello world message."
)
def hello_world(_) -> int:
    print("Hello World!!!")
    return 0
