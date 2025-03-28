#!/usr/bin/env python3
"""Enforce ordering of the dependencies.

We generate the dependency order with snakefood.
In this script, we ensure that the expected set of dependencies aren't violated.
"""

__copyright__ = "Copyright (C) 2014-2017, 2024  Martin Blais"
__license__ = "GNU GPLv2"

import argparse
import logging
import re
import sys
from os import path

RULES = [
    ("ALLOW", "beancount/.*_test$", "beancount/loader"),
    ("ALLOW", "beancount/.*_test$", "beancount/utils"),
    ("ALLOW", "beancount/loader", "beancount/(core|utils|parser|ops)"),
    ("ALLOW", "beancount/core", "beancount/(core|utils)"),
    ("ALLOW", "beancount/core/.*_test", "beancount/parser"),
    ("DISALLOW", "beancount/core/(?!interpolate)", "beancount/core/interpolate"),
    ("ALLOW", "beancount/parser", "beancount/(utils|core|parser)"),
    ("ALLOW", "beancount/ops", "beancount/(core|utils|ops)"),
    ("ALLOW", "beancount/ops/summarize", "beancount/parser/options"),
    ("ALLOW", "beancount/ops/.*_test", "beancount/parser"),
    ("ALLOW", "beancount/plugins", "beancount/(core|parser|ops|plugins)"),
    ("ALLOW", "beancount/plugins/book_conversions", "beancount/(loader|reports)"),
    ("ALLOW", "beancount/plugins/merge_meta", "beancount/(loader)"),
    ("ALLOW", "beancount/reports", "beancount/(core|utils|ops|parser|reports|loader)"),
    ("ALLOW", "beancount/reports/convert_reports_test", "beancount/scripts/example"),
    ("ALLOW", "beancount/query", "beancount/(core|utils|ops|parser|query)"),
    (
        "ALLOW",
        "beancount/scripts",
        "beancount/(core|utils|parser|web|ops|loader$|reports|query|scripts)",
    ),
    ("ALLOW", "beancount/web", "beancount/(core|utils|parser|ops|loader$|reports|web)"),
    (
        "ALLOW",
        "beancount/projects",
        "beancount/(core|utils|parser|web|ops|loader$|reports|scripts)",
    ),
    ("ALLOW", "beancount/projects/.*_test", "beancount/(projects)"),
    ("ALLOW", "beancount/docs/.*_test", "beancount/docs"),
    ("ALLOW", "beancount/docs", "beancount/(docs|parser|utils)"),
    ("ALLOW", "beancount/prices", "beancount/(core|ops|prices|loader|parser|utils)"),
    ("ALLOW", "beancount/ingest", "beancount/(utils|core|parser|ingest)"),
]


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)-8s: %(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dependencies", help="The dependencies file generated by snakefood")
    opts = parser.parse_args()

    root = path.join(
        path.dirname(path.dirname(path.join(path.abspath(__file__)))), "src", "python"
    )

    has_errors = False
    for line in open(opts.dependencies):
        ((from_dir, from_file), (to_dir, to_file)) = eval(line)
        if to_dir is None:
            continue
        if from_dir != root or to_dir != root:
            continue
        from_file = from_file.replace(".py", "")
        to_file = to_file.replace(".py", "")

        # Find all the rules that match the source file.
        matching_rules = [rule for rule in RULES if re.match(rule[1], from_file)]

        # If any disallowing rules match, disallow.
        allow_rules = [
            rule
            for rule in matching_rules
            if rule[0] == "ALLOW" and re.match(rule[2], to_file)
        ]

        # If none of the allowing rules match, disallow.
        disallow_rules = [
            rule
            for rule in matching_rules
            if rule[0] == "DISALLOW" and re.match(rule[2], to_file)
        ]

        # At least one of the allowing rules must match and none of the
        # disallowing rules may match.
        if disallow_rules or not allow_rules:
            # Failed!
            logging.error("Invalid dependency:  {:40} -> {:40}".format(from_file, to_file))
            has_errors = True

    return 1 if has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
