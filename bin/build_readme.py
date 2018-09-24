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

# Markdown star emoji
STAR_CHARACTER = ":star:"

# Recipe files to ignore.
IGNORE_FILES = ["r/TEMPLATE.md"]

# Ordered list of section names.
SECTIONS = collections.OrderedDict(
    [
        ("Poultry", ("chicken", "poultry")),
        ("Beef", ("beef",)),
        ("Ground Beef", ("ground beef",)),
        ("Pork", ("pork",)),
        ("Lamb", ("lamb",)),
        ("Seafood", ("fish", "seafood", "shrimp")),
        ("Soup (Veg)", ("soup",)),
        ("Vegetable", ("vegetable",)),
        ("Side Dish", ("rice", "salad", "side dish")),
        ("Bread", ("bread",)),
        ("Breakfast", ("breakfast",)),
        ("Treats", ("chocolate", "cookie press", "cookies", "dessert")),
        ("Appetizers", ("appetizer",)),
        ("Drinks", ("drink",)),
        ("Other", ())
    ]
)


def write_header(readme, name, level):
    """
    Write a header element.

    The level is '=' or '-'.
    """

    readme.write(f"{name}\n{level * len(name)}\n")


def write_comment(readme, comment):
    """
    Write a comment element.
    """

    readme.write(f"{{% comment %}}\n{comment}\n{{% endcomment %}}\n")


def write_file_header(readme):
    """Write the README.md file header."""

    write_header(readme, "tschutter Culinary Recipes", "=")
    write_comment(
        readme,
        "Links on this page do not work,"
        " use http://tschutter.github.io/recipes/ instead."
    )


def create_keyword_to_section_name():
    """Create a map of keyword to section name."""

    keyword_to_section_name = {}
    for section_name, keywords in SECTIONS.items():
        for keyword in keywords:
            keyword_to_section_name[keyword] = section_name

    return keyword_to_section_name


def list_files(args, root_dir):
    """Return a dictionary of type: [(filename, title)]."""

    # Create a map of keyword to section name.
    keyword_to_section_name = create_keyword_to_section_name()

    # Initialize the ordered dictionary of sections.
    recipies = collections.OrderedDict()
    for section_name in SECTIONS:
        recipies[section_name] = []

    # Loop through all recipes on disk.
    os.chdir(root_dir)
    for filename in sorted(glob.glob(os.path.join("r", "*.md"))):
        if filename in IGNORE_FILES:
            continue

        # Collect metadata from recipe.
        title = "unknown"
        keywords = []
        ratings = ""
        with open(filename) as recipe:
            title = recipe.readline().strip()
            for line in recipe.readlines():
                if line.startswith("- keywords:"):
                    keywords = [
                        keyword.strip() for keyword in line[12:].split(",")
                    ]
                elif line.startswith("- ratings:"):
                    if re.search(r"[0-9]", line):
                        ratings = line[11:].strip()

        # Determine which section this recipe should be in.
        section_name = "Other"
        for keyword in keywords:
            if keyword in keyword_to_section_name:
                section_name = keyword_to_section_name[keyword]
                break
        if section_name == "Other" and args.print_other:
            print(f"{filename:45}: {keywords}")

        # Add the recipe to the section.
        recipe = (title, filename, keywords, ratings)
        recipies[section_name].append(recipe)

    # Sort the recipes in each section by title.
    for sectionname in recipies.keys():
        recipies[sectionname] = sorted(recipies[sectionname])

    return recipies


def write_file_body(readme, sections):
    """Write the README.md body."""

    # Table of contents.
    readme.write("\n")
    for name in sections.keys():
        readme.write(f"- [{name}](#{name.lower().replace(' ', '-')})\n")

    for section_name, recipes in sections.items():
        readme.write("\n")
        write_header(readme, section_name, "-")
        for recipe in recipes:
            title, filename, keywords, ratings = recipe
            item = f"- [{title}]({filename[:-3]})"
            if "favorite" in keywords:
                item += " " + STAR_CHARACTER
            if ratings:
                item += f" ({ratings})"
            readme.write(item + "\n")


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
            - All recipes are ASCII text files.
            - 100 years from now anyone will be able to read them.
            - No funky abbreviations.  Tablespoons, not tbsp.
            - Flour is measured by mass instead of volume when baking.
            - Ingredients are ordered to make prep and cleanup easier.
            - Ingredients are logically grouped.
            - This file was created by [build_readme.py](bin/build_readme.py)
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
