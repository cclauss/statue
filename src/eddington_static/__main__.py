"""Main of Eddington Static."""
from argparse import ArgumentParser
from pathlib import Path

from eddington_static import DESCRIPTION
from eddington_static.command import Command

parser = ArgumentParser(description=DESCRIPTION)
parser.add_argument("input", nargs="+", type=Path, help="Input path to analyze")
parser.add_argument(
    "--format", action="store_true", default=False, help="Format code when possible"
)
parser.add_argument(
    "--silent", action="store_true", default=False, help="Runs silently"
)
RESOURCES_PATH = Path(__file__).parent.parent / "resources"


def print_title(title):
    """
    Print a title with a title line under it.

    :param title: The title to print
    """
    print(title.title())
    print("=" * len(title))


def run(*commands, is_format=False, is_silent=False):
    """
    Run all static analysis commands.

    :param commands: List of commands to run
    :param is_format: Boolean. Indicates if formatting is required.
    :param is_silent: Boolean. Indicates to run the command without capturing
     output.
    :return: List of failed command names.
    """
    failed_commands = []
    for command in commands:
        if not is_silent:
            print_title(command.name)
        return_code = command.execute(is_format=is_format, is_silent=is_silent)
        if return_code != 0:
            failed_commands.append(command.name)
    return failed_commands


def main():
    """A main function of Eddington-Static."""
    args = parser.parse_args()
    input_path = args.input
    if not isinstance(input_path, list):
        input_path = [input_path]
    input_path = [str(path) for path in input_path]

    silent = args.silent
    if not silent:
        print(f"Evaluating the following files: {', '.join(input_path)}")
    failed_commands = run(
        Command(name="black", args=input_path, check_arg="--check"),
        Command(
            name="flake8", args=[*input_path, f"--config={RESOURCES_PATH / '.flake8'}"]
        ),
        Command(
            name="isort",
            args=[
                *input_path,
                "--recursive",
                f"--settings-path={RESOURCES_PATH / '.isort.cfg'}",
            ],
            check_arg="--check-only",
        ),
        Command(name="pylint", args=input_path),
        Command(
            name="pydocstyle",
            args=[*input_path, f"--config={RESOURCES_PATH / '.pydocstyle.ini'}"],
        ),
        is_format=args.format,
        is_silent=silent,
    )
    print_title("Summary")
    if len(failed_commands) == 0:
        print("Static code analysis successful")
    else:
        print(f"The following commands failed: {', '.join(failed_commands)}")


if __name__ == "__main__":
    main()
