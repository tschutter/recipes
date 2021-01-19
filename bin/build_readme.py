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
import argparse
import collections
import glob
#import json
import os
import re
import textwrap

# Recipe files to ignore.
IGNORE_FILES = ["r/TEMPLATE.md"]

# Ordered list of section names.
SECTIONS = collections.OrderedDict(
    [
        ("Poultry :chicken:", ("chicken", "poultry")),
        ("Beef :cow2:", ("beef",)),
        ("Ground Beef :cow2:", ("ground beef",)),
        ("Pork :pig2:", ("pork",)),
        ("Lamb :sheep:", ("lamb",)),
        ("Seafood :fish:", ("fish", "seafood", "shrimp")),
        ("Soup and Stew :stew:", ("soup", "stew")),
        ("Vegetable :herb:", ("casserole", "vegetarian")),
        ("Side Dish", ("rice", "salad", "side dish")),
        ("Salad :rabbit:", ("salad",)),
        ("Bread :bread:", ("bread",)),
        ("Breakfast", ("breakfast",)),
        ("Treats :cake:", ("chocolate", "cookie press", "cookies", "dessert")),
        ("Appetizers", ("appetizer",)),
        ("Drinks :tropical_drink:", ("drink",)),
        ("Other", ())
    ]
)

# Keyword to emoji map.
# See https://www.webfx.com/tools/emoji-cheat-sheet/
EMOJIS = {
    "beef": ":cow2:",
    "chicken": ":chicken:",
    "favorite": ":star:",
    "fish": ":fish:",
    "ground beef": ":cow2:",
    "lamb": ":sheep:",
    "pork": ":pig2:",
    "poultry": ":chicken:",
    "salad": ":rabbit:",
    "seafood": ":fish:",
    "shrimp": ":fish:",
    "southwest": ":cactus:",
    "vegetarian": ":herb:"
}

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

    # Debug print to diagnose section problems.
    # print(json.dumps(keyword_to_section_name, indent=2))

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

        # Determine which section this recipe should be in.  The first
        # keyword in the recipe that matches determines the section.
        section_name = "Other"
        emoji_keywords = set(keywords)
        for keyword in keywords:
            if keyword in keyword_to_section_name:
                section_name = keyword_to_section_name[keyword]
                emoji_keywords.remove(keyword)
                break
        if section_name == "Other" and args.print_other:
            print(f"{filename:45}: {keywords}")

        # Build list of applicable emojis.  Order is determined by
        # order of keys in EMOJIS.
        emojis = []
        for emoji in EMOJIS:
            if emoji in emoji_keywords:
                emojis.append(EMOJIS[emoji])

        # Add the recipe to the section.
        recipe = (title, filename, keywords, emojis, ratings)
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
        target = name.lower().replace(" ", "-").replace(":", "")
        readme.write(f"- [{name}](#{target})\n")

    for section_name, recipes in sections.items():
        readme.write("\n")
        write_header(readme, section_name, "-")
        for recipe in recipes:
            title, filename, _keywords, emojis, ratings = recipe
            item = f"- [{title}]({filename[:-3]})"
            if emojis:
                item += " " + " ".join(emojis)
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
            bin/build_readme.py
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

            Keywords
            --------
            - The first keyword controls the section.
            - If the only non-vegetarian item is chicken broth, the
              recipe is still marked as vegetarian assuming that
              vegetable broth can be substituted for chicken broth.
            - Emojis for the primary keyword are not displayed in the
              recipe list; if the recipe is in the pork section, it is
              not displayed with a pig emoji.

            See Also
            --------
            - [kschutter Culinary Recipes](http://github.com/kschutter/recipes)
            - [sschutter Culinary Recipes](https://github.com/sschutter/recipes/tree/master/r)
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
