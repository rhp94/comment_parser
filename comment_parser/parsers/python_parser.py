#!/usr/bin/python
"""This module provides methods
for parsing comments from Python."""

from comment_parser.parsers import common as common
import tokenize
import ast
import io
import re


def parse_single_line_comments(file_contents, comments, start_lines_dict):
    """ Extracts single line comments and adds them to a list.
        Also stores line numbers on which the comments occur.

        Args:
            file_contents: (str) from which to extract comments
            comments: list of comments. Each entry is a Comment class object
            start_lines_dict:
                key - line number on which a comment occurs
                value - index of comment
    """
    buf = io.StringIO(file_contents)
    comment_index = len(comments)
    for token_type, token, start, end, line in tokenize.generate_tokens(buf.readline):
        if token_type == tokenize.COMMENT:
            token = token.replace('#', '', 1)
            line_number = start[0]

            # Create comment using token text and line number
            comment = common.Comment(text=token, start_line=line_number, end_line=line_number)
            comments.append(comment)

            # Add key-value pair of line number and comment index
            start_lines_dict[line_number] = comment_index
            comment_index += 1


def parse_multi_line_comments(file_contents, comments, start_lines_dict, end_lines_dict):
    """ Extracts multi line comments and adds them to a list.
        Also stores start and end line numbers of each comment.

        Args:
            file_contents: (str) from which to extract comments
            comments: list of comments. Each entry is a Comment class object
            start_lines_dict:
                key - starting line number of comment
                value - index of comment
            end_lines_dict:
                key - ending line number of comment
                value - index of comment
    """

    # Store line numbers
    end = '.*\n'
    line = []
    for match in re.finditer(end, file_contents):
        line.append(match.end())

    # Match triple double quoted strings spanning multiple lines
    pattern = re.compile('^[ \t]*("{3}([^"]|\n)*"{3})$', re.MULTILINE | re.DOTALL)
    comment_index = len(comments)
    for match in re.finditer(pattern, file_contents):

        # Store text and start and end line numbers of match
        start_line = next(i for i in range(len(line)) if line[i] > match.start(1)) + 1
        match = match.group(1)
        end_line = start_line + match.count("\n")
        match = match.replace('"""', '')

        # Create a comment using matching group and line numbers
        comment = common.Comment(text=match, start_line=start_line, end_line=end_line, multiline=True)
        comments.append(comment)

        # Add key-value pair of line number and comment index
        start_lines_dict[start_line] = comment_index
        end_lines_dict[end_line] = comment_index
        comment_index += 1


def extract_comments(filename):
    """Extracts a list of comments from the given Python source file.

        Comments are represented with the Comment class found in the common module.
        Python comments come in two forms, single and multi-line comments.
            - Single-line comments begin with '#' and continue to the end of line.
            - Multi-line comments are enclosed within triple double quotes as docstrings and can span
                multiple lines of code.

        Note that this doesn't take language-specific preprocessor directives into
        consideration.

        Args:
            filename: String name of the file to extract comments from.
        Returns:
            Python list of common.Comment in the order that they appear in the file.
        Raises:
            common.FileError: File was unable to be open or read.
        """
    try:
        comments = []
        start_lines_dict = {}
        end_lines_dict = {}
        with open(filename, 'r') as source_file:
            file_contents = source_file.read()
            parse_single_line_comments(file_contents, comments, start_lines_dict)
            parse_multi_line_comments(file_contents, comments, start_lines_dict, end_lines_dict)

            source_file.close()
        return comments
    except OSError as exception:
        raise common.FileError(str(exception))
