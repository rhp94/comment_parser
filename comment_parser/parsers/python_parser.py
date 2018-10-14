#!/usr/bin/python
"""This module provides methods for parsing comments from Python."""

from comment_parser.parsers import common as common


def extract_comments(filename):
    try:
        with open(filename, 'r') as source_file:
            state = 0
            current_comment = ''
            comments = []
            line_counter = 1
            comment_start = 1
            while True:
                char = source_file.read(1)
                if not char:
                    if state == 1:
                        # Was in single line comment. Create comment.
                        comment = common.Comment(current_comment, line_counter)
                        comments.append(comment)
                    return comments
                if state == 0:
                    # Beginning of new line
                    # Check if new line starts with a comment
                    if char == '#':
                        state = 1
                    elif char == '"':
                        state = 2
                    elif char == "'":
                        state = 3
                    else:
                        state = 4
                elif state == 1:
                    # Found a single line comment. Create comment
                    if char == '\n':
                        comment = common.Comment(current_comment, line_counter)
                        comments.append(comment)
                        current_comment = ''
                    else:
                        current_comment += char
                elif state == 4:
                    # Parse lines that don't begin with a '#' or quotes
                    # Wait for '#' to occur in line
                    if char == '#':
                        state = 1
                    elif char == '"' or char == "'":
                        state = 5
                elif state == 5:
                    # In string literal, expect literal end or escape char.
                    if char == '"' or char == "'":
                        state = 4
                    elif char == '\\':
                        state = 6
                elif state is 6:
                    # In string literal, escaping current char.
                    state = 5
                if char == '\n':
                    # End of line
                    line_counter += 1
                    state = 0
    except OSError as exception:
        raise common.FileError(str(exception))
