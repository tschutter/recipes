#!/usr/bin/env python3

"""
Convert .txt recipe files to .md files.

Adjacent lists must be separated by <!-- --> comment lines otherwise
most Markdown parsers will combine them into a single list.
"""

import argparse
import os
import re

RE_INGREDIENT = re.compile(
    r"^([1-9]|\?|olive oil|canola oil|lemon|salt|seasoning salt|pepper|"
    "juice |coarse salt|pinch|splash of|dash|zest|grated|freshly|"
    "cayenne|hot pepper|grated parmesan|leaves|cornstarch)"
)
RE_METADATA = re.compile("^(keywords|notes|ratings|servings|source|time|todo):")


def is_ingredient(line):
    """Determine if the line is an ingredient line."""
    return RE_INGREDIENT.search(line)


def is_metadata(line):
    """Determine if the line is a metadata line."""
    return RE_METADATA.search(line)


def convert(input_lines):
    """Convert input_lines to output_lines."""
    # pylint: disable=too-many-branches

    output_lines = []
    state = "title"
    n_instructions = 0

    for lineno, line in enumerate(input_lines):
        if state == "title":
            if line == "\n":
                output_lines.append(line)
                state = "ingredients"
                continue
            else:
                output_lines.append(line)
                output_lines.append("-" * (len(line) - 1) + "\n")
                continue

        if state == "ingredients":
            if line == "\n":
                if lineno + 1 >= len(input_lines):
                    next_line = "EOF"
                else:
                    next_line = input_lines[lineno + 1]
                if is_ingredient(next_line):
                    output_lines.append("<!-- -->\n")
                else:
                    output_lines.append("\n")
                continue
            elif not is_ingredient(line):
                state = "instructions"
            else:
                output_lines.append("- " + line)
                continue

        if state == "instructions":
            if is_ingredient(line) and n_instructions < 5:
                output_lines.append("FIXME: " + line)
                continue
            if is_metadata(line):
                state = "metadata"
            else:
                output_lines.append(line)
                n_instructions += 1
                continue

        if state == "metadata":
            if is_metadata(line):
                output_lines.append("- " + line)
            else:
                output_lines.append("FIXME: " + line)

    return output_lines


def convert_file(input_filename):
    """Convert a single file."""

    root, _ext = os.path.splitext(input_filename)
    output_filename = root + ".md"

    input_lines = open(input_filename).readlines()
    output_lines = convert(input_lines)
    with open(output_filename, "w") as output_file:
        for line in output_lines:
            output_file.write(line)


def main():
    """Main."""
    arg_parser = argparse.ArgumentParser(
        description="Convert .txt recipe files to .md files."
    )
    arg_parser.add_argument(
        "file_or_dirs",
        metavar="file-or-dir",
        nargs="*",
        help="file or directory to convert"
    )
    args = arg_parser.parse_args()

    if not args.file_or_dirs:
        # Locate the default directory.
        root_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..")
        )
        args.file_or_dirs = [os.path.join(root_dir, "r")]

    # Do the work.
    for file_or_dir in args.file_or_dirs:
        if not os.path.exists(file_or_dir):
            arg_parser.error(f"{file_or_dir} does not exist")
        if os.path.isdir(file_or_dir):
            for filename in os.listdir(file_or_dir):
                if not filename.endswith(".txt"):
                    continue
                input_filename = os.path.join(file_or_dir, filename)
                if not os.path.isfile(input_filename):
                    continue
                convert_file(input_filename)
        else:
            convert_file(file_or_dir)

    return 0


if __name__ == "__main__":
    main()
