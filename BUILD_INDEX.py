#!/usr/bin/env python

"""
Builds an index.html.
"""

import collections
import glob
import optparse
import re

SECTION_NAMES = [
    "Poultry",
    "Beef",
    "Pork",
    "Seafood",
    "Soup",
    "Vegetable",
    "Side Dish",
    "Bread",
    "Breakfast",
    "Treats",
    "Drinks",
    "Other"
]

KEYWORD_TO_SECTION = {
    "chicken": "Poultry",
    "poultry": "Poultry",
    "beef": "Beef",
    "pork": "Pork",
    "fish": "Seafood",
    "shrimp": "Seafood",
    "soup": "Soup",
    "vegetable": "Vegetable",
    "rice": "Vegetable",
    "salad": "Vegetable",
    "side dish": "Side Dish",
    "bread": "Bread",
    "breakfast": "Breakfast",
    "cookies": "Treats",
    "chocolate": "Treats",
    "cookie press": "Treats",
    "dessert": "Treats",
    "drink": "Drinks"
}

def list_files(options):
    """Return a dictionary of type: [(filename, title)]."""

    # Initialize the ordered dictionary of sections.
    sections = collections.OrderedDict()
    for section_name in SECTION_NAMES:
        sections[section_name] = []

    # Loop through all recipes on disk.
    for filename in sorted(glob.glob("*.txt")):
        if filename == "TEMPLATE.txt":
            continue

        # Collect metadata from recipe.
        title = "unknown"
        keywords = []
        ratings = ""
        with open(filename) as recipe:
            title = recipe.readline().strip()
            keywords = ""
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
        if section_name == "Other" and options.print_other:
            print "%45s: %s" % (filename, keywords)

        # Add the recipe to the section.
        recipe = (title, filename, ratings)
        sections[section_name].append(recipe)

    # Sort the recipes in each section by title.
    for sectionname in sections.keys():
        sections[sectionname] = sorted(sections[sectionname])

    return sections


def build_index(index, sections):
    """Create index.html."""
    index.write("<!doctype html public \"-//W3C//DTD HTML 3.2 Final//EN\">\n")
    index.write("<html>\n")
    index.write("<head>\n")
    index.write("<title>Recipes</title>\n")
    index.write("</head>\n")
    index.write("<h1 align=\"center\">Recipes</h1>\n")
    for section_name in sections.keys():
        index.write("<a href=\"#%s\">%s</a>\n" % (section_name, section_name))
    for section_name, recipes in sections.items():
        index.write("<h2><a id=\"%s\">%s</h2>" % (section_name, section_name))
        index.write("<ul>\n")
        for recipe in recipes:
            title, filename, ratings = recipe
            if len(ratings) > 0:
                ratings = " (%s)" % ratings
            index.write(
                "  <li><a href=\"%s\">%s</a>%s</li>\n" % (
                    filename,
                    title,
                    ratings
                )
            )
        index.write("</ul>\n")
    index.write("</body>\n")
    index.write("</html>\n")


def main():
    """main"""
    option_parser = optparse.OptionParser(
        usage="usage: %prog [options]\n" +
        "  Create index.html."
    )
    option_parser.add_option(
        "--print-other",
        action="store_true",
        default=False,
        help="print keywords for recipes in Other section"
    )

    # Parse command line arguments.
    (options, args) = option_parser.parse_args()
    if len(args) > 0:
        option_parser.error("invalid argument")

    # Do the work.
    sections = list_files(options)
    with open("index.html", "w") as index:
        build_index(index, sections)

    return 0

if __name__ == "__main__":
    main()
