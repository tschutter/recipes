#!/usr/bin/env python3

"""
Builds an README.md for the recipes repository.

Should be run when:
- new recipe files are added or renamed
- keywords are changed
- ratings are changed
"""

# pylint: disable=invalid-name

from __future__ import print_function
import collections
import glob
import argparse
import os
import re
import textwrap

IGNORE_TXT_FILES = ["TEMPLATE.txt"]

SECTION_NAMES = [
    "Poultry",
    "Beef",
    "Ground Beef",
    "Pork",
    "Lamb",
    "Seafood",
    "Soup (Veg)",
    "Vegetable",
    "Side Dish",
    "Bread",
    "Breakfast",
    "Treats",
    "Appetizers",
    "Drinks",
    "Other"
]

KEYWORD_TO_SECTION = {
    "appetizer": "Appetizers",
    "beef": "Beef",
    "bread": "Bread",
    "breakfast": "Breakfast",
    "chicken": "Poultry",
    "chocolate": "Treats",
    "cookie press": "Treats",
    "cookies": "Treats",
    "dessert": "Treats",
    "drink": "Drinks",
    "fish": "Seafood",
    "ground beef": "Ground Beef",
    "lamb": "Lamb",
    "pork": "Pork",
    "poultry": "Poultry",
    "rice": "Side Dish",
    "salad": "Side Dish",
    "seafood": "Seafood",
    "shrimp": "Seafood",
    "side dish": "Side Dish",
    "soup": "Soup (Veg)",
    "vegetable": "Vegetable"
}


def write_header(readme, name, level):
    """
    Write a header element.

    The level is '=' or '-'.
    """

    readme.write(f"{name}\n{level * len(name)}\n")


def write_file_header(readme):
    """Write the README.md file header."""

    write_header(readme, "Culinary Recipes", "=")


def list_files(args, root_dir):
    """Return a dictionary of type: [(filename, title)]."""

    # Initialize the ordered dictionary of sections.
    sections = collections.OrderedDict()
    for section_name in SECTION_NAMES:
        sections[section_name] = []

    # Loop through all recipes on disk.
    os.chdir(root_dir)
    for filename in sorted(glob.glob(os.path.join("r", "*.txt"))):
        if filename in IGNORE_TXT_FILES:
            continue

        # Collect metadata from recipe.
        title = "unknown"
        keywords = []
        ratings = ""
        with open(filename) as recipe:
            title = recipe.readline().strip()
            for line in recipe.readlines():
                if line.startswith("keywords:"):
                    keywords = [
                        keyword.strip() for keyword in line[10:].split(",")
                    ]
                elif line.startswith("ratings:"):
                    if re.search(r"[0-9]", line):
                        ratings = line[9:].strip()

        # Determine which section this recipe should be in.
        section_name = "Other"
        for keyword in keywords:
            if keyword in KEYWORD_TO_SECTION:
                section_name = KEYWORD_TO_SECTION[keyword]
                break
        if section_name == "Other" and args.print_other:
            print("%45s: %s" % (filename, keywords))

        # Add the recipe to the section.
        recipe = (title, filename, ratings)
        sections[section_name].append(recipe)

    # Sort the recipes in each section by title.
    for sectionname in sections.keys():
        sections[sectionname] = sorted(sections[sectionname])

    return sections


def write_file_body(readme, sections):
    """Write the README.md body."""

    # Table of contents.
    readme.write("\n")
    write_header(readme, "Table of Contents", "-")
    for name in sections.keys():
        readme.write(f"- [{name}](#{name.lower().replace(' ', '-')})\n")

    for section_name, recipes in sections.items():
        readme.write("\n")
        write_header(readme, section_name, "-")
        for recipe in recipes:
            title, filename, ratings = recipe
            if ratings:
                ratings = f" ({ratings})"
            readme.write(f"- [{title}]({filename}?raw=true){ratings}\n")


def write_file_footer(readme):
    """Write the README.md file footer."""

    readme.write(
        textwrap.dedent(
            """
            Usage
            -----
            ```shell
            git clone git://github.com/tschutter/recipes.git
            ```

            Design
            ------
            All recipes are ASCII text files.
            100 years from now anyone will be able to read them.
            """
        )
    )


def main():
    """Main."""
    arg_parser = argparse.ArgumentParser(
        description="Create README.md for recipes."
    )
    arg_parser.add_argument(
        "--print-other",
        action="store_true",
        default=False,
        help="print keywords for recipes in Other section"
    )
    args = arg_parser.parse_args()

    # Locate the root directory.
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # Do the work.
    sections = list_files(args, root_dir)
    with open(os.path.join(root_dir, "README.md"), "w") as readme:
        write_file_header(readme)
        write_file_body(readme, sections)
        write_file_footer(readme)

    return 0


if __name__ == "__main__":
    main()
